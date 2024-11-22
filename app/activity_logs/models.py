from django.db import models
from users.models import Users
import uuid

# Create your models here.
class ActivityLogs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True)
    actor_name = models.CharField(max_length=500, null=True, blank=True)
    action = models.TextField()
    
    def __str__(self):
        return f"Activity Log by {self.actor_name} - {self.action} - {self.created_at}"
    
    def save(self, *args, **kwargs):
        if self.user:
            self.actor_name = f"{self.user.first_name} {self.user.last_name}"
        else:
            self.actor_name = "Anonymous User"

        super(ActivityLogs, self).save(*args, **kwargs)
