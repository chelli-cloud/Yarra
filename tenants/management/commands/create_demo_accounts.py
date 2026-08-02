from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tenants.models import School, Profile

DEMO_PASSWORD = 'test@1234'

ROLE_LABELS = [
    ('school_leader', 'School Leader'),
    ('admin', 'Admin'),
    ('pl_teacher', 'PL Teacher'),
    ('teacher', 'Teacher'),
    ('student', 'Student'),
]


class Command(BaseCommand):
    help = (
        'Creates one dummy account per role under a single "Yarra Demo School", '
        'for the Super Admin role-preview switcher. Safe to rerun -- never '
        'touches existing schools/users.'
    )

    def handle(self, *args, **options):
        school, created = School.objects.get_or_create(
            name='Yarra Demo School',
            defaults={
                'location': 'Demo City',
                'email': 'admin@yarrademoschool.edu',
                'membership_tier': 'premium',
                'is_active': True,
            },
        )
        self.stdout.write(self.style.SUCCESS(
            f"{'Created' if created else 'Using existing'} school: {school.name}"
        ))

        rows = []
        for role, label in ROLE_LABELS:
            username = f'demo_{role}'
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@yarrademoschool.edu',
                    'first_name': 'Demo',
                    'last_name': label,
                },
            )
            if user_created:
                user.set_password(DEMO_PASSWORD)
                user.save()

            Profile.objects.get_or_create(user=user, defaults={'school': school, 'role': role})

            rows.append((label, username))
            self.stdout.write(self.style.SUCCESS(
                f"{'Created' if user_created else 'Already existed'}: {username} ({label})"
            ))

        self.stdout.write('\n--- DEMO LOGIN DETAILS ---')
        self.stdout.write(f'Password for every demo account: {DEMO_PASSWORD}')
        for label, username in rows:
            self.stdout.write(f'{label:15} username={username}')
        self.stdout.write(
            '\nThese are also what the Super Admin "Preview as role" dropdown logs into.'
        )
