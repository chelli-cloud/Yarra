from django.db import models
from django.contrib.auth.models import User

REVIEW_STATUS_CHOICES = [
    ('not_started', 'Not Started'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
]

class School(models.Model):
    MEMBERSHIP_TIERS = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
    ]

    name = models.CharField(max_length=200, unique=True)
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    contact_person = models.CharField(max_length=150, blank=True)
    key_offerings = models.TextField(blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    # Location (filled by Super Admin at creation)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    # Yarra Coordinator (filled by Super Admin at creation)
    yarra_coordinator_name = models.CharField(max_length=150, blank=True)
    yarra_coordinator_email = models.EmailField(blank=True)
    yarra_coordinator_phone = models.CharField(max_length=20, blank=True)

    # Social / web links
    website = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)

    # Two-stage registration: Super Admin creates the basic record,
    # School Admin completes the rest via SchoolProfileExtended.
    profile_completed = models.BooleanField(default=False)

    # Membership fields
    membership_tier = models.CharField(max_length=20, choices=MEMBERSHIP_TIERS, default='free')
    membership_expiry = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    signed_up_for_early_years = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class SchoolProfileExtended(models.Model):
    """Extended school registration data collected from School Admin after account creation."""
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name='extended_profile')

    year_established = models.PositiveIntegerField(null=True, blank=True)
    district = models.CharField(max_length=150, blank=True)
    association = models.CharField(max_length=200, blank=True, help_text="Association the school is a part of")
    curriculum_adopted = models.CharField(max_length=200, blank=True)
    grades_offered = models.CharField(max_length=200, blank=True)
    total_learners = models.PositiveIntegerField(null=True, blank=True)

    form_filled_by_name = models.CharField(max_length=150, blank=True)
    form_filled_by_designation = models.CharField(max_length=150, blank=True)
    form_filled_by_contact = models.CharField(max_length=20, blank=True)

    parent_demographics = models.TextField(blank=True)
    fee_structure = models.TextField(blank=True)

    principal_name = models.CharField(max_length=150, blank=True)
    principal_contact = models.CharField(max_length=20, blank=True)
    communication_email = models.EmailField(blank=True)

    curriculum_change_reason = models.TextField(blank=True)
    vision_5_years = models.TextField(blank=True)
    success_definition = models.TextField(blank=True)
    curriculum_expectations = models.TextField(blank=True)

    built_up_area = models.CharField(max_length=100, blank=True)
    classroom_infrastructure = models.TextField(blank=True)
    pd_programs_impact = models.TextField(blank=True)
    immediate_support_needed = models.TextField(blank=True)

    curriculum_planning_description = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Extended profile - {self.school.name}"


class SchoolDocument(models.Model):
    """Curriculum planning documents uploaded as part of the extended school profile (max 10)."""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='school_documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.school.name} - {self.file.name}"


class Payment(models.Model):
    METHOD_CHOICES = [
        ('online', 'Online'),
        ('cheque', 'Cheque'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='online')
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    receipt = models.FileField(upload_to='payment_receipts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.school.name} - {self.amount} ({self.method})"


class ActivityLog(models.Model):
    """Records user activity for the User Management 'what they have done' view
    and to drive Super Admin notifications on any app activity."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    description = models.CharField(max_length=255)
    target_url = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['school', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.description}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='profiles')
    role = models.CharField(max_length=20, choices=[
        ('school_leader', 'School Leader'),
        ('admin', 'Admin'),
        ('pl_teacher', 'PL Teacher'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ])
    
    # Profile Customization
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Basic Information (from images)
    date_of_birth = models.DateField(null=True, blank=True)
    mobile_no = models.CharField(max_length=15, blank=True)
    alternate_mobile_no = models.CharField(max_length=15, blank=True)
    emergency_contact_no = models.CharField(max_length=15, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    nationality = models.CharField(max_length=50, default='Indian')
    religion = models.CharField(max_length=50, blank=True)
    category = models.CharField(max_length=50, blank=True, help_text="e.g. BC, MBC, General")
    
    # Other Information
    aadhaar_no = models.CharField(max_length=12, blank=True)
    pan_no = models.CharField(max_length=10, blank=True)
    languages_known = models.CharField(max_length=200, blank=True)
    extra_curricular = models.TextField(blank=True)
    
    # Academic Context
    campus = models.CharField(max_length=100, blank=True)
    grade = models.CharField(max_length=50, blank=True, help_text="e.g. Grade 10")
    section = models.CharField(max_length=50, blank=True, help_text="e.g. Section A")
    admission_date = models.DateField(null=True, blank=True)
    
    # Address
    permanent_address = models.TextField(blank=True)
    current_address = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['school', 'role']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.school.name} - {self.role}"

class ReviewCycle(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='review_cycles')
    title = models.CharField(max_length=150, default='Current Review Cycle')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    self_study_status = models.CharField(max_length=20, choices=REVIEW_STATUS_CHOICES, default='not_started')
    self_study_start = models.DateField(null=True, blank=True)
    self_study_end = models.DateField(null=True, blank=True)
    self_study_document = models.FileField(upload_to='review_documents/self_study/', null=True, blank=True)

    review_visit_status = models.CharField(max_length=20, choices=REVIEW_STATUS_CHOICES, default='not_started')
    review_visit_start = models.DateField(null=True, blank=True)
    review_visit_end = models.DateField(null=True, blank=True)
    review_visit_document = models.FileField(upload_to='review_documents/review_visit/', null=True, blank=True)

    sip_status = models.CharField(max_length=20, choices=REVIEW_STATUS_CHOICES, default='not_started')
    sip_start = models.DateField(null=True, blank=True)
    sip_end = models.DateField(null=True, blank=True)
    sip_document = models.FileField(upload_to='review_documents/sip/', null=True, blank=True)

    recommendations_status = models.CharField(max_length=20, choices=REVIEW_STATUS_CHOICES, default='not_started')
    recommendations_start = models.DateField(null=True, blank=True)
    recommendations_end = models.DateField(null=True, blank=True)
    recommendations_document = models.FileField(upload_to='review_documents/recommendations/', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.school.name} - {self.title}"


class TeacherResource(models.Model):
    RESOURCE_TYPES = [
        ('session', 'Upcoming PL Session'),
        ('recording', 'Past Recording'),
        ('document', 'Resource Document'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='teacher_resources')
    title = models.CharField(max_length=150)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='document')
    
    # Session/Recording specific fields
    presenter = models.CharField(max_length=100, blank=True)
    session_date = models.DateField(null=True, blank=True)
    session_time = models.TimeField(null=True, blank=True)
    duration = models.CharField(max_length=50, blank=True, help_text="e.g. 1h 20m")
    
    # Capacity for sessions
    capacity_max = models.PositiveIntegerField(null=True, blank=True)
    capacity_current = models.PositiveIntegerField(default=0)

    # Links and files
    meeting_link = models.URLField(blank=True, null=True)
    registration_gform = models.URLField(blank=True, null=True)
    uploaded_file = models.FileField(upload_to='teacher_hub/resources/', blank=True, null=True)
    
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_resource_type_display()}] {self.title}"


class DiscussionThread(models.Model):
    title = models.CharField(max_length=200)
    key_takeaways = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussion_threads')
    created_at = models.DateTimeField(auto_now_add=True)
    is_locked = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ThreadReply(models.Model):
    thread = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thread_replies')
    content = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['posted_at']

    def __str__(self):
        return f"Reply by {self.author.username} on {self.thread.title}"


class Notification(models.Model):
    LEVEL_CHOICES = [
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=160)
    message = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='info')
    target_url = models.CharField(max_length=255, blank=True)
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['recipient', '-created_at']),
        ]

    def __str__(self):
        return f"{self.recipient.username}: {self.title}"


class Invitation(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=[
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ])
    token = models.CharField(max_length=100, unique=True)
    is_used = models.BooleanField(default=False)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invite for {self.email} to join {self.school.name} as {self.role}"
