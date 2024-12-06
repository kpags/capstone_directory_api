from django.db import models
from users.models import CapstoneGroups
import uuid
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class CapstoneProjects(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    capstone_group = models.ForeignKey(CapstoneGroups, on_delete=models.CASCADE, null=True, blank=True, related_name="groups")
    title = models.TextField()
    ip_registration = models.TextField(null=True, blank=True)
    acm_paper = models.TextField(null=True, blank=True)
    full_document = models.TextField(null=True, blank=True)
    pubmat = models.TextField(null=True, blank=True)
    approval_form = models.TextField(null=True, blank=True)
    source_code = models.TextField(null=True, blank=True)
    members = ArrayField(models.CharField(max_length=500), null=True, blank=True) # When uploading a project from alumni that have no accounts yet
    keywords = ArrayField(models.CharField(max_length=500), null=True, blank=True)
    is_best_project = models.BooleanField(default=False)
    date_published = models.DateField(null=True, blank=True)
    status = models.CharField(null=True, blank=True)
    is_approved = models.CharField(default="pending")
    course = models.CharField(null=True, blank=True, max_length=255)
    specialization = models.CharField(null=True, blank=True, max_length=255)
    
    def __str__(self):
        if self.capstone_group is None:
            return f"{self.title} published on {self.date_published}"
        
        return f"{self.title} - Group {self.capstone_group.name} of {self.capstone_group.academic_year}"
    
    def save(self, *args, **kwargs):
        if self.status:
            self.status = self.status.title()
        
        self.is_approved = self.is_approved.lower()
        
        super(CapstoneProjects, self).save(*args, **kwargs)