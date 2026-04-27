from django.db import models
from tenants.models import School

class SchoolMetric(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='metrics')
    date = models.DateField(auto_now_add=True)
    
    # KPIs
    student_count = models.PositiveIntegerField(default=0)
    teacher_count = models.PositiveIntegerField(default=0)
    competition_registrations = models.PositiveIntegerField(default=0)
    exchange_programs_participated = models.PositiveIntegerField(default=0)
    content_views = models.PositiveIntegerField(default=0)
    vendor_enquiries = models.PositiveIntegerField(default=0)
    
    # Performance score (calculated)
    engagement_score = models.FloatField(default=0.0, help_text="0-100 score based on activity")

    class Meta:
        unique_together = ('school', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.school.name} Metrics - {self.date}"

class ConsortiumMetric(models.Model):
    date = models.DateField(auto_now_add=True)
    
    # Aggregate KPIs
    total_schools = models.PositiveIntegerField(default=0)
    total_students = models.PositiveIntegerField(default=0)
    total_teachers = models.PositiveIntegerField(default=0)
    total_competitions_held = models.PositiveIntegerField(default=0)
    total_exchanges_completed = models.PositiveIntegerField(default=0)
    total_vendor_savings = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    
    # Growth metrics
    new_schools_this_month = models.PositiveIntegerField(default=0)
    active_users_daily = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Consortium Global Metrics - {self.date}"
