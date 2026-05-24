from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.datastructures import FileStorage
from datetime import datetime
from app.models import db, Client, Case, RawImageUpload, ProcessedImage, DataAccessAuditLog
from app.upload.forms import UploadForm
from app.upload.validators import (
    validate_uploaded_file, 
    validate_patient_reference_id,
    validate_modality,
    DICOMValidationError
)
from app.upload.processors import DICOMProcessor
from app.storage.minio_client import get_storage

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/dashboard')
@login_required
def dashboard():
    """Upload dashboard for operators"""
    form = UploadForm()
    
    # Populate client dropdown with active clients
    clients = Client.query.filter_by(is_active=True).all()
    form.client_id.choices = [(c.id, f"{c.name} ({c.type})") for c in clients]
    
    return render_template('upload/dashboard.html', form=form)


@upload_bp.route('/upload', methods=['POST'])
@login_required
def upload_files():
    """Handle DICOM file uploads"""
    form = UploadForm()
    
    # Populate client dropdown
    clients = Client.query.filter_by(is_active=True).all()
    form.client_id.choices = [(c.id, f"{c.name} ({c.type})") for c in clients]
    
    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
        return redirect(url_for('upload.dashboard'))
    
    try:
        # Validate form data
        client_id = form.client_id.data
        patient_reference_id = form.patient_reference_id.data.strip()
        modality = form.modality.data
        
        if not validate_patient_reference_id(patient_reference_id):
            flash('Invalid Patient Reference ID', 'danger')
            return redirect(url_for('upload.dashboard'))
        
        if not validate_modality(modality):
            flash('Invalid modality selected', 'danger')
            return redirect(url_for('upload.dashboard'))
        
        # Get uploaded files
        files = request.files.getlist('dicom_files')
        
        if not files or all(f.filename == '' for f in files):
            flash('No files selected for upload', 'danger')
            return redirect(url_for('upload.dashboard'))
        
        # Check file count limit
        max_files = current_app.config['MAX_FILES_PER_UPLOAD']
        valid_files = [f for f in files if f.filename != '']
        
        if len(valid_files) > max_files:
            flash(f'Maximum {max_files} files allowed per upload', 'danger')
            return redirect(url_for('upload.dashboard'))
        
        # Initialize storage
        storage = get_storage()
        storage.ensure_buckets_exist()
        
        # Create new case
        new_case = Case(
            client_id=client_id,
            operator_id=current_user.id,
            patient_reference_id=patient_reference_id,
            modality=modality
        )
        db.session.add(new_case)
        db.session.flush()  # Get case_id before committing
        
        # Process each file
        uploaded_count = 0
        failed_files = []
        
        for file in valid_files:
            try:
                # Validate file
                is_valid, error_msg, metadata = validate_uploaded_file(file)
                if not is_valid:
                    failed_files.append((file.filename, error_msg))
                    continue
                
                # Read file data
                file.seek(0)
                file_data = file.read()
                file_size = len(file_data)
                
                # Upload raw DICOM to MinIO
                storage_path_raw, checksum = storage.upload_raw_image(
                    client_id=client_id,
                    case_id=new_case.id,
                    filename=file.filename,
                    file_data=file_data,
                    file_size=file_size
                )
                
                # Create raw image upload record
                raw_upload = RawImageUpload(
                    case_id=new_case.id,
                    file_name_original=file.filename,
                    storage_path=storage_path_raw,
                    file_size_bytes=file_size,
                    mime_type='application/dicom',
                    checksum_sha256=checksum
                )
                db.session.add(raw_upload)
                db.session.flush()  # Get raw_upload_id
                
                # Process DICOM to generate preview image
                png_bytes, _ = DICOMProcessor.process_dicom_to_preview(
                    file_data, 
                    resize=True, 
                    target_size=(512, 512)
                )
                
                # Upload processed image to MinIO
                preview_filename = file.filename.rsplit('.', 1)[0] + '.png'
                storage_path_processed = storage.upload_processed_image(
                    client_id=client_id,
                    case_id=new_case.id,
                    filename=preview_filename,
                    file_data=png_bytes,
                    file_size=len(png_bytes),
                    mime_type='image/png'
                )
                
                # Create processed image record
                processed_upload = ProcessedImage(
                    case_id=new_case.id,
                    raw_image_id=raw_upload.id,
                    file_name_original=preview_filename,
                    storage_path=storage_path_processed,
                    file_size_bytes=len(png_bytes),
                    mime_type='image/png',
                    processing_type='preview'
                )
                db.session.add(processed_upload)
                
                uploaded_count += 1
                
            except DICOMValidationError as e:
                failed_files.append((file.filename, str(e)))
                current_app.logger.error(f"DICOM validation error for {file.filename}: {e}")
            except Exception as e:
                failed_files.append((file.filename, str(e)))
                current_app.logger.error(f"Error processing {file.filename}: {e}")
        
        # Commit all database changes
        db.session.commit()
        
        # Log audit entry
        audit_log = DataAccessAuditLog(
            operator_id=current_user.id,
            action='UPLOAD_IMAGE',
            target_table='cases',
            target_record_id=new_case.id,
            ip_address=request.remote_addr
        )
        db.session.add(audit_log)
        db.session.commit()
        
        # Show results
        if uploaded_count > 0:
            flash(f'Successfully uploaded {uploaded_count} file(s) for case {new_case.id}', 'success')
        
        if failed_files:
            flash(f'Failed to upload {len(failed_files)} file(s):', 'warning')
            for filename, error in failed_files:
                flash(f'  - {filename}: {error}', 'warning')
        
        return redirect(url_for('upload.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Upload error: {e}")
        flash(f'An error occurred during upload: {str(e)}', 'danger')
        return redirect(url_for('upload.dashboard'))
