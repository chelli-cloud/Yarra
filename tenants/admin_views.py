from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, F
from tenants.models import School, Profile, Notification, Payment
from competitions.models import StudentRegistration
from vendors.models import Vendor, VendorPromotion
from cms.models import Comment, ContentItem
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
        'pending_promotions': VendorPromotion.objects.filter(is_approved=False).count(),
    }

    # Revenue = verified event registrations (at each event's own fee) + all manually recorded payments
    registration_revenue = StudentRegistration.objects.filter(
        payment_status='verified'
    ).aggregate(total=Sum('event__fee'))['total'] or 0
    manual_payments_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
    metrics['estimated_revenue'] = registration_revenue + manual_payments_revenue

    # Recent activity
    recent_schools = School.objects.order_by('-id')[:5]
    flagged_notifications = Notification.objects.filter(level='error').order_by('-created_at')[:5]

    # Moderation Queue
    flagged_comments = Comment.objects.filter(is_flagged=True).order_by('-created_at')[:5]
    pending_vendors = Vendor.objects.filter(is_approved=False).order_by('-created_at')[:5]

    return render(request, 'admin/custom_dashboard.html', {
        'metrics': metrics,
        'recent_schools': recent_schools,
        'flagged_notifications': flagged_notifications,
        'flagged_comments': flagged_comments,
        'pending_vendors': pending_vendors,
        'title': 'Super Admin Command Centre'
    })
