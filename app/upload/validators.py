import pydicom
from pydicom.errors import InvalidDicomError

from app.config import settings


class DICOMValidationError(Exception):
    """Custom exception for DICOM validation errors"""
    pass


def validate_file_extension(filename):
    """
    Validate file extension is .dcm
    
    Args:
        filename: Name of the file to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not filename:
        return False
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS


def validate_file_size(file_size):
    """
    Validate file size is within limits
    
    Args:
        file_size: Size of the file in bytes
        
    Returns:
        bool: True if valid, False otherwise
    """
    max_size = settings.MAX_CONTENT_LENGTH
    return file_size <= max_size


def validate_dicom_format(file_data):
    """
    Validate that file data is a valid DICOM file
    
    Args:
        file_data: File data as bytes
        
    Returns:
        dict: Extracted DICOM metadata if valid
        
    Raises:
        DICOMValidationError: If file is not a valid DICOM
    """
    try:
        # Read DICOM file from bytes
        dicom_file = pydicom.io.dcmread(pydicom.filebase.DicomBytesIO(file_data))
        
        metadata = {
            'PatientID': None,
            'StudyDate': None,
            'Modality': None,
            'BodyPartExamined': None,
            'StudyDescription': None,
            'SeriesDescription': None,
            'ImagePositionPatient': None,
            'ImageOrientationPatient': None,
            'PixelSpacing': None,
            'Rows': None,
            'Columns': None,
            'BitsAllocated': None,
            'BitsStored': None,
            'HighBit': None,
            'PixelRepresentation': None,
            'SamplesPerPixel': None,
            'PhotometricInterpretation': None
        }
        
        # Extract metadata from DICOM tags
        for tag in metadata.keys():
            if hasattr(dicom_file, tag):
                metadata[tag] = str(getattr(dicom_file, tag))
        
        # Validate required tags
        required_tags = settings.REQUIRED_DICOM_TAGS
        missing_tags = [tag for tag in required_tags if not metadata.get(tag)]
        
        if missing_tags:
            raise DICOMValidationError(
                f"Missing required DICOM tags: {', '.join(missing_tags)}"
            )
        
        # Validate modality is in allowed list
        modality = metadata.get('Modality', '').upper()
        if modality not in settings.ALLOWED_MODALITIES:
            raise DICOMValidationError(
                f"Invalid modality: {modality}. Allowed: {', '.join(settings.ALLOWED_MODALITIES)}"
            )
        
        return metadata
        
    except InvalidDicomError:
        raise DICOMValidationError("File is not a valid DICOM format")
    except Exception as e:
        raise DICOMValidationError(f"Error parsing DICOM file: {str(e)}")


def validate_uploaded_file(filename, file_data):
    """
    Perform comprehensive validation on uploaded file
    
    Args:
        filename: Uploaded file name
        file_data: Uploaded file bytes
        
    Returns:
        tuple: (is_valid, error_message, metadata)
        
    Raises:
        DICOMValidationError: If validation fails
    """
    if not filename or not file_data:
        raise DICOMValidationError("No file provided")
    
    # Validate file extension
    if not validate_file_extension(filename):
        raise DICOMValidationError(
            f"Invalid file extension. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    file_size = len(file_data)
    if not validate_file_size(file_size):
        max_size_mb = settings.MAX_CONTENT_LENGTH / (1024 * 1024)
        raise DICOMValidationError(
            f"File size exceeds maximum limit of {max_size_mb:.0f}MB"
        )
    
    # Validate DICOM format and extract metadata
    metadata = validate_dicom_format(file_data)
    
    return True, None, metadata


def validate_patient_reference_id(patient_id):
    """
    Validate patient reference ID format
    
    Args:
        patient_id: Patient reference ID string
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not patient_id:
        return False
    
    # Basic validation: non-empty, reasonable length
    return len(patient_id.strip()) > 0 and len(patient_id) <= 100


def validate_modality(modality):
    """
    Validate modality is in allowed list
    
    Args:
        modality: Modality string
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not modality:
        return False
    
    return modality.upper() in settings.ALLOWED_MODALITIES
