from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tenants.models import School, Profile

class Command(BaseCommand):
    help = 'Seeds 10 schools and their leader accounts'

    def handle(self, *args, **kwargs):
        password = 'Password123!'
        schools_data = [
            ('Oakridge International', 'oakridge'),
            ('Greenwood High', 'greenwood'),
            ('Silver Oaks', 'silveroaks'),
            ('The Heritage School', 'heritage'),
            ('Delhi Public School', 'dps'),
            ('The Doon School', 'doon'),
            ('Mayo College', 'mayo'),
            ('Scindia School', 'scindia'),
            ('Welham Girls', 'welham'),
            ('Bishop Cotton', 'bishop'),
        ]

        for name, slug in schools_data:
            school, created = School.objects.get_or_create(
                name=name,
                defaults={
                    'location': f'{name} City',
                    'email': f'admin@{slug}.edu',
                    'membership_tier': 'premium'
                }
            )
            
            username = f'{slug}_admin'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'admin@{slug}.edu',
                }
            )
            
            user.set_password(password)
            user.save()
            
            Profile.objects.get_or_create(
                user=user,
                defaults={
                    'school': school,
                    'role': 'school_leader'
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created school {name} and user {username}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated password for user {username}'))

        self.stdout.write(self.style.SUCCESS('Successfully seeded 10 schools. Default password: Password123!'))
