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
    UserProfileSerializer,
    CapstoneGroupsSerializer,
    CSVFileSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from utils.auth import encode_tokens
from utils.permissions import IsActive, IsAdmin, IsAdminOrReadOnly, IsAdminOrCoordinator
from utils.validations import password_validator_throws_exception
from django.contrib.auth.hashers import (
    check_password,
)
from .tasks import upload_users_from_excel
from django.core.cache import cache
import pandas as pd
from utils.activity_logs import create_activity_log
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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
        }
        
        if hasattr(user, "group"):
            if user.group:
                data["group"] = {
                    "id": user.group.id,
                    "number": user.group.number,
                    "academic_year": user.group.academic_year,
                    "course_spec": f"{user.group.course} - {user.group.specialization}",
                }
        
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
                return Response(
                    {"message": "Invalid password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            access_token, refresh_token = encode_tokens(user=user)

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

class ForgotPasswordAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_classes = EmailAndPasswordSerializer
    
    @swagger_auto_schema(
        request_body=EmailAndPasswordSerializer,
        responses={
            200: "Password successfully changed.",
            400: "User is not active.",
            404: "Email is not yet a registered user."
        }
    )
    def post(self, request):
        data = request.data
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exceptions=True)
        valdiated_data = serializer.validated_data
        
        email = valdiated_data["email"]
        password = valdiated_data["password"]
        
        existing_user = Users.objects.filter(email=email)
        
        if not existing_user:
            return Response(
                {"message": f"{email} is not yet a registered user."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        user = existing_user.first()
        
        if not user.is_active:
            return Response(
                {"message": "User is not active."},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        user.password = password
        user.save()
        
        return Response({
            "message": "Password successfully changed.",
        }, status=status.HTTP_200_OK)
        

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
    queryset = Users.objects.order_by("last_name")
    serializer_class = UsersSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["first_name", "last_name", "email"]
    filterset_fields = ["role", "is_active", "course", "specialization"]
    permission_classes = [IsAdminOrReadOnly]

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
        else:
            return Users.objects.filter(id=user.id)
        
    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.instance
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        serializer.save()
                
        create_activity_log(actor=user, action=f"Created user '{validated_data.get('email', 'Anonymous User')}'.")
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.instance 
        
        create_activity_log(actor=user, action=f"Updated user '{instance.email}'.")
        return super().update(request, *args, **kwargs)
    
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
        
        upload_users_from_excel.delay(file_data=file_data)
        create_activity_log(actor=user, action="Uploaded an excel file of users.")
        
        return Response({
            "message": f"{str(file)} is being uploaded."
        }, status=status.HTTP_201_CREATED)
    
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

@swagger_auto_schema()
class UserProfileViewset(viewsets.ModelViewSet):
    queryset = UserProfile.objects.order_by("user__last_name")
    serializer_class = UserProfileSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["user__first_name", "user__last_name", "user__email"]
    
    def get_queryset(self):
        user = self.request.instance
        role = user.role
        
        if role.lower() in ["admin", "administrator"]:
            return UserProfile.objects.order_by("user__last_name").select_related("user")
        else:
            return UserProfile.objects.filter(user=user)
        
class CapstoneGroupsViewset(viewsets.ModelViewSet):
    queryset = CapstoneGroups.objects.order_by("created_at")
    permission_classes = [IsAdminOrCoordinator]
    serializer_class = CapstoneGroupsSerializer