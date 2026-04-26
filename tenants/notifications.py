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
