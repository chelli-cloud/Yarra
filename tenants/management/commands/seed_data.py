import random
import os
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from tenants.models import School, Profile, TeacherResource, DiscussionThread, ThreadReply
from competitions.models import Event, EventCategory, CompetitionResult

class Command(BaseCommand):
    help = 'Seed the database with 10 schools and comprehensive sample data'

    def handle(self, *args, **options):
        # Configure Site
        Site.objects.update_or_create(
            id=settings.SITE_ID,
            defaults={'domain': 'yarra.pythonanywhere.com', 'name': 'Yaara Consortium'}
        )

        # Create media directories if they don't exist
        resources_path = os.path.join(settings.MEDIA_ROOT, 'teacher_hub', 'resources')
        os.makedirs(resources_path, exist_ok=True)
        
        # Create dummy files for resources
        dummy_pdf = os.path.join(resources_path, 'curriculum_plan_2026.pdf')
        dummy_excel = os.path.join(resources_path, 'student_marks_template.xlsx')
        
        with open(dummy_pdf, 'w') as f: f.write('Sample PDF content for Yarra Teachers Hub.')
        with open(dummy_excel, 'w') as f: f.write('Sample Excel content for Yarra Teachers Hub.')

        # Clear existing data to avoid duplicates (except superusers if any)
        self.stdout.write("Clearing existing sample data...")
        School.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

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

        roles = ['school_leader', 'admin', 'pl_teacher', 'teacher', 'student']
        
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
                    date_of_birth="2005-02-18",
                    mobile_no="7305774555",
                    campus="Main Campus",
                    grade="Grade 10",
                    section="A",
                    admission_date="2023-07-01",
                    permanent_address="No 30a, Thirumurthy Street, Tnagar, Chennai-600017",
                    current_address="No 30a, Thirumurthy Street, Tnagar, Chennai-600017",
                )
                users.append(user)

            # Create Events & Opportunities for each school
            staff_user = User.objects.get(username=f"teacher_{school.pk}")
            
            # 3 Competitions
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

            # 2 Opportunities
            for i in range(2):
                Event.objects.create(
                    school=school,
                    created_by=staff_user,
                    title=f"Opportunity: {['Global Scholarship', 'Summer Internship'][i]}",
                    description=f"Exciting opportunity for {school.name} students to excel in their chosen fields with external partners.",
                    category=EventCategory.OPPORTUNITY,
                    registration_link="https://forms.gle/opportunity",
                    is_active=True
                )

            # Teacher Resources (Categorized)
            # 1. Upcoming Sessions
            TeacherResource.objects.create(
                school=school,
                title="STEM Innovation in the Classroom",
                resource_type='session',
                presenter="Dr. Li Chen",
                session_date="2026-05-03",
                session_time="10:00:00",
                capacity_max=40,
                capacity_current=25,
                meeting_link="https://meet.google.com/abc-defg-hij",
                registration_gform="https://forms.gle/staff",
                uploaded_by=staff_user
            )
            TeacherResource.objects.create(
                school=school,
                title="Differentiated Learning Strategies",
                resource_type='session',
                presenter="Prof. Emma Taylor",
                session_date="2026-05-17",
                session_time="14:00:00",
                capacity_max=30,
                capacity_current=12,
                meeting_link="https://meet.google.com/abc-defg-hij",
                registration_gform="https://forms.gle/staff",
                uploaded_by=staff_user
            )

            # 2. Past Recordings
            recordings_data = [
                ("Inquiry-Based Learning Workshop", "2026-03-15", "1h 20m"),
                ("Student Wellbeing Frameworks", "2026-02-22", "55m"),
                ("Data-Driven Instruction", "2026-01-18", "1h 05m"),
            ]
            for title, date, dur in recordings_data:
                TeacherResource.objects.create(
                    school=school,
                    title=title,
                    resource_type='recording',
                    session_date=date,
                    duration=dur,
                    meeting_link="https://youtube.com/sample-recording",
                    uploaded_by=staff_user
                )

            # 3. Resources (Documents)
            resource_files = [
                ("PL Planning Template", "DOCX", "245 KB", dummy_pdf),
                ("Student Assessment Rubric Pack", "PDF", "1.2 MB", dummy_pdf),
                ("Classroom Observation Checklist", "PDF", "380 KB", dummy_pdf),
                ("Curriculum Guide", "XLSX", "4.5 MB", dummy_excel),
            ]
            for title, ftype, size, dummy_path in resource_files:
                res = TeacherResource.objects.create(
                    school=school,
                    title=title,
                    resource_type='document',
                    duration=size, # using duration field for size display in UI
                    uploaded_by=staff_user
                )
                with open(dummy_path, 'rb') as f:
                    # Append correct extension for UI logic
                    ext = ftype.lower()
                    res.uploaded_file.save(f"{title.lower().replace(' ', '_')}.{ext}", File(f), save=True)

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
        self.stdout.write('Roles: school_leader, admin, pl_teacher, teacher, student')
        self.stdout.write('Example: student_1 (School 1), teacher_2 (School 2), etc.')
