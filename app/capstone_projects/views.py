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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q

# Create your views here.

class CapstoneProjectsViewset(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend]
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

    @swagger_auto_schema()
    def get_queryset(self):
        user = self.request.instance
        role = user.role.lower()
        
        if role in ["admin", "administrator"]:
            queryset = CapstoneProjects.objects.order_by('-created_at')
        else:
            queryset = CapstoneProjects.objects.filter(capstone_group=user.group).order_by('-created_at')
            
        queryset = queryset.exclude(Q(is_approved__isnull=True) | Q(is_approved=""))
        return queryset
    
    @swagger_auto_schema(
        request_body=CapstoneProjectsCustomSerializer,
        responses={
            201: CapstoneProjectsCustomSerializer(many=False),
        }
    )
    def create(self, request, *args, **kwargs):
        user = request.instance
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        acm_file = validated_data.pop("acm_paper", None)
        keywords = generate_pdf_keywords(file=acm_file)
        group_members = data.getlist("members[]", [])
        capstone_group_id = validated_data.get("capstone_group_id", None)
        group = None
        
        if capstone_group_id:
            group = CapstoneGroups.objects.filter(id=data["capstone_group_id"])
            
            if group:
                group = group.first()
                group_members = Users.objects.filter(group=group)
                
                if "members" not in validated_data.keys():
                    members = []
                    for member in group_members:
                        members.append(f"{member.first_name} {member.last_name}")
                        
                    validated_data["members"] = members
                    
        if group is None:
            group = user.group
        
        if group_members:
            validated_data["members"] = group_members
            
        binary_acm_form_file = request.FILES["acm_paper"]
        cloudinary_response = upload_to_cloudinary(file=binary_acm_form_file)
        acm_file_url = cloudinary_response.get("url", None)
        
        ip_reg = validated_data.pop("ip_regristration", None)
        members = validated_data.pop("members", None)
        project = CapstoneProjects(
            capstone_group=group,
            keywords=keywords,
            acm_paper=acm_file_url,
            ip_registration=ip_reg,
            members=members,
            **validated_data
        )
        
        if user.role.lower() in ['admin', 'administrator']:
            project.is_approved = True
        
        project.save()
        serialized_data = serializer.data
        serialized_data["keywords"] = keywords
        serialized_data["acm_paper"] = acm_file_url
        
        if group:
            action = f"Uploaded capstone project '{project.title}' by Group#{project.capstone_group.name} of {project.capstone_group.course}."
        else:
            action = f"Uploaded capstone project '{project.title}' from a former capstone group published in {validated_data.get('date_published', 'Unknown')}."
            
        create_activity_log(actor=user, action=action)
        return Response(serialized_data, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        responses={
            204: CapstoneProjectsSerializer(many=False),
            401: "Only administrators can delete capstone projects."
        }
    )
    def destroy(self, request, *args, **kwargs):
        user = request.instance
        project = self.get_object()
        
        if not user.role.lower() in ["admin", "administrator"]:
            return Response({
                "message": "Only administrators can delete capstone projects."
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        create_activity_log(actor=user, action=f"Deleted capstone project '{project.title}'.")
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the project'),
                'ip_regristration': openapi.Schema(type=openapi.TYPE_STRING, description='Storange link of the file'),
                'acm_paper': openapi.Schema(type=openapi.TYPE_STRING, description='Storange link of the file'),
                'full_document': openapi.Schema(type=openapi.TYPE_STRING, description='Storange link of the file'),
                'pubmat': openapi.Schema(type=openapi.TYPE_STRING, description='Storange link of the file'),
                'approval_form': openapi.Schema(type=openapi.TYPE_STRING, description='Storange link of the file'),
                'source_code': openapi.Schema(type=openapi.TYPE_STRING, description='Storange link of the file'),
                'members': openapi.Schema(type=openapi.TYPE_STRING, description='Array of names of the members'),
                'date_published': openapi.Schema(type=openapi.TYPE_STRING, description='Date'),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='Project status'),
            },
            required=['field1'],  # Fields that are required
        ),
        responses={
            200: CapstoneProjectsSerializer(many=False),
            401: "Only administrators update the details capstone projects."
        }
    )
    def update(self, request, *args, **kwargs):
        data = request.data
        user = request.instance
        project = self.get_object()
        
        if not user.role.lower() in ["admin", "administrator"]:
            return Response({
                "message": "Only administrators can update the details capstone projects."
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        capstone_group_id = data.get("capstone_group_id", None)
        
        serializer = CapstoneProjectsSerializer(data=data, instance=project)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        if capstone_group_id:
            group = CapstoneGroups.objects.filter(id=data["capstone_group_id"])
            
            if group:
                group = group.first()
                validated_data["capstone_group"] = group
                group_members = Users.objects.filter(group=group)
                
                if "members" not in validated_data.keys():
                    members = []
                    for member in group_members:
                        members.append(f"{member.first_name} {member.last_name}")
                        
                    validated_data["members"] = members
                    
        acm_file = validated_data.pop("acm_paper", None)
        keywords = generate_pdf_keywords(file=acm_file)
        capstone_group_id = validated_data.get("capstone_group_id", None)
        group = None
        
        binary_acm_form_file = request.FILES["acm_paper"]
        cloudinary_response = upload_to_cloudinary(file=binary_acm_form_file)
        acm_file_url = cloudinary_response.get("url", None)
        
        project.keywords = keywords
        project.acm_paper = acm_file_url
        for field, value in validated_data.items():
            setattr(project, field, value)
        project.save()
            
        serialized_data = CapstoneProjectsSerializer(project).data
        
        create_activity_log(actor=user, action=f"Updated capstone project '{project.title}'.")
        return Response(serialized_data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "is_best_project",
                openapi.IN_QUERY,
                description="Filter by best projects or not",
                type=openapi.TYPE_BOOLEAN,
                required=False,
            ),
            openapi.Parameter(
                "is_ip_registered",
                openapi.IN_QUERY,
                description="Filter by registered ip or not",
                type=openapi.TYPE_BOOLEAN,
                required=False,
            ),
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search by title, group name, academic year, keywords",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "sort_by",
                openapi.IN_QUERY,
                description="Sort by newest, oldest, and alphabetical (Ascending/Descending)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={
            200: CapstoneProjectsSerializer(many=False),
        }
    )
    @action(detail=False, methods=["GET"], permission_classes=[IsActive], serializer_class=CapstoneProjectsSerializer, filterset_class=[], url_path="all-projects")
    def get_all_projects_based_on_course(self, request):
        user = request.instance
        user_course = user.course
        user_spec = user.specialization
        user_role = user.role
        
        is_best_project = request.query_params.get('is_best_project', None)
        is_ip_registered = request.query_params.get('is_ip_registered', None)
        search = request.query_params.get('search', None)
        sort_by = request.query_params.get('sort_by', None)
        
        if user_role.lower() == "student":
            queryset = CapstoneProjects.objects.filter(specialization=user_spec)
        
        if user_role.lower() in ['faculty', 'coordinator', 'capstone coordinator']:
            specialization_filter = request.query_params.get('specialization', None)
            
            if specialization_filter:
                queryset = CapstoneProjects.objects.filter(course=user_course, specialization=specialization_filter)
            else:
                queryset = CapstoneProjects.objects.filter(course=user_course)
        
        if is_best_project:
            queryset = queryset.filter(is_best_project=True)
        
        if is_ip_registered:
            if is_ip_registered.lower() == "true" or is_ip_registered == True:
                queryset = queryset.exclude(ip_registration=None).exclude(ip_registration="")
            elif is_ip_registered.lower() == "false" or is_ip_registered == False:
                queryset = queryset.filter(Q(ip_registration=None) | Q(ip_registration=""))
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(capstone_group__name=search) | 
                Q(capstone_group__academic_year=search) | 
                Q(keywords__overlap=search)
            )
            
        if sort_by:
            if sort_by.lower() == "newest":
                queryset = queryset.order_by('-created_at')
            elif sort_by.lower() == "oldest":
                queryset = queryset.order_by('created_at')
            elif sort_by.lower() == "alphabetical_asc":
                queryset = queryset.order_by('title')
            elif sort_by.lower() == "alphabetical_desc":
                queryset = queryset.order_by('-title')
        
        queryset = queryset.exclude(Q(is_approved__isnull=True) | Q(is_approved=""))
        serialized_data = self.serializer_class(queryset).data
        
        return Response(serialized_data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        request_body=CapstoneProjectApprovalSerializer,
        responses={
            200: "Capstone project with ID '####' has been approved/disapproved by #####.",
            400: "ProjectID is required to approve it.",
            404: "Project with ID '####' does not exist."
        }
    )
    @action(detail=False, methods=["POST"], permission_classes=[IsAdmin], serializer_class=CapstoneProjectApprovalSerializer, url_path="approve")
    def approve_project(self, request):
        data = request.data
        user = request.instance
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        project_id = validated_data.get('project_id', None)
        is_approved = validated_data.get('is_approved', None)
                
        if not project_id:
            raise ValidationError({
                "message": "Project ID is required to approve it."
            })
        
        try:
            existing_project = CapstoneProjects.objects.get(id=project_id)
            existing_project.is_approved = is_approved
            existing_project._for_approval = True
            existing_project.save()
            
            if is_approved:
                approve_word = "Approved"
            else:
                approve_word = "Rejected"
                
            has_group = getattr(existing_project, "capstone_group", None)
            
            if has_group and (has_group is not None or has_group != ""):
                action = f"{approve_word} the capstone project '{existing_project.title}' by Group#{existing_project.capstone_group.name} of {existing_project.capstone_group.course}."
            else:
                action = f"{approve_word} the capstone project '{existing_project.title}'."
                
            create_activity_log(actor=user, action=action)
            return Response({
                "message": f"Capstone project with ID '{project_id}' has been {approve_word.lower()} by {user.get_full_name}."
            }, status=status.HTTP_200_OK)
        except CapstoneProjects.DoesNotExist:
            return Response({
                "message": f"Project with ID '{project_id}' does not exist."
            }, status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        request_body=CapstoneProjectBestProjectSerializer,
        responses={
            200: "Capstone project with ID '####' has been mared/removed as best project by #####.",
            400: "ProjectID is required to make it a best project.",
            404: "Project with ID '####' does not exist."
        }
    )
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
            existing_project._for_best_project = True
            existing_project.save()
            
            if is_best_project:
                best_project_word = "Marked"
            else:
                best_project_word = "Removed"
            
            has_group = getattr(existing_project, "capstone_group", None)
            
            if has_group and (has_group is not None or has_group != ""):
                action = f"{best_project_word} the capstone project '{existing_project.title}' by Group#{existing_project.capstone_group.name} of {existing_project.capstone_group.course} as best project."
            else:
                action = f"{best_project_word} the capstone project '{existing_project.title}' as best project."
                
            create_activity_log(actor=user, action=action)
            return Response({
                "message": f"Capstone project with ID '{project_id}' has been {best_project_word.lower()} as best project by {user.get_full_name}."
            }, status=status.HTTP_200_OK)
        except CapstoneProjects.DoesNotExist:
            raise ValidationError({
                "message": f"Project with ID '{project_id}' does not exist."
            })