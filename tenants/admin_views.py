from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from tenants.models import School, Profile, Notification
from competitions.models import StudentRegistration
from vendors.models import Vendor, VendorPromotion
from django.utils import timezone
from datetime import timedelta

@staff_member_required
def admin_dashboard(request):
    """Custom dashboard for Super Admins with key metrics."""
    today = timezone.now().date()
    next_30_days = today + timedelta(days=30)
    
    metrics = {
        'total_schools': School.objects.count(),
        'active_schools': School.objects.filter(is_active=True).count(),
        'expiring_soon': School.objects.filter(
            membership_expiry__lte=next_30_days, 
            membership_expiry__gte=today,
            is_active=True
        ).count(),
        'total_vendors': Vendor.objects.count(),
        'pending_vendors': Vendor.objects.filter(is_approved=False).count(),
        'total_registrations': StudentRegistration.objects.filter(payment_status='verified').count(),
    }
    
    # Calculate revenue (assuming fixed fee for now as per settings)
    # In a real app, this would come from a Payment model
    from django.conf import settings
    registration_fee = getattr(settings, 'COMPETITION_REGISTRATION_FEE', 500)
    metrics['estimated_revenue'] = metrics['total_registrations'] * registration_fee

    # Recent activity
    recent_schools = School.objects.order_by('-id')[:5]
    flagged_notifications = Notification.objects.filter(level='error').order_by('-created_at')[:5]

    return render(request, 'admin/custom_dashboard.html', {
        'metrics': metrics,
        'recent_schools': recent_schools,
        'flagged_notifications': flagged_notifications,
        'title': 'Super Admin Command Centre'
    })
