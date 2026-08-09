from django.contrib import admin
from .models import Event, EventCategory, StudentRegistration, PaymentStatus, CompetitionResult, EventPhoto


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'school', 'created_by', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'school')
    search_fields = ('title', 'description', 'school__name')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'category', 'school', 'created_by')
        }),
        ('Registration', {
            'fields': ('registration_link', 'razorpay_payment_link')
        }),
        ('Files', {
            'fields': ('brochure', 'payment_qr')
        }),
        ('Results', {
            'fields': ('winners', 'winning_resources')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StudentRegistration)
class StudentRegistrationAdmin(admin.ModelAdmin):
    list_display = ('participant_name', 'school', 'event', 'payment_status', 'registered_at')
    list_filter = ('payment_status', 'event')
    search_fields = ('participant_name', 'student__username', 'event__title', 'razorpay_payment_id')
    readonly_fields = ('registered_at',)


@admin.register(EventPhoto)
class EventPhotoAdmin(admin.ModelAdmin):
    list_display = ('event', 'caption', 'uploaded_at')
    list_filter = ('event',)


@admin.register(CompetitionResult)
class CompetitionResultAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'prize', 'event', 'school', 'announced_at')
    list_filter = ('school', 'event')
    search_fields = ('student_name', 'prize', 'event__title', 'school__name')
    readonly_fields = ('announced_at',)
