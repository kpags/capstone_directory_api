from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import Users
from notifications.models import Notifications

@receiver(post_save, sender=Users)
def create_notification(sender, instance: Users, **kwargs):
    group = getattr(instance, 'group', None)
    role = getattr(instance, 'role', None)
        
    full_name = f"{instance.first_name} {instance.last_name}"
    
    if group:
        action = f"{full_name} has been added to Group#{group.name} of {group.course} - {group.specialization}."
        
        Notifications.objects.create(
            to_group=group,
            action=action
        )
    
    if role:
        if role.lower() in ["coordinator", "capstone coordinator", "faculty"]:
            action = f"{full_name} role has been changed to {role.upper()}."
        
            Notifications.objects.create(
                to_user=instance,
                action=action
            )