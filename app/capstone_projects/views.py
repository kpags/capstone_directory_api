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
    CapstoneProjectsCustomSerializer,
    CapstoneProjectApprovalSerializer,
    CapstoneProjectBestProjectSerializer
)
from utils.permissions import IsActive, IsAdmin
from .filters import CapstoneProjectsFilter
from utils.pdf_keywords_generator import generate_pdf_keywords
from utils.cloudinary import upload_to_cloudinary
from utils.activity_logs import create_activity_log

# Create your views here.
class CapstoneProjectsViewset(viewsets.ModelViewSet):
    queryset = CapstoneProjects.objects.order_by('created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['title', 'capstone_group__number', 'capstone_group__academic_year']
    filterset_class = CapstoneProjectsFilter
    
    def get_serializer_context(self):
        user = self.request.instance
        method = self.request.method
        
        context = super().get_serializer_context()
        context["user"] = user
        context["request"] = method
        return context
    
    def get_serializer_class(self):
        method = self.request.method
        path = self.request.path
        
        if "approve" in path:
            return CapstoneProjectApprovalSerializer
        
        if "best-project" in path:
            return CapstoneProjectBestProjectSerializer
        
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
        user = request.instance
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
        
        project = CapstoneProjects.objects.create(
            capstone_group=group,
            keywords=keywords,
            acm_paper=acm_file_url,
            **validated_data
        )
        
        serialized_data = serializer.data
        serialized_data["keywords"] = keywords
        serialized_data["acm_paper"] = acm_file_url
        
        create_activity_log(actor=user, action=f"Uploaded capstone project '{project.title}' by Group#{project.capstone_group.number} of {project.capstone_group.course}.")
        return Response(serialized_data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        user = request.instance
        project = self.get_object()
        
        if not user.role.lower() in ["admin", "administrator"]:
            raise ValidationError({
                "message": "Only administrators can delete capstone projects."
            })
            
        create_activity_log(actor=user, action=f"Deleted capstone project '{project.title}' by Group#{project.capstone_group.number} of {project.capstone_group.course}.")
        return super().destroy(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        user = request.instance
        project = self.get_object()
        
        if not user.role.lower() in ["admin", "administrator"]:
            raise ValidationError({
                "message": "Only administrators can update the details of capstone projects."
            })
            
        create_activity_log(actor=user, action=f"Deleted capstone project '{project.title}' by Group#{project.capstone_group.number} of {project.capstone_group.course}.")
        return super().update(request, *args, **kwargs)
    
    @action(detail=False, methods=["POST"], permission_classes=[IsAdmin], serializer_class=CapstoneProjectApprovalSerializer, url_path="approve")
    def approve_project(self, request):
        data = request.data
        user = request.instance
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        project_id = validated_data.get('project_id', None)
        is_approved = validated_data.get('is_approved', False)
        
        if not project_id:
            raise ValidationError({
                "message": "Project ID is required to approve it."
            })
        
        try:
            existing_project = CapstoneProjects.objects.get(id=project_id)
            existing_project.is_approved = is_approved
            existing_project.save()
            
            if is_approved:
                approve_word = "Approved"
            else:
                approve_word = "Disapproved"
            
            create_activity_log(actor=user, action=f"{approve_word} the capstone project '{existing_project.title}' by Group#{existing_project.capstone_group.number} of {existing_project.capstone_group.course}.")
            return Response({
                "message": f"Capstone project with ID '{project_id}' has been {approve_word.lower()} by {user.get_full_name}."
            }, status=status.HTTP_200_OK)
        except CapstoneProjects.DoesNotExist:
            raise ValidationError({
                "message": f"Project with ID '{project_id}' does not exist."
            })
            
    @action(detail=False, methods=["POST"], permission_classes=[IsAdmin], serializer_class=CapstoneProjectBestProjectSerializer, url_path="best-project")
    def make_best_project(self, request):
        data = request.data
        user = request.instance
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        project_id = validated_data.get('project_id', None)
        is_best_project = validated_data.get('is_best_project', False)
        
        if not project_id:
            raise ValidationError({
                "message": "Project ID is required to make it a best project."
            })
        
        try:
            existing_project = CapstoneProjects.objects.get(id=project_id)
            existing_project.is_best_project = is_best_project
            existing_project.save()
            
            if is_best_project:
                best_project_word = "Marked"
            else:
                best_project_word = "Removed"
            
            create_activity_log(actor=user, action=f"{best_project_word} the capstone project '{existing_project.title}' by Group#{existing_project.capstone_group.number} of {existing_project.capstone_group.course} as best project.")
            return Response({
                "message": f"Capstone project with ID '{project_id}' has been {best_project_word.lower()} as best project by {user.get_full_name}."
            }, status=status.HTTP_200_OK)
        except CapstoneProjects.DoesNotExist:
            raise ValidationError({
                "message": f"Project with ID '{project_id}' does not exist."
            })