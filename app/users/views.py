from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Users, UserProfile, CapstoneGroups, TechnicalAdvisorGroups
from .serializers import (
    UsersSerializer,
    EmailAndPasswordSerializer,
    ChangeCurrentPasswordSerializer,
    CapstoneGroupsSerializer,
    CSVFileSerializer,
    EmailSerializer,
    ResetPasswordSerializer,
    RegisterSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from utils.auth import encode_tokens
from utils.permissions import IsActive, IsAdmin, IsAdminOrReadOnly, IsAdminOrCoordinator
from utils.validations import password_validator_throws_exception, reset_password_validator_throws_exception
from django.contrib.auth.hashers import (
    check_password, make_password
)

from django.core.cache import cache
import pandas as pd
from utils.activity_logs import create_activity_log
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import os, random, string
from django.utils import timezone

# Create your views here.
class MeAPIView(APIView):
    permission_classes = [IsActive]
    
    @swagger_auto_schema(
         responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
                    'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First Name'),
                    'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last Name'),
                    'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email Address'),
                    'role': openapi.Schema(type=openapi.TYPE_STRING, description='Role of the User'),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether the User is Active'),
                    'group': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Group ID'),
                            'number': openapi.Schema(type=openapi.TYPE_INTEGER, description='Group Number'),
                            'academic_year': openapi.Schema(type=openapi.TYPE_STRING, description='Academic Year'),
                        },
                        description='Group Information',
                        nullable=True,  # To allow `null` if `group` is absent
                    ),
                    'is_technical_adviser': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether the User is a Technical Adviser'),
                },
            )
        }
    )
    def get(self, request):
        user = request.instance
        
        data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "course": getattr(user, "course", None),
            "specialization": getattr(user, "specialization", None),
        }
        
        if hasattr(user, "group"):
            if user.group:
                data["group"] = {
                    "id": user.group.id,
                    "number": user.group.name,
                    "academic_year": user.group.academic_year,
                    "course_spec": f"{user.group.course} - {user.group.specialization}",
                }
            else:
                data["group"] = None
        else:
            data["group"] = None
            
        technical_advisor_group = TechnicalAdvisorGroups.objects.filter(user=user).exists()
        
        data["is_technical_adviser"] = technical_advisor_group
            
        return Response(data, status=status.HTTP_200_OK)
    
class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = EmailAndPasswordSerializer

    @swagger_auto_schema(
        request_body=EmailAndPasswordSerializer,
        responses={
            200: "user_id, access_token, refresh_token",
            400: "Invalid email or password",
            404: "User not yet registered"
        }
    )
    def post(self, request):
        data = request.data

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        email = validated_data["email"]
        password = validated_data["password"]

        try:
            user = Users.objects.get(email=email)
            is_password_correct = check_password(password, user.password)
                
            if not is_password_correct:
                message = "Invalid password."
                
                login_failed_attempts = user.login_failed_attempts
                login_failed_attempts += 1
                user.login_failed_attempts = login_failed_attempts
                
                if login_failed_attempts == 3:
                    user.temporary_disabled_date = timezone.now()
                    message = "Account is temporarily locked for 10 minutes after multiple failed login attempts."
                    
                if login_failed_attempts == 6:
                    user.temporary_disabled_date = timezone.now()
                    message = "Account is temporarily locked for hour after another multiple failed login attempts."
                    
                if login_failed_attempts == 9:
                    user.temporary_disabled_date = timezone.now()
                    message = "Account is disabled due to multiple failed login attempts. Reset your password to reactivate your account."
                    
                user.save()
                
                return Response(
                    {"message": message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
                
            current_date_time = timezone.now()
            
            if user.login_failed_attempts == 3:
                time_difference = current_date_time - user.temporary_disabled_date
                minutes_difference = abs(int(time_difference.total_seconds() // 60))
                
                if minutes_difference < 10:
                    return Response(
                        {"message": f"Account still temporarily locked for {10 - minutes_difference} minutes due to multiple failed login attempts."},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            
            if user.login_failed_attempts == 6:
                time_difference = current_date_time - user.temporary_disabled_date
                minutes_difference = abs(int(time_difference.total_seconds() // 60))
                
                if minutes_difference < 60:
                    return Response(
                        {"message": f"Account still temporarily locked for {60 - minutes_difference} minutes due to multiple failed login attempts."},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
                    
            if user.login_failed_attempts == 9:
                return Response(
                    {"message": f"Account still disabled due to multiple failed login attempts. Reset your password to reactivate your account."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            access_token, refresh_token = encode_tokens(user=user)
            user.login_failed_attempts = 0
            user.temporary_disabled_date = None
            user.save()
            
            return Response(
                {
                    "id": user.id,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
                status=status.HTTP_200_OK,
            )
        except Users.DoesNotExist:
            return Response(
                {"message": f"{email} is not yet a registered user."},
                status=status.HTTP_404_NOT_FOUND,
            )


class StudentRegisterAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = RegisterSerializer
    
    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={
            200: UsersSerializer(many=False),
            400: "Email/Student number is already registered | Password Validation Messages",
        }
    )
    def post(self, request):
        data = request.data
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        student_number = validated_data['student_number']
        email = validated_data['email']
        password = validated_data['password']
        confirm_password = validated_data['confirm_password']
        course = validated_data['course']
        specialization = validated_data['specialization']
        
        existing_email = Users.objects.filter(email=email)
        existing_student_number = Users.objects.filter(student_number=student_number)
        
        if existing_email:
            return Response(
                {"message": f"Email {email} is already registered."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if existing_student_number:
            return Response(
                {"message": f"Student number {student_number} is already registered."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if password != confirm_password:
            return Response(
                {"message": "Passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        password_validator_throws_exception(password=confirm_password, has_capital_letter_checker=True, has_digit_checker=True, has_special_char_checker=True)
        
        created_student = Users(
            first_name=first_name,
            last_name=last_name,
            student_number=student_number,
            email=email,
            password=make_password(confirm_password),
            role="Student",
            course=course,
            specialization=specialization,
        )
        created_student._is_notif = False
        created_student.save()
        
        serialized_data = UsersSerializer(created_student).data
        return Response(serialized_data, status=status.HTTP_201_CREATED)
        
class ForgotPasswordAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = EmailSerializer
    
    @swagger_auto_schema(
        request_body=EmailSerializer,
        responses={
            200: "Password reset link sent successfully.",
            404: "Email is not yet a registered user."
        }
    )
    def post(self, request):
        data = request.data
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data["email"]
        
        existing_user = Users.objects.filter(email=email)
        
        if not existing_user:
            return Response(
                {"message": f"{email} is not yet a registered user."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        user = existing_user.first()
        self.send_reset_password_link(user=user)
        
        return Response({
            "message": "Password reset link sent successfully."
        }, status=status.HTTP_200_OK)
        
    def send_reset_password_link(self, user: Users):
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        context = {
            "name": user.get_full_name,
            "link": f"{os.getenv('FRONTEND_HOST_URL')}/reset-password/?token={token}"
        }
        
        email_html_message = render_to_string("email/reset_password.html", context)
        
        send_mail(
            subject="Capstone Directory Reset Password",
            message="",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            html_message=email_html_message,
            auth_user=settings.EMAIL_HOST_USER,
            auth_password=settings.EMAIL_HOST_PASSWORD,
        )
        
        user.token = token
        user.save()

class ResetPasswordAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = ResetPasswordSerializer
    
    @swagger_auto_schema(
        request_body=ResetPasswordSerializer,
        responses={
            200: "Password reset successfully.",
            404: "User with token #### does not exists for password reset."
        }
    )
    def post(self, request):
        data = request.data
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]
        confirm_password = serializer.validated_data["confirm_password"]
        
        reset_password_validator_throws_exception(new_password=new_password, confirm_password=confirm_password)
        
        try:
            existing_user_with_token = Users.objects.get(token=token)
            existing_user_with_token.password=confirm_password
            existing_user_with_token.token = None
            existing_user_with_token._is_notif = False
            existing_user_with_token.login_failed_attempts = 0
            existing_user_with_token.temporary_disabled_date = None
            existing_user_with_token.save()
            
            return Response({
                "message": "Password reset successfully."
            }, status=status.HTTP_200_OK)
        except Users.DoesNotExist:
            return Response(
                {"message": f"User with token {token} does not exists for password reset."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        

class ChangeCurrentPasswordAPIView(APIView):
    permission_classes = [IsActive]
    serializer_class = ChangeCurrentPasswordSerializer

    @swagger_auto_schema(
        request_body=ChangeCurrentPasswordSerializer,
        responses={
            200: "Password updated successfully.",
            400: "Password must not match the old password, must be at least 8 characters long, contain at least one digit, one uppercase letter, or one special character.",
            404: "User not yet registered"
        }
    )
    def post(self, request):
        data = request.data
        user = request.instance

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        email = user.email
        current_password = data["current_password"]
        new_password = data["new_password"]

        is_current_password_correct = check_password(current_password, user.password)
        
        if not is_current_password_correct:
            return Response(
                {"message": "Entered current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        password_validator_throws_exception(
            password=new_password,
            old_password=current_password,
            has_capital_letter_checker=True,
            has_digit_checker=True,
            has_special_char_checker=True,
        )

        try:
            user = Users.objects.get(email=email)
            user.password = new_password
            user.save()
            
            create_activity_log(actor=user, action="Changed current password to a new password.")

            return Response(
                {"message": "Password updated successfully."},
                status=status.HTTP_200_OK,
            )
        except Users.DoesNotExist:
             return Response(
                {"message": f"{email} is not yet a registered user."},
                status=status.HTTP_404_NOT_FOUND,
            )


@swagger_auto_schema()
class UsersViewset(viewsets.ModelViewSet):
    serializer_class = UsersSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["first_name", "last_name", "email"]
    filterset_fields = ["role", "is_active", "course", "specialization"]
    permission_classes = [IsActive]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        method = self.request.method

        context["request"] = method

        return context
    
    def get_queryset(self):
        user = self.request.instance
        role = user.role
        
        if role.lower() in ["admin", "administrator"]:
            return Users.objects.order_by("last_name")
        elif role.lower() == "faculty":
            return Users.objects.filter(role="student").order_by("last_name")
        elif role.lower() in ["coordinator", "capstone coordinator"]:
            return Users.objects.filter(role__in=["student", "faculty"]).order_by("last_name")
        else:
            return Users.objects.filter(id=user.id).order_by("last_name")
        
    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.instance
        
        if user.role.lower() not in ['admin', 'administrator']:
            return Response({"message": "Only administrators can create new users."}, status=status.HTTP_403_FORBIDDEN)
        
        created_role = data.get('role', None)
        
        if created_role.lower() == 'student':
            student_number = data.get('student_number')
            existing_student_number = Users.objects.filter(student_number=student_number)
            
            if existing_student_number.exists():
                return Response({"message": f"Student with student number '{student_number}' already exists."})
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        validated_data["password"] = f"{validated_data['first_name']}.{validated_data['last_name']}"
        
        created_user = Users(**validated_data)
        created_user._is_notif = True
        created_user.save()
        
        self.send_account_creation_email(created_user, f"{created_user.first_name}.{created_user.last_name}")
        create_activity_log(actor=user, action=f"Created user '{validated_data.get('email', 'Anonymous User')}'.")
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.instance 
        data = request.data
        
        old_group = getattr(instance, 'group', None)
        
        serializer = self.serializer_class(data=data, instance=instance, partial=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        for field, value in validated_data.items():
            setattr(instance, field, value)
        
        new_group = validated_data.get('group', None)

        if new_group:
            group_members = Users.objects.filter(group=new_group).values_list('id', flat=True)
            
            if len(group_members) == 4 and instance.id not in group_members:
                return Response({"message": "A group can only have exactly 4 members."}, status=status.HTTP_400_BAD_REQUEST)
        
            if old_group != new_group:
                instance._is_notif = True
            
        instance.save()
        
        create_activity_log(actor=user, action=f"Updated user '{instance.email}'.")
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        user = request.instance
        instance = self.get_object()
        
        create_activity_log(actor=user, action=f"Deleted user '{instance.email}'.")
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema(
        manual_parameters=[],
        responses={
            400: "Invalid file format. Please upload an excel file."
        }
    )
    @action(detail=False, methods=["POST"], serializer_class=CSVFileSerializer, url_path="upload-users", filter_backends=[])
    def bulk_create_users(self, request):
        data = request.data
        user = request.instance
        
        serializer = CSVFileSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        file = data["file"]
        if not str(file).endswith(".xlsx"):
            return Response(
                {"message": "Invalid file format. Please upload an excel file."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        df = pd.read_excel(file)
        df = df.fillna('')
        file_data = df.to_dict(orient="records")
        
        create_activity_log(actor=user, action="Uploaded an excel file of users.")
        self.upload_users_from_excel(file_data=file_data)
        
        return Response({
            "message": f"{str(file)} is being uploaded."
        }, status=status.HTTP_201_CREATED)
        
    def upload_users_from_excel(self, file_data):
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
                
                if email is None or email == "":
                    break
                
                created_user = Users(
                    first_name=first_name.title(),
                    last_name=last_name.title(),
                    email=email,
                    password=password,
                    role=role.lower(),
                    course=course,
                    specialization=specialization,
                    student_number=student_number
                )
                
                users_to_write.append(created_user)
                self.send_account_creation_email(created_user=created_user, plain_text_password=f"{first_name}.{last_name}")
                
            Users.objects.bulk_create(users_to_write)
            print("Users created from excel file.")
                
            cache.set('users_upload', True, timeout=1800)
        except Exception as e:
            print(f"Error occurred while reading Excel file: {str(e)}")
            pass
    
    def send_account_creation_email(self, created_user: Users, plain_text_password):
        context = {
            "name": created_user.get_full_name,
            "email": created_user.email,
            "password": plain_text_password,
        }
        
        email_html_message = render_to_string("email/account_creation.html", context)
        
        send_mail(
            subject="Capstone Directory Account Creation",
            message="",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[created_user.email],
            html_message=email_html_message,
            auth_user=settings.EMAIL_HOST_USER,
            auth_password=settings.EMAIL_HOST_PASSWORD,
        )
        
    @swagger_auto_schema(
        manual_parameters=[],
        responses={
            200: "status: True/False, message: Recent upload of users was successful/is still in progress."
        }
    )
    @action(detail=False, methods=["GET"], url_path="check-upload-status", filter_backends=[])
    def check_users_upload_status(self, request):
        is_uploaded = cache.get("users_upload", False)
        
        if is_uploaded:
            message = "Recent upload of users was successful."
        else:
            message = "Recent upload of users is still in progress."
            
        return Response({
            "status": is_uploaded,
            "message": message
        }, status=status.HTTP_200_OK)

# NOT YET NEEDED
# class UserProfileViewset(viewsets.ModelViewSet):
#     queryset = UserProfile.objects.order_by("user__last_name")
#     serializer_class = UserProfileSerializer
#     filter_backends = [DjangoFilterBackend, SearchFilter]
#     search_fields = ["user__first_name", "user__last_name", "user__email"]
    
#     def get_queryset(self):
#         user = self.request.instance
#         role = user.role
        
#         if role.lower() in ["admin", "administrator"]:
#             return UserProfile.objects.order_by("user__last_name").select_related("user")
#         else:
#             return UserProfile.objects.filter(user=user)
   
@swagger_auto_schema()     
class CapstoneGroupsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrCoordinator]
    serializer_class = CapstoneGroupsSerializer
    pagination_class = None
    
    def get_queryset(self):
        queryset = CapstoneGroups.objects.order_by("created_at")\
            .prefetch_related("group_members") \
        
        return queryset
        
        