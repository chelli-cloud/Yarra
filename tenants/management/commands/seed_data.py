import random
import re
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from tenants.models import School, Profile, DiscussionThread, ThreadReply
from competitions.models import Event, EventCategory, CompetitionResult

SEED_USERNAME_PATTERN = re.compile(r'^(school_leader|admin|pl_teacher|teacher|student)_\d+$')
# NOTE: 'student' stays in the pattern (not the roles list below) so reruns still clean up
# any leftover student_<id> accounts created before self-service student login was removed.

class Command(BaseCommand):
    help = 'Seed the database with 10 schools and comprehensive sample data'

    def handle(self, *args, **options):
        # Configure Site
        Site.objects.update_or_create(
            id=settings.SITE_ID,
            defaults={'domain': 'yarra.pythonanywhere.com', 'name': 'Yaara Consortium'}
        )

        # Clear existing data to avoid duplicates. Matches by username pattern rather than
        # is_superuser=False, since the seeded 'admin_<id>' accounts are themselves superusers
        # and would otherwise survive a rerun as orphaned, profile-less users once their old
        # school (and thus profile) gets cascade-deleted below.
        self.stdout.write("Clearing existing sample data...")
        School.objects.all().delete()
        stale_user_ids = [u.pk for u in User.objects.all() if SEED_USERNAME_PATTERN.match(u.username)]
        User.objects.filter(pk__in=stale_user_ids).delete()

        schools_data = [
            ("Akshar Arbol International", "Chennai, TN", "IB & IGCSE, Arts, Sports"),
            ("Riverdale Academy", "Bangalore, KA", "CBSE, STEM, Football Academy"),
            ("Greenwood High", "Hyderabad, TS", "ICSE, Drama, Cricket"),
            ("Oakridge International", "Mumbai, MH", "IB, Robotics, Swimming"),
            ("The Heritage School", "Delhi, NCR", "Experiential Learning, Music"),
            ("Silver Oaks School", "Pune, MH", "CBSE, Character Building, Yoga"),
            ("Bishop Cotton", "Shimla, HP", "Residential, Traditional, Hockey"),
            ("Mayo College", "Ajmer, RJ", "Heritage, Equestrian, Arts"),
            ("The Doon School", "Dehradun, UK", "Leadership, Social Service, Trekking"),
            ("St. Paul's School", "Darjeeling, WB", "Classic Education, Choir, Nature"),
        ]

        roles = ['school_leader', 'admin', 'pl_teacher', 'teacher']
        
        for name, loc, offerings in schools_data:
            school = School.objects.create(
                name=name,
                location=loc,
                key_offerings=offerings,
                address=f"123 Educational Lane, {loc}",
                phone=f"044-{random.randint(2000000, 9999999)}",
                email=f"info@{name.lower().replace(' ', '')}.edu"
            )
            self.stdout.write(f"Created School: {name}")

            # Create users for each school
            users = []
            for role in roles:
                username = f"{role}_{school.pk}"
                is_staff = (role == 'admin')
                is_superuser = (role == 'admin')
                user = User.objects.create(
                    username=username,
                    email=f"{username}@yarra.edu",
                    first_name=name.split()[0],
                    last_name=role.replace('_', ' ').title(),
                    is_staff=is_staff,
                    is_superuser=is_superuser
                )
                user.set_password('test@1234')
                user.save()
                
                profile = Profile.objects.create(
                    user=user,
                    school=school,
                    role=role,
                )
                users.append(user)

            # Create Events for each school
            staff_user = User.objects.get(username=f"teacher_{school.pk}")

            # 3 Events
            comp_types = [EventCategory.YARRA_ACTION, EventCategory.YARRA_SPOTLIGHT, EventCategory.YARRA_ACTIVE]
            for i, cat in enumerate(comp_types):
                event = Event.objects.create(
                    school=school,
                    created_by=staff_user,
                    title=f"{school.name} {cat.label} 2026",
                    description=f"Annual {cat.label} event featuring various activities and talent showcases for our students.",
                    category=cat,
                    registration_link="https://forms.gle/sample",
                    is_active=True
                )
                
                # Add some results for the first event
                if i == 0:
                    CompetitionResult.objects.create(
                        event=event,
                        school=school,
                        student_name="Arjun Kumar",
                        prize="1st Place"
                    )
                    CompetitionResult.objects.create(
                        event=event,
                        school=school,
                        student_name="Sanya Malhotra",
                        prize="Runner-up"
                    )

            # Leadership Discussions (only for first few schools to keep it manageable)
            if school.pk <= 3:
                leader_user = User.objects.get(username=f"school_leader_{school.pk}")
                thread = DiscussionThread.objects.create(
                    title=f"Policy Discussion: Future of {school.name}",
                    created_by=leader_user
                )
                ThreadReply.objects.create(
                    thread=thread,
                    author=leader_user,
                    content="I believe we should focus more on digital integration this year."
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded 10 schools with complete data!'))
        self.stdout.write('\n--- LOGIN DETAILS ---')
        self.stdout.write('Password for all users: test@1234')
        self.stdout.write('\nFormat: [role]_[school_id]')
        self.stdout.write('Roles: school_leader, admin, pl_teacher, teacher')
        self.stdout.write('Example: teacher_1 (School 1), admin_2 (School 2), etc.')
