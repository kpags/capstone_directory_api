from django.db import models
import uuid
from users.models import Users, CapstoneGroups

# Create your models here.
class Notifications(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    to_group = models.ForeignKey(CapstoneGroups, on_delete=models.CASCADE, null=True, blank=True)
    to_user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, blank=True, related_name="notified_to")
    action = models.TextField()
    
    def __str__(self):
        return self.action
    
class NotificationRead(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    reader = models.ForeignKey(Users, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notifications, on_delete=models.CASCADE)
    