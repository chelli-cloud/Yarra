from django.contrib.auth.models import User
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


def role_preview_context(request):
    """Drives the Super Admin 'preview as role' testing tool: whether the
    switcher should render, and -- if currently previewing -- who to show
    the 'Return to Super Admin' banner for."""
    if not request.user.is_authenticated:
        return {}

    impersonator_id = request.session.get('impersonator_id')
    if not impersonator_id:
        return {'can_switch_role': request.user.is_superuser}

    impersonator = User.objects.filter(pk=impersonator_id, is_superuser=True).first()
    return {
        'can_switch_role': True,
        'is_role_preview': True,
        'role_preview_admin': impersonator,
    }
