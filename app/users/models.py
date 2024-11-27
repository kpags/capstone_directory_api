from django.db import models
import uuid, os
from django.contrib.auth.hashers import (
    make_password,
)


# Create your models here.
class CapstoneGroups(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField()
    academic_year = models.CharField(max_length=255)
    course = models.CharField(null=True, blank=True)
    specialization = models.CharField(null=True, blank=True)

    def __str__(self):
        return f"Group #{self.name} of S.Y {self.academic_year}"

    
class Users(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255)
    student_number = models.CharField(null=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField()
    role = models.CharField(
        max_length=200, default="student"
    )  # Student, Administrator, Faculty, Capstone Coordinator etc.
    course = models.CharField(null=True, blank=True)
    specialization = models.CharField(null=True, blank=True)
    group = models.ForeignKey(
        CapstoneGroups,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="group_members",
    )
    is_active = models.BooleanField(default=True)
    token=models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.title()
        self.middle_name = (
            self.middle_name.title() if self.middle_name else self.middle_name
        )
        self.last_name = self.last_name.title()
        self.email = self.email.lower()
        self.role = self.role.lower()

        hash_prefix = os.getenv("ALLOWED_HASHED_PREFIX")

        if not self.password.startswith(hash_prefix):
            self.password = make_password(self.password)

        super(Users, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} - {self.role}"
    
    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(
        Users, on_delete=models.CASCADE, related_name="user_profile"
    )
    birthdate = models.DateField(null=True, blank=True)
    age = models.BigIntegerField(default=0)
    sex = models.CharField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    # profile_picture = models.ImageField(null=True, blank=True)
    emergency_contacts = models.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        sex = self.sex

        if sex:
            if sex.lower() in ["male", "m"]:
                self.sex = "Male"
            elif sex.lower() in ["female", "f"]:
                self.sex = "Female"

        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email}'s User Profile"

class TechnicalAdvisorGroups(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    group = models.ForeignKey(CapstoneGroups, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Group {self.group.name} of {self.group.academic_year}"