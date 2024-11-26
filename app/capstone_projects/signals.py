from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import CapstoneProjects
from notifications.models import Notifications

@receiver(post_save, sender=CapstoneProjects)
def create_notification(sender, instance: CapstoneProjects, **kwargs):
    for_approval = getattr(instance, '_for_approval', None)
    for_best_project = getattr(instance, '_for_best_project', None)
    
    if for_approval:
        group = instance.capstone_group
        is_approved = instance.is_approved
        
        if is_approved:
            approval_status = "APPROVED"
        else:
            approval_status = "REJECTED"
            
        action = f"{instance.title} by Group#{group.number} of {group.course} - {group.specialization} has been {approval_status.upper()}."
        
        Notifications.objects.create(
            to_group=group,
            action=action
        )
    
    if for_best_project:
        group = instance.capstone_group
        is_best_project = instance.is_best_project
        
        if is_best_project:
            best_project_status = "marked"
        else:
            best_project_status = "removed"
            
        action = f"{instance.title} by Group#{group.number} of {group.course} - {group.specialization} has been {best_project_status} as best project."
        
        Notifications.objects.create(
            to_group=group,
            action=action
        )