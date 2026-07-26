from django.contrib.auth.models import User
from .models import Notification


def create_notification(recipient, title, message, level='info', target_url='', data=None):
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        level=level,
        target_url=target_url,
        data=data or {},
    )


def notify_superadmins(title, message, level='info', target_url=''):
    """Notify every Super Admin (superuser) — any activity on the app triggers a notification here."""
    for admin_user in User.objects.filter(is_superuser=True):
        create_notification(admin_user, title, message, level=level, target_url=target_url)


def log_activity(user, description, school=None, target_url=''):
    """Record an activity for the User Management 'what they have done' view
    and notify Super Admins, per the requirement that any app activity triggers a notification."""
    from .models import ActivityLog

    ActivityLog.objects.create(
        user=user,
        school=school,
        description=description,
        target_url=target_url,
    )
    notify_superadmins(
        title='New activity',
        message=f"{user.username}: {description}",
        level='info',
        target_url=target_url,
    )
