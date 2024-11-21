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
    CapstoneGroupsSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from utils.auth import encode_tokens
from utils.permissions import IsActive, IsAdmin
from utils.validations import password_validator_throws_exception
from django.contrib.auth.hashers import (
    check_password,
)


# Create your views here.
class MeAPIView(APIView):
    permission_classes = [IsActive]
    
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
                    "academic_year": user.group
                }
        
        technical_advisor_group = TechnicalAdvisorGroups.objects.filter(user=user).exists()
        
        data["is_technical_adviser"] = technical_advisor_group
            
        return Response(data, status=status.HTTP_200_OK)
    
class LoginAPIView(APIView):
    permission_classes = []
    serializer_class = EmailAndPasswordSerializer

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


class ChangeCurrentPasswordAPIView(APIView):
    permission_classes = [IsActive]
    serializer_class = ChangeCurrentPasswordSerializer

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

            return Response(
                {"message": "Password updated successfully."},
                status=status.HTTP_200_OK,
            )
        except Users.DoesNotExist:
            raise ValidationError({"message": f"{email} is not yet a registered user."})


class UsersViewset(viewsets.ModelViewSet):
    queryset = Users.objects.order_by("last_name")
    serializer_class = UsersSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["first_name", "last_name", "email"]
    filterset_fields = ["role", "is_active", "course", "specialization"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        method = self.request.method

        if method in ["PUT", "PATCH"]:
            context["request"] = method

        return context
    
    def get_queryset(self):
        user = self.request.instance
        role = user.role
        
        if role.lower() in ["admin", "administrator"]:
            return Users.objects.order_by("last_name")
        else:
            return Users.objects.filter(id=user.id)

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
    permission_classes = [IsAdmin]
    serializer_class = CapstoneGroupsSerializer