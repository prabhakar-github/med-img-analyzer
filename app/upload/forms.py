from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask import current_app


class UploadForm(FlaskForm):
    """Form for uploading DICOM images"""
    
    client_id = SelectField('Client', coerce=int, validators=[
        DataRequired(message='Client selection is required')
    ])
    
    patient_reference_id = StringField('Patient Reference ID', validators=[
        DataRequired(message='Patient Reference ID is required'),
        Length(min=1, max=100, message='Patient Reference ID must be between 1 and 100 characters')
    ])
    
    modality = SelectField('Modality', choices=[
        ('XRAY', 'X-Ray'),
        ('MRI', 'MRI'),
        ('CT', 'CT'),
        ('ULTRASOUND', 'Ultrasound'),
        ('MAMMOGRAPHY', 'Mammography')
    ], validators=[
        DataRequired(message='Modality selection is required')
    ])
    
    dicom_files = FileField('DICOM Files', validators=[
        FileRequired(message='At least one DICOM file is required'),
        FileAllowed(['dcm'], message='Only .dcm files are allowed')
    ])
    
    submit = SubmitField('Upload Images')
