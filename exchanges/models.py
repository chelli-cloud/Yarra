from django.db import models
from tenants.models import School

class ExchangeType(models.TextChoices):
    TEACHER = 'teacher', 'Teacher'
    STUDENT = 'student', 'Student'

class ExchangeStatus(models.TextChoices):
    OPEN = 'open', 'Open'
    MATCHED = 'matched', 'Matched'
    COMPLETED = 'completed', 'Completed'

class ExchangeListing(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='exchange_listings')
    type = models.CharField(max_length=10, choices=ExchangeType.choices)
    subject_grade = models.CharField(max_length=200, help_text="e.g. Mathematics - Grade 10")
    duration = models.CharField(max_length=100, help_text="e.g. 1 week, 1 semester")
    description = models.TextField()
    objectives = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=ExchangeStatus.choices, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} Exchange - {self.school.name} ({self.subject_grade})"

class ExchangeApplication(models.Model):
    APPLICATION_STATUS = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    listing = models.ForeignKey(ExchangeListing, on_delete=models.CASCADE, related_name='applications')
    applicant_school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='exchange_applications')
    message = models.TextField(help_text="Why are you interested in this exchange?")
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application for {self.listing} from {self.applicant_school.name}"

class ExchangeMessage(models.Model):
    application = models.ForeignKey(ExchangeApplication, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} on {self.sent_at}"
