from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from tenants.models import School


class EventCategory(models.TextChoices):
    YARRA_ACTION = 'action', 'Yarra Action'
    YARRA_SPOTLIGHT = 'spotlight', 'Yarra Spotlight'
    YARRA_ACTIVE = 'active', 'Yarra Active'
    OPPORTUNITY = 'opportunity', 'Opportunity'


class Event(models.Model):
    """
    Represents a school competition/event in one of three tracks:
    Yarra Action (sports), Yarra Spotlight (arts/culture), Yarra Active (ongoing programs).
    """
    # Events are Yarra-wide (created only by Super Admin); school is now optional context, not ownership.
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EventCategory.choices)

    class FeeType(models.TextChoices):
        PRO_BONO = 'pro_bono', 'Pro Bono (Yarra Members)'
        PAID = 'paid', 'Paid (Non Members)'

    fee_type = models.CharField(max_length=20, choices=FeeType.choices, default=FeeType.PAID)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Registration fee for the event")

    # M6 Requirements
    event_date = models.DateTimeField(null=True, blank=True)
    format = models.CharField(max_length=20, choices=[
        ('in_person', 'In-person'),
        ('virtual', 'Virtual'),
        ('hybrid', 'Hybrid'),
    ], default='virtual')
    speaker_host = models.CharField(max_length=200, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, help_text="Venue or Meeting Link")

    # Actionables
    registration_link = models.URLField(help_text="Google Form URL for registration")
    brochure = models.FileField(upload_to='competitions/brochures/', blank=True, null=True)
    payment_qr = models.FileField(upload_to='competitions/payment_qr/', blank=True, null=True,
                                  help_text="UPI QR code for payment")
    razorpay_payment_link = models.URLField(blank=True, help_text="Razorpay payment page URL (optional)")

    # Post-event data
    winners = models.TextField(blank=True, help_text="Finalist/winner details")
    winning_resources = models.FileField(upload_to='competitions/winners/', blank=True, null=True,
                                         help_text="Photos, PDFs of winning entries")
    recording_url = models.URLField(blank=True, help_text="Link to the event recording")
    presentation_file = models.FileField(upload_to='competitions/presentations/', blank=True, null=True,
                                         help_text="Presentation/slides from the event")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['school', 'is_active']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

    def get_absolute_url(self):
        return reverse('event_detail', args=[self.pk])


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    VERIFIED = 'verified', 'Verified'
    FAILED = 'failed', 'Failed'


class StudentRegistration(models.Model):
    """
    Tracks a participant's registration for an event with payment verification.
    Participants no longer have their own login -- School Admin/Teacher registers
    them by name on the school's behalf, so `school`/`participant_name`/`registered_by`
    are now the source of truth. `student` is kept only for backward compatibility
    with registrations created before self-service student login was removed.
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations', null=True, blank=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='event_registrations', null=True, blank=True)
    participant_name = models.CharField(max_length=150, blank=True)
    registered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='registrations_made')

    # Razorpay payment tracking
    razorpay_payment_id = models.CharField(max_length=50, blank=True)
    razorpay_signature = models.CharField(max_length=200, blank=True)
    razorpay_order_id = models.CharField(max_length=50, blank=True)

    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default='pending')
    payment_screenshot = models.FileField(upload_to='competitions/payment_screenshots/', blank=True, null=True)

    # M6: Attendance & Feedback
    attended = models.BooleanField(default=False)
    feedback_rating = models.PositiveIntegerField(null=True, blank=True, help_text="1-5 rating")
    feedback_text = models.TextField(blank=True)
    certificate_issued = models.BooleanField(default=False)

    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-registered_at']
        indexes = [
            models.Index(fields=['event', 'payment_status']),
            models.Index(fields=['school', 'payment_status']),
        ]

    @property
    def display_name(self):
        return self.participant_name or (self.student.get_full_name() or self.student.username if self.student else 'Participant')

    def __str__(self):
        return f"{self.display_name} - {self.event.title} ({self.payment_status})"


class EventPhoto(models.Model):
    """Photo gallery for an event, separate from `winning_resources` (which is winner-specific)."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='competitions/photos/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Photo for {self.event.title}"


class CompetitionResult(models.Model):
    """
    Records competition results (winners/finalists) for analytics.
    Triggers notification to School Leader when created.
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='results')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='competition_results')
    student_name = models.CharField(max_length=100)
    prize = models.CharField(max_length=50, help_text="e.g., 1st Place, 2nd Place, Runner-up")
    announced_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-announced_at']
        indexes = [
            models.Index(fields=['school', '-announced_at']),
            models.Index(fields=['event', 'school']),
        ]

    def __str__(self):
        return f"{self.student_name} - {self.prize} in {self.event.title}"
