from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CompetitionResult
from tenants.models import Profile
from tenants.notifications import create_notification


@receiver(post_save, sender=CompetitionResult)
def notify_school_leader_on_result(sender, instance, created, **kwargs):
    """
    Send notification to School Leader when a competition result is announced.
    This fires only when a new result is created (not on updates).
    """
    if created:
        # Get all School Leaders from the winning school
        sl_profiles = Profile.objects.filter(
            school=instance.school,
            role='school_leader'
        )

        notification_verb = f"Student won {instance.prize} in {instance.event.title}"

        for profile in sl_profiles:
            create_notification(
                recipient=profile.user,
                title='Competition result announced',
                message=notification_verb,
                level='success',
                target_url=instance.event.get_absolute_url(),
                data={
                    'event_id': instance.event.id,
                    'student_name': instance.student_name,
                    'prize': instance.prize,
                },
            )
