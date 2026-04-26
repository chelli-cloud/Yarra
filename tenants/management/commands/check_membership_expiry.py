from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from tenants.models import School, Profile, Notification
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Check for expiring school memberships and send notifications'

    def handle(self, *args, **options):
        today = timezone.now().date()
        notification_days = [30, 14, 7, 2, 1]
        
        for days in notification_days:
            expiry_date = today + timedelta(days=days)
            expiring_schools = School.objects.filter(membership_expiry=expiry_date, is_active=True)
            
            for school in expiring_schools:
                # Find school leaders or admins to notify
                recipients = Profile.objects.filter(
                    school=school, 
                    role__in=['school_leader', 'admin']
                ).select_related('user')
                
                for profile in recipients:
                    Notification.objects.create(
                        recipient=profile.user,
                        title=f"Membership Expiry Alert: {days} days left",
                        message=f"Your school's membership for {school.name} will expire on {school.membership_expiry}. Please renew to avoid service interruption.",
                        level='warning' if days <= 7 else 'info',
                        target_url='/school-profile/' # Assuming renewal happens here
                    )
                
                self.stdout.write(self.style.SUCCESS(f"Sent {days}-day expiry notification to {school.name}"))

        # Also check for schools that expired today
        expired_schools = School.objects.filter(membership_expiry=today, is_active=True)
        for school in expired_schools:
            school.is_active = False
            school.save()
            
            recipients = Profile.objects.filter(
                school=school, 
                role__in=['school_leader', 'admin']
            ).select_related('user')
            
            for profile in recipients:
                Notification.objects.create(
                    recipient=profile.user,
                    title="Membership Expired",
                    message=f"Your school's membership for {school.name} has expired today. Your access has been suspended.",
                    level='error',
                    target_url='/school-profile/'
                )
            
            self.stdout.write(self.style.WARNING(f"Suspended expired school: {school.name}"))
