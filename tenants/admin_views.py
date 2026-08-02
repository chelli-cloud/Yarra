import csv

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, F
from django.http import HttpResponse
from tenants.models import School, Profile, Notification, Payment
from tenants.notifications import create_notification
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


@staff_member_required
def export_schools_csv(request):
    """M4: CSV export of every school."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="schools.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Location', 'State', 'Country', 'Membership Tier', 'Active', 'Membership Expiry', 'Email', 'Yarra Coordinator Email'])
    for school in School.objects.all().order_by('name'):
        writer.writerow([
            school.name, school.location, school.state, school.country,
            school.get_membership_tier_display(), school.is_active,
            school.membership_expiry or '', school.email, school.yarra_coordinator_email,
        ])
    return response


@staff_member_required
def export_payments_csv(request):
    """M4: CSV export of every manually recorded payment."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payments.csv"'
    writer = csv.writer(response)
    writer.writerow(['School', 'Amount', 'Method', 'Recorded By', 'Notes', 'Date'])
    for payment in Payment.objects.select_related('school', 'recorded_by').order_by('-created_at'):
        writer.writerow([
            payment.school.name, payment.amount, payment.get_method_display(),
            payment.recorded_by.username if payment.recorded_by else '',
            payment.notes, payment.created_at.strftime('%Y-%m-%d %H:%M'),
        ])
    return response


@staff_member_required
def export_vendors_csv(request):
    """M4: CSV export of every vendor."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="vendors.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Category', 'Contact Email', 'Contact Phone', 'Approved', 'Vetted', 'Created'])
    for vendor in Vendor.objects.all().order_by('name'):
        writer.writerow([
            vendor.name, vendor.get_category_display(), vendor.contact_email, vendor.contact_phone,
            vendor.is_approved, vendor.is_vetted, vendor.created_at.strftime('%Y-%m-%d'),
        ])
    return response


@staff_member_required
def broadcast_announcement(request):
    """M4/M12: Super Admin sends an announcement to all schools, or a membership-tier segment."""
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        tier = request.POST.get('tier')

        if not title or not message:
            messages.error(request, "Title and message are required.")
            return redirect('broadcast_announcement')

        profiles = Profile.objects.select_related('user', 'school')
        if tier:
            profiles = profiles.filter(school__membership_tier=tier)

        recipients = {p.user for p in profiles}
        for user in recipients:
            create_notification(
                recipient=user,
                title=title,
                message=message,
                level='info',
            )
        messages.success(request, f"Announcement sent to {len(recipients)} user(s).")
        return redirect('admin_dashboard')

    return render(request, 'admin/broadcast_announcement.html', {
        'tier_choices': School.MEMBERSHIP_TIERS,
    })
