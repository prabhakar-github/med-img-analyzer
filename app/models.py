from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Client(db.Model):
    """Client (Hospital/Diagnostic Center/Clinic) model"""
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(
        db.Enum('HOSPITAL', 'DIAGNOSTIC_CENTER', 'CLINIC', name='client_type'),
        nullable=False
    )
    license_number = db.Column(db.String(100), nullable=False, unique=True)
    address = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=True)
    
    # Relationships
    operators = db.relationship('Operator', backref='client', lazy=True)
    cases = db.relationship('Case', backref='client', lazy=True)
    
    def __repr__(self):
        return f'<Client {self.name} ({self.type})>'


class Operator(UserMixin, db.Model):
    """Operator (User) model for authentication"""
    __tablename__ = 'operators'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    role = db.Column(
        db.Enum('OPERATOR', 'FACILITY_ADMIN', 'SYSTEM_SUPER_ADMIN', name='operator_role'),
        nullable=False, default='OPERATOR'
    )
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=True)
    
    # Relationships
    cases = db.relationship('Case', backref='operator', lazy=True)
    login_audit_logs = db.relationship('LoginAuditLog', backref='operator', lazy=True)
    data_access_audit_logs = db.relationship('DataAccessAuditLog', backref='operator', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Operator {self.username} ({self.role})>'


class Case(db.Model):
    """Case model representing a patient imaging session"""
    __tablename__ = 'cases'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    operator_id = db.Column(db.Integer, db.ForeignKey('operators.id'), nullable=False)
    patient_reference_id = db.Column(db.String(100), nullable=False)
    modality = db.Column(
        db.Enum('XRAY', 'MRI', 'CT', 'ULTRASOUND', 'MAMMOGRAPHY', name='case_modality'),
        nullable=False
    )
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    
    # Relationships
    raw_image_uploads = db.relationship('RawImageUpload', backref='case', lazy=True)
    
    def __repr__(self):
        return f'<Case {self.id} - {self.modality}>'


class RawImageUpload(db.Model):
    """Raw DICOM image upload metadata"""
    __tablename__ = 'raw_image_uploads'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    file_name_original = db.Column(db.String(255), nullable=False)
    storage_path = db.Column(db.String(2048), nullable=False)
    file_size_bytes = db.Column(db.BigInteger, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    checksum_sha256 = db.Column(db.String(64), nullable=False)
    uploaded_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RawImageUpload {self.file_name_original}>'


class ProcessedImage(db.Model):
    """Processed image metadata (PNG/JPEG conversions)"""
    __tablename__ = 'processed_images'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    raw_image_id = db.Column(db.Integer, db.ForeignKey('raw_image_uploads.id'), nullable=False)
    file_name_original = db.Column(db.String(255), nullable=False)
    storage_path = db.Column(db.String(2048), nullable=False)
    file_size_bytes = db.Column(db.BigInteger, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    processing_type = db.Column(db.String(50), nullable=False)  # e.g., 'preview', 'normalized', 'resized'
    uploaded_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    
    # Relationship
    raw_image = db.relationship('RawImageUpload', backref='processed_images')
    
    def __repr__(self):
        return f'<ProcessedImage {self.file_name_original} ({self.processing_type})>'


class LoginAuditLog(db.Model):
    """Login authentication audit log"""
    __tablename__ = 'login_audit_logs'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('operators.id'), nullable=True)
    attempted_username = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.String(512), nullable=True)
    status = db.Column(
        db.Enum('SUCCESS', 'FAILED_PASSWORD', 'ACCOUNT_LOCKED', name='login_status'),
        nullable=False
    )
    timestamp = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<LoginAuditLog {self.attempted_username} - {self.status}>'


class DataAccessAuditLog(db.Model):
    """Data access audit log for compliance"""
    __tablename__ = 'data_access_audit_logs'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('operators.id'), nullable=False)
    action = db.Column(
        db.Enum('UPLOAD_IMAGE', 'VIEW_IMAGE', 'DELETE_RECORD', 'EXPORT_METADATA', name='data_action'),
        nullable=False
    )
    target_table = db.Column(db.String(100), nullable=False)
    target_record_id = db.Column(db.Integer, nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DataAccessAuditLog {self.action} on {self.target_table}>'
