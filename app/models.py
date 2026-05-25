from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash


class Base(DeclarativeBase):
    pass


class Client(Base):
    """Client (Hospital/Diagnostic Center/Clinic) model"""
    __tablename__ = 'clients'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(Enum('HOSPITAL', 'DIAGNOSTIC_CENTER', 'CLINIC', name='client_type'), nullable=False)
    license_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    operators: Mapped[list['Operator']] = relationship(back_populates='client')
    cases: Mapped[list['Case']] = relationship(back_populates='client')
    
    def __repr__(self):
        return f'<Client {self.name} ({self.type})>'


class Operator(Base):
    """Operator (User) model for authentication"""
    __tablename__ = 'operators'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey('clients.id'), nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[str] = mapped_column(Enum('OPERATOR', 'FACILITY_ADMIN', 'SYSTEM_SUPER_ADMIN', name='operator_role'), nullable=False, default='OPERATOR')
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    client: Mapped[Client] = relationship(back_populates='operators')
    cases: Mapped[list['Case']] = relationship(back_populates='operator')
    login_audit_logs: Mapped[list['LoginAuditLog']] = relationship(back_populates='operator')
    data_access_audit_logs: Mapped[list['DataAccessAuditLog']] = relationship(back_populates='operator')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Operator {self.username} ({self.role})>'


class Case(Base):
    """Case model representing a patient imaging session"""
    __tablename__ = 'cases'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey('clients.id'), nullable=False)
    operator_id: Mapped[int] = mapped_column(Integer, ForeignKey('operators.id'), nullable=False)
    patient_reference_id: Mapped[str] = mapped_column(String(100), nullable=False)
    modality: Mapped[str] = mapped_column(Enum('XRAY', 'MRI', 'CT', 'ULTRASOUND', 'MAMMOGRAPHY', name='case_modality'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    client: Mapped[Client] = relationship(back_populates='cases')
    operator: Mapped[Operator] = relationship(back_populates='cases')
    raw_image_uploads: Mapped[list['RawImageUpload']] = relationship(back_populates='case')
    
    def __repr__(self):
        return f'<Case {self.id} - {self.modality}>'


class RawImageUpload(Base):
    """Raw DICOM image upload metadata"""
    __tablename__ = 'raw_image_uploads'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(Integer, ForeignKey('cases.id'), nullable=False)
    file_name_original: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(2048), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    case: Mapped[Case] = relationship(back_populates='raw_image_uploads')
    processed_images: Mapped[list['ProcessedImage']] = relationship(back_populates='raw_image')
    
    def __repr__(self):
        return f'<RawImageUpload {self.file_name_original}>'


class ProcessedImage(Base):
    """Processed image metadata (PNG/JPEG conversions)"""
    __tablename__ = 'processed_images'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(Integer, ForeignKey('cases.id'), nullable=False)
    raw_image_id: Mapped[int] = mapped_column(Integer, ForeignKey('raw_image_uploads.id'), nullable=False)
    file_name_original: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(2048), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    processing_type: Mapped[str] = mapped_column(String(50), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    raw_image: Mapped[RawImageUpload] = relationship(back_populates='processed_images')
    
    def __repr__(self):
        return f'<ProcessedImage {self.file_name_original} ({self.processing_type})>'


class LoginAuditLog(Base):
    """Login authentication audit log"""
    __tablename__ = 'login_audit_logs'
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    operator_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('operators.id'), nullable=True)
    attempted_username: Mapped[str] = mapped_column(String(100), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(Enum('SUCCESS', 'FAILED_PASSWORD', 'ACCOUNT_LOCKED', name='login_status'), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    operator: Mapped[Operator | None] = relationship(back_populates='login_audit_logs')
    
    def __repr__(self):
        return f'<LoginAuditLog {self.attempted_username} - {self.status}>'


class DataAccessAuditLog(Base):
    """Data access audit log for compliance"""
    __tablename__ = 'data_access_audit_logs'
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    operator_id: Mapped[int] = mapped_column(Integer, ForeignKey('operators.id'), nullable=False)
    action: Mapped[str] = mapped_column(Enum('UPLOAD_IMAGE', 'VIEW_IMAGE', 'DELETE_RECORD', 'EXPORT_METADATA', name='data_action'), nullable=False)
    target_table: Mapped[str] = mapped_column(String(100), nullable=False)
    target_record_id: Mapped[int] = mapped_column(Integer, nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    operator: Mapped[Operator] = relationship(back_populates='data_access_audit_logs')
    
    def __repr__(self):
        return f'<DataAccessAuditLog {self.action} on {self.target_table}>'
