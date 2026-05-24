import pydicom
import numpy as np
from PIL import Image
import io
from flask import current_app


class DICOMProcessor:
    """Process DICOM files and generate preview images"""
    
    @staticmethod
    def read_dicom(file_data):
        """
        Read DICOM file from bytes
        
        Args:
            file_data: DICOM file data as bytes
            
        Returns:
            pydicom Dataset object
        """
        return pydicom.io.dcmread(pydicom.filebase.DicomBytesIO(file_data))
    
    @staticmethod
    def get_pixel_array(dicom_dataset):
        """
        Extract pixel array from DICOM dataset
        
        Args:
            dicom_dataset: pydicom Dataset object
            
        Returns:
            numpy array of pixel data
        """
        try:
            pixel_array = dicom_dataset.pixel_array
            
            # Apply rescale slope and intercept if present
            if hasattr(dicom_dataset, 'RescaleSlope') and hasattr(dicom_dataset, 'RescaleIntercept'):
                pixel_array = pixel_array * float(dicom_dataset.RescaleSlope) + float(dicom_dataset.RescaleIntercept)
            
            return pixel_array
        except Exception as e:
            current_app.logger.error(f"Error extracting pixel array: {e}")
            raise
    
    @staticmethod
    def normalize_pixel_values(pixel_array):
        """
        Normalize pixel values to 0-255 range for image display
        
        Args:
            pixel_array: numpy array of pixel data
            
        Returns:
            normalized numpy array (0-255)
        """
        try:
            # Handle different data types
            if pixel_array.dtype != np.uint8:
                # Convert to float for normalization
                pixel_array_float = pixel_array.astype(np.float32)
                
                # Normalize to 0-255
                pixel_min = np.min(pixel_array_float)
                pixel_max = np.max(pixel_array_float)
                
                if pixel_max > pixel_min:
                    pixel_array_float = ((pixel_array_float - pixel_min) / (pixel_max - pixel_min) * 255)
                else:
                    pixel_array_float = np.zeros_like(pixel_array_float)
                
                # Clip and convert to uint8
                pixel_array = np.clip(pixel_array_float, 0, 255).astype(np.uint8)
            
            return pixel_array
        except Exception as e:
            current_app.logger.error(f"Error normalizing pixel values: {e}")
            raise
    
    @staticmethod
    def resize_image(pixel_array, target_size=(512, 512)):
        """
        Resize image to target dimensions
        
        Args:
            pixel_array: numpy array of pixel data
            target_size: tuple of (width, height)
            
        Returns:
            resized numpy array
        """
        try:
            # Convert to PIL Image
            if len(pixel_array.shape) == 2:
                # Grayscale
                image = Image.fromarray(pixel_array, mode='L')
            elif len(pixel_array.shape) == 3:
                # RGB or multi-channel
                if pixel_array.shape[2] == 3:
                    image = Image.fromarray(pixel_array, mode='RGB')
                else:
                    # Take first channel if multi-channel
                    image = Image.fromarray(pixel_array[:, :, 0], mode='L')
            else:
                raise ValueError(f"Unsupported pixel array shape: {pixel_array.shape}")
            
            # Resize
            image_resized = image.resize(target_size, Image.LANCZOS)
            
            # Convert back to numpy array
            return np.array(image_resized)
        except Exception as e:
            current_app.logger.error(f"Error resizing image: {e}")
            raise
    
    @staticmethod
    def convert_to_png(pixel_array):
        """
        Convert pixel array to PNG format
        
        Args:
            pixel_array: numpy array of pixel data
            
        Returns:
            bytes: PNG image data
        """
        try:
            # Convert to PIL Image
            if len(pixel_array.shape) == 2:
                image = Image.fromarray(pixel_array, mode='L')
            elif len(pixel_array.shape) == 3 and pixel_array.shape[2] == 3:
                image = Image.fromarray(pixel_array, mode='RGB')
            else:
                # Convert grayscale to RGB for consistency
                if len(pixel_array.shape) == 2:
                    image = Image.fromarray(pixel_array, mode='L').convert('RGB')
                else:
                    image = Image.fromarray(pixel_array[:, :, 0], mode='L').convert('RGB')
            
            # Save to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            return img_byte_arr.getvalue()
        except Exception as e:
            current_app.logger.error(f"Error converting to PNG: {e}")
            raise
    
    @staticmethod
    def process_dicom_to_preview(file_data, resize=True, target_size=(512, 512)):
        """
        Process DICOM file to generate PNG preview
        
        Args:
            file_data: DICOM file data as bytes
            resize: Whether to resize the image
            target_size: Target dimensions for resizing
            
        Returns:
            tuple: (png_bytes, metadata_dict)
        """
        try:
            # Read DICOM
            dicom_dataset = DICOMProcessor.read_dicom(file_data)
            
            # Extract metadata
            metadata = {}
            metadata_tags = [
                'PatientID', 'StudyDate', 'Modality', 'BodyPartExamined',
                'StudyDescription', 'SeriesDescription', 'Rows', 'Columns',
                'BitsAllocated', 'BitsStored', 'PixelSpacing'
            ]
            
            for tag in metadata_tags:
                if hasattr(dicom_dataset, tag):
                    metadata[tag] = str(getattr(dicom_dataset, tag))
            
            # Extract pixel array
            pixel_array = DICOMProcessor.get_pixel_array(dicom_dataset)
            
            # Normalize pixel values
            pixel_array = DICOMProcessor.normalize_pixel_values(pixel_array)
            
            # Resize if requested
            if resize:
                pixel_array = DICOMProcessor.resize_image(pixel_array, target_size)
            
            # Convert to PNG
            png_bytes = DICOMProcessor.convert_to_png(pixel_array)
            
            return png_bytes, metadata
            
        except Exception as e:
            current_app.logger.error(f"Error processing DICOM to preview: {e}")
            raise
    
    @staticmethod
    def get_file_info(file_data):
        """
        Get basic file information
        
        Args:
            file_data: File data as bytes
            
        Returns:
            dict: File information
        """
        return {
            'size_bytes': len(file_data),
            'mime_type': 'application/dicom'
        }
