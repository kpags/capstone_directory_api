import os, requests
from rest_framework.exceptions import ValidationError

        
def upload_to_cloudinary(file):
    data = {
        "upload_preset": os.getenv("UNSIGNED_PRESET"),
        "folder": os.getenv("UPLOAD_FOLDER")
    }
    
    files = {
        "file": file
    }
    
    response = requests.post(f"https://api.cloudinary.com/v1_1/{os.getenv('CLOUD_NAME')}/raw/upload", files=files, data=data)
    
    response_json = response.json()
    
    if "error" in response_json.keys():
        raise ValidationError({
            "message": "Error uploading to cloudinary.",
            "details": response_json
        })
        
    return response.json()