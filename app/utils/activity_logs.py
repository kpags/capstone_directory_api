from activity_logs.models import ActivityLogs
from users.models import Users

def create_activity_log(actor: Users, action):
    ActivityLogs.objects.create(
        user=actor,
        action=action
    )