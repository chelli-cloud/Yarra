from .models import Notification, Profile


def notification_context(request):
    if not request.user.is_authenticated:
        return {
            'recent_notifications': [],
            'unread_notification_count': 0,
        }

    notifications = Notification.objects.filter(recipient=request.user)
    return {
        'recent_notifications': notifications[:5],
        'unread_notification_count': notifications.filter(is_read=False).count(),
    }


def school_context(request):
    """Provide the current user's school and profile to all templates."""
    if not request.user.is_authenticated:
        return {}

    profile = Profile.objects.filter(user=request.user).select_related('school').first()
    if not profile:
        return {}

    return {
        'user_profile': profile,
        'user_school': profile.school,
    }
