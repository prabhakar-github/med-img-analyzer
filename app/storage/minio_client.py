from minio import Minio
from minio.error import S3Error
from flask import current_app
import hashlib
import io


class MinIOStorage:
    """MinIO storage client for managing DICOM image uploads"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize MinIO client with configuration"""
        try:
            self.client = Minio(
                endpoint=current_app.config['MINIO_ENDPOINT'],
                access_key=current_app.config['MINIO_ACCESS_KEY'],
                secret_key=current_app.config['MINIO_SECRET_KEY'],
                secure=current_app.config['MINIO_SECURE']
            )
            current_app.logger.info("MinIO client initialized successfully")
        except Exception as e:
            current_app.logger.error(f"Failed to initialize MinIO client: {e}")
            raise
    
    def ensure_buckets_exist(self):
        """Create buckets if they don't exist"""
        buckets = [
            current_app.config['MINIO_BUCKET_RAW'],
            current_app.config['MINIO_BUCKET_PROCESSED']
        ]
        
        for bucket in buckets:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    current_app.logger.info(f"Created bucket: {bucket}")
                else:
                    current_app.logger.info(f"Bucket already exists: {bucket}")
            except S3Error as e:
                current_app.logger.error(f"Error creating bucket {bucket}: {e}")
                raise
    
    def upload_raw_image(self, client_id, case_id, filename, file_data, file_size):
        """
        Upload raw DICOM file to MinIO
        
        Args:
            client_id: Client ID
            case_id: Case ID
            filename: Original filename
            file_data: File data (bytes)
            file_size: File size in bytes
            
        Returns:
            tuple: (storage_path, checksum_sha256)
        """
        bucket = current_app.config['MINIO_BUCKET_RAW']
        object_name = f"{client_id}/{case_id}/{filename}"
        
        # Calculate SHA256 checksum
        checksum = hashlib.sha256(file_data).hexdigest()
        
        try:
            self.client.put_object(
                bucket_name=bucket,
                object_name=object_name,
                data=io.BytesIO(file_data),
                length=file_size,
                content_type='application/dicom'
            )
            storage_path = f"minio://{bucket}/{object_name}"
            current_app.logger.info(f"Uploaded raw image: {storage_path}")
            return storage_path, checksum
        except S3Error as e:
            current_app.logger.error(f"Error uploading raw image: {e}")
            raise
    
    def upload_processed_image(self, client_id, case_id, filename, file_data, file_size, mime_type):
        """
        Upload processed image (PNG/JPEG) to MinIO
        
        Args:
            client_id: Client ID
            case_id: Case ID
            filename: Original filename (with new extension)
            file_data: File data (bytes)
            file_size: File size in bytes
            mime_type: MIME type (image/png or image/jpeg)
            
        Returns:
            str: storage_path
        """
        bucket = current_app.config['MINIO_BUCKET_PROCESSED']
        object_name = f"{client_id}/{case_id}/{filename}"
        
        try:
            self.client.put_object(
                bucket_name=bucket,
                object_name=object_name,
                data=io.BytesIO(file_data),
                length=file_size,
                content_type=mime_type
            )
            storage_path = f"minio://{bucket}/{object_name}"
            current_app.logger.info(f"Uploaded processed image: {storage_path}")
            return storage_path
        except S3Error as e:
            current_app.logger.error(f"Error uploading processed image: {e}")
            raise
    
    def download_file(self, bucket, object_name):
        """
        Download file from MinIO
        
        Args:
            bucket: Bucket name
            object_name: Object name (path)
            
        Returns:
            bytes: File data
        """
        try:
            response = self.client.get_object(bucket_name=bucket, object_name=object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            current_app.logger.error(f"Error downloading file: {e}")
            raise
    
    def generate_presigned_url(self, bucket, object_name, expires=3600):
        """
        Generate presigned URL for secure file access
        
        Args:
            bucket: Bucket name
            object_name: Object name (path)
            expires: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            str: Presigned URL
        """
        try:
            url = self.client.presigned_get_object(
                bucket_name=bucket,
                object_name=object_name,
                expires=expires
            )
            return url
        except S3Error as e:
            current_app.logger.error(f"Error generating presigned URL: {e}")
            raise
    
    def delete_file(self, bucket, object_name):
        """
        Delete file from MinIO
        
        Args:
            bucket: Bucket name
            object_name: Object name (path)
        """
        try:
            self.client.remove_object(bucket_name=bucket, object_name=object_name)
            current_app.logger.info(f"Deleted file: {bucket}/{object_name}")
        except S3Error as e:
            current_app.logger.error(f"Error deleting file: {e}")
            raise
    
    def list_files(self, bucket, prefix=None):
        """
        List files in a bucket with optional prefix
        
        Args:
            bucket: Bucket name
            prefix: Path prefix for filtering
            
        Returns:
            list: List of object names
        """
        try:
            objects = self.client.list_objects(bucket_name=bucket, prefix=prefix)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            current_app.logger.error(f"Error listing files: {e}")
            raise


# Global storage instance
storage = None


def get_storage():
    """Get or initialize the MinIO storage instance"""
    global storage
    if storage is None:
        storage = MinIOStorage()
    return storage
