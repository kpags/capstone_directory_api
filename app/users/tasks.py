from celery import shared_task
from utils.celery.celery_base_task import *
import pandas as pd
from users.models import Users
from django.core.cache import cache
from django.contrib.auth.hashers import (
    make_password,
)
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

@shared_task
def upload_users_from_excel(file_data):
    try:
        users_to_write = []
        
        print("Getting data from excel file...")
        for row in file_data:
            first_name = row['First Name']
            last_name = row['Last Name']
            email = row['Email']
            password = make_password(f"{first_name}.{last_name}")
            student_number = row.get('Student Number', None)
            course = row.get('Course', None)
            specialization = row.get('Specialization', None)
            role = row["Role"]
            
            user = Users(
                first_name=first_name.title(),
                last_name=last_name.title(),
                email=email,
                password=password,
                role=role.lower(),
                course=course,
                specialization=specialization,
                student_number=student_number
            )
            
            users_to_write.append(user)
            send_account_creation_email(user=user, plain_text_password=f"{first_name}.{last_name}")
            
        Users.objects.bulk_create(users_to_write)
        print("Users created from excel file.")
            
        cache.set('users_upload', True, timeout=1800)
    except Exception as e:
        print(f"Error occurred while reading Excel file: {str(e)}")
        pass
    
def send_account_creation_email(user: Users, plain_text_password):
    context = {
        "name": user.get_full_name,
        "email": user.email,
        "password": plain_text_password,
    }
    
    email_html_message = render_to_string("email/account_creation.html", context)
    
    send_mail(
        subject="Capstone Directory Account Creation",
        message="",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        html_message=email_html_message,
        auth_user=settings.EMAIL_HOST_USER,
        auth_password=settings.EMAIL_HOST_PASSWORD,
    )