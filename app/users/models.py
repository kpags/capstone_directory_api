from django.db import models
import uuid
from django.contrib.auth.hashers import (
    make_password,
)

# Create your models here.
class CapstoneGroups(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    number = models.CharField()
    academic_year = models.CharField(max_length=255)

    def __str__(self):
        return f"Group #{self.number} of S.Y {self.academic_year}"


class Users(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255)
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
        related_name="capstone_group",
    )
    advisory_group = models.ForeignKey(
        CapstoneGroups,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="group_technical_advisor",  # For Faculty/Coordinator only
    )
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.title()
        self.middle_name = (
            self.middle_name.title() if self.middle_name else self.middle_name
        )
        self.last_name = self.last_name.title()
        self.email = self.email.lower()
        self.role = self.role.lower()
        self.password = make_password(self.password)

        super(Users, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} - {self.role}"


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
