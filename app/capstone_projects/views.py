from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CapstoneProjects, CapstoneGroups
from users.models import Users
from .serializers import (
    CapstoneProjectsSerializer,
    CapstoneProjectsCustomSerializer
)
from utils.permissions import IsActive, IsAdmin
from .filters import CapstoneProjectsFilter
from utils.pdf_keywords_generator import generate_pdf_keywords
from utils.cloudinary import upload_to_cloudinary

# Create your views here.
class CapstoneProjectsViewset(viewsets.ModelViewSet):
    queryset = CapstoneProjects.objects.order_by('created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['title', 'capstone_group__number', 'capstone_group__academic_year']
    filterset_class = CapstoneProjectsFilter
    
    def get_serializer_context(self):
        user = self.request.instance
        context = super().get_serializer_context()
        context["user"] = user
        return context
    
    def get_serializer_class(self):
        method = self.request.method
        
        if method == "POST":
            return CapstoneProjectsCustomSerializer
        
        return CapstoneProjectsSerializer
    
    def get_queryset(self):
        user = self.request.instance
        role = user.role.lower()
        
        if role in ["admin", "administrator"]:
            return CapstoneProjects.objects.order_by('created_at')
        
        return CapstoneProjects.objects.filter(capstone_group=user.group)
    
    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        acm_file = validated_data.pop("acm_paper", None)
        keywords = generate_pdf_keywords(file=acm_file)
        
        group = CapstoneGroups.objects.get(id=data["capstone_group_id"])
        group_members = Users.objects.filter(group=group)
        
        if "members" not in validated_data.keys():
            members = []
            for member in group_members:
                members.append(f"{member.first_name} {member.last_name}")
                
            validated_data["members"] = members
        
        binary_acm_form_file = request.FILES["acm_paper"]
        cloudinary_response = upload_to_cloudinary(file=binary_acm_form_file)
        acm_file_url = cloudinary_response.get("url", None)
        
        CapstoneProjects.objects.create(
            capstone_group=group,
            keywords=keywords,
            acm_paper=acm_file_url,
            **validated_data
        )
        
        serialized_data = serializer.data
        serialized_data["keywords"] = keywords
        serialized_data["acm_paper"] = acm_file_url
        
        return Response(serialized_data, status=status.HTTP_201_CREATED)