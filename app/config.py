import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    SECRET_KEY = os.getenv('FASTAPI_SECRET_KEY', os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production'))
    DEBUG = os.getenv('FASTAPI_DEBUG', os.getenv('FLASK_DEBUG', 'True')).lower() == 'true'

    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'med_img_analyzer')

    DATABASE_URL = (
        f"mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )

    MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
    MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
    MINIO_SECURE = os.getenv('MINIO_SECURE', 'False').lower() == 'true'
    MINIO_BUCKET_RAW = 'raw-images'
    MINIO_BUCKET_PROCESSED = 'processed-images'

    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 104857600))
    MAX_FILES_PER_UPLOAD = int(os.getenv('MAX_FILES_PER_UPLOAD', 50))
    ALLOWED_EXTENSIONS = {'dcm'}
    REQUIRED_DICOM_TAGS = ['PatientID', 'StudyDate', 'Modality']
    ALLOWED_MODALITIES = ['XRAY', 'MRI', 'CT', 'ULTRASOUND', 'MAMMOGRAPHY']

    SESSION_COOKIE_SECURE = not DEBUG
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'lax'
    PERMANENT_SESSION_LIFETIME = 3600


settings = Settings()
