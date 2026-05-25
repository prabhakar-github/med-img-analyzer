import logging

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.routes import get_current_operator
from app.config import settings
from app.database import get_db
from app.models import Client, Case, DataAccessAuditLog, Operator, ProcessedImage, RawImageUpload
from app.storage.minio_client import get_storage
from app.template_helpers import flash, templates
from app.upload.processors import DICOMProcessor
from app.upload.validators import DICOMValidationError, validate_modality, validate_patient_reference_id, validate_uploaded_file


logger = logging.getLogger(__name__)
router = APIRouter()


async def require_operator(request: Request, db: AsyncSession) -> Operator | RedirectResponse:
    operator = await get_current_operator(request, db)
    if not operator:
        flash(request, 'Please log in to access this page.', 'info')
        return RedirectResponse(url=request.url_for('login'), status_code=303)
    return operator


@router.get('/dashboard', name='upload_dashboard')
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await require_operator(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user

    result = await db.execute(select(Client).where(Client.is_active.is_(True)))
    clients = result.scalars().all()
    return templates.TemplateResponse(
        'upload/dashboard.html',
        {
            'request': request,
            'current_user': current_user,
            'clients': clients,
            'modalities': settings.ALLOWED_MODALITIES,
            'errors': {},
        },
    )


@router.post('/upload', name='upload_files')
async def upload_files(
    request: Request,
    client_id: int = Form(...),
    patient_reference_id: str = Form(...),
    modality: str = Form(...),
    dicom_files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    current_user = await require_operator(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user

    try:
        patient_reference_id = patient_reference_id.strip()

        if not validate_patient_reference_id(patient_reference_id):
            flash(request, 'Invalid Patient Reference ID', 'danger')
            return RedirectResponse(url=request.url_for('upload_dashboard'), status_code=303)

        if not validate_modality(modality):
            flash(request, 'Invalid modality selected', 'danger')
            return RedirectResponse(url=request.url_for('upload_dashboard'), status_code=303)

        valid_files = [file for file in dicom_files if file.filename]
        if not valid_files:
            flash(request, 'No files selected for upload', 'danger')
            return RedirectResponse(url=request.url_for('upload_dashboard'), status_code=303)

        if len(valid_files) > settings.MAX_FILES_PER_UPLOAD:
            flash(request, f'Maximum {settings.MAX_FILES_PER_UPLOAD} files allowed per upload', 'danger')
            return RedirectResponse(url=request.url_for('upload_dashboard'), status_code=303)

        storage = get_storage()
        storage.ensure_buckets_exist()

        new_case = Case(
            client_id=client_id,
            operator_id=current_user.id,
            patient_reference_id=patient_reference_id,
            modality=modality,
        )
        db.add(new_case)
        await db.flush()

        uploaded_count = 0
        failed_files = []

        for file in valid_files:
            try:
                file_data = await file.read()
                file_size = len(file_data)
                validate_uploaded_file(file.filename, file_data)

                storage_path_raw, checksum = storage.upload_raw_image(
                    client_id=client_id,
                    case_id=new_case.id,
                    filename=file.filename,
                    file_data=file_data,
                    file_size=file_size,
                )

                raw_upload = RawImageUpload(
                    case_id=new_case.id,
                    file_name_original=file.filename,
                    storage_path=storage_path_raw,
                    file_size_bytes=file_size,
                    mime_type='application/dicom',
                    checksum_sha256=checksum,
                )
                db.add(raw_upload)
                await db.flush()

                png_bytes, _ = DICOMProcessor.process_dicom_to_preview(file_data, resize=True, target_size=(512, 512))

                preview_filename = file.filename.rsplit('.', 1)[0] + '.png'
                storage_path_processed = storage.upload_processed_image(
                    client_id=client_id,
                    case_id=new_case.id,
                    filename=preview_filename,
                    file_data=png_bytes,
                    file_size=len(png_bytes),
                    mime_type='image/png',
                )

                db.add(ProcessedImage(
                    case_id=new_case.id,
                    raw_image_id=raw_upload.id,
                    file_name_original=preview_filename,
                    storage_path=storage_path_processed,
                    file_size_bytes=len(png_bytes),
                    mime_type='image/png',
                    processing_type='preview',
                ))
                uploaded_count += 1

            except DICOMValidationError as exc:
                failed_files.append((file.filename, str(exc)))
                logger.error(f'DICOM validation error for {file.filename}: {exc}')
            except Exception as exc:
                failed_files.append((file.filename, str(exc)))
                logger.error(f'Error processing {file.filename}: {exc}')

        await db.commit()

        db.add(DataAccessAuditLog(
            operator_id=current_user.id,
            action='UPLOAD_IMAGE',
            target_table='cases',
            target_record_id=new_case.id,
            ip_address=request.client.host if request.client else '',
        ))
        await db.commit()

        if uploaded_count > 0:
            flash(request, f'Successfully uploaded {uploaded_count} file(s) for case {new_case.id}', 'success')

        if failed_files:
            flash(request, f'Failed to upload {len(failed_files)} file(s):', 'warning')
            for filename, error in failed_files:
                flash(request, f'  - {filename}: {error}', 'warning')

        return RedirectResponse(url=request.url_for('upload_dashboard'), status_code=303)

    except Exception as exc:
        await db.rollback()
        logger.error(f'Upload error: {exc}')
        flash(request, f'An error occurred during upload: {str(exc)}', 'danger')
        return RedirectResponse(url=request.url_for('upload_dashboard'), status_code=303)
