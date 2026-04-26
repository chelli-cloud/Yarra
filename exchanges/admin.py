from django.contrib import admin
from .models import ExchangeListing, ExchangeApplication

@admin.register(ExchangeListing)
class ExchangeListingAdmin(admin.ModelAdmin):
    list_display = ('school', 'type', 'subject_grade', 'duration', 'status', 'created_at')
    list_filter = ('type', 'status', 'created_at')
    search_fields = ('school__name', 'subject_grade', 'description')

@admin.register(ExchangeApplication)
class ExchangeApplicationAdmin(admin.ModelAdmin):
    list_display = ('listing', 'applicant_school', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('applicant_school__name', 'listing__school__name', 'message')
    actions = ['approve_applications']

    def approve_applications(self, request, queryset):
        queryset.update(status='approved')
        # Logic to mark listing as matched if approved
        for app in queryset:
            if app.status == 'approved':
                app.listing.status = 'matched'
                app.listing.save()
    approve_applications.short_description = "Approve selected applications and match listings"
