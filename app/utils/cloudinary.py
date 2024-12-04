import os, requests
from rest_framework.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import cloudinary, cloudinary.uploader
from pathlib import Path

CLOUDINARY = {
    'cloud_name': os.getenv('CLOUD_NAME'),
    'api_key': os.getenv('CLOUDINARY_API_KEY'),
    'api_secret': os.getenv('CLOUDINARY_API_SECRET'),
}

BASE_DIR = Path(__file__).resolve().parent.parent

def handle_uploaded_file(file):
    file_path = str(BASE_DIR / f"uploaded_files/{file.name}")
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return file_path

def delete_local_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        
def upload_to_cloudinary(file):
    file_path = handle_uploaded_file(file=file)
    
    response = cloudinary.uploader.upload(
        file_path,
        resource_type='raw',
        pages=1,
        public_id=f"pdfs/{file.name}",
        use_filename=True,
        unique_filename=True,
        folder="uploads"
    )
    
    response_json = response
        
    delete_local_file(file_path=file_path)
    return response