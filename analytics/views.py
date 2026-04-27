from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, Count, Avg
from tenants.models import School, Profile
from competitions.models import StudentRegistration, Event
from exchanges.models import ExchangeListing, ExchangeApplication
from vendors.models import Vendor, VendorEnquiry
from .models import ConsortiumMetric, SchoolMetric

def is_super_admin(user):
    return user.is_authenticated and (user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'admin'))

@user_passes_test(is_super_admin)
def consortium_dashboard(request):
    """M13: Super Admin Dashboard for Consortium-wide metrics."""
    
    # Current Stats
    total_schools = School.objects.count()
    total_students = Profile.objects.filter(role='student').count()
    total_teachers = Profile.objects.filter(role='teacher').count()
    
    # Competition Stats
    total_events = Event.objects.count()
    total_registrations = StudentRegistration.objects.count()
    
    # Exchange Stats
    total_exchanges = ExchangeListing.objects.count()
    matched_exchanges = ExchangeListing.objects.filter(status='matched').count()
    
    # Vendor Stats
    total_vendors = Vendor.objects.filter(is_approved=True).count()
    total_enquiries = VendorEnquiry.objects.count()
    
    # School Performance Ranking
    school_ranking = School.objects.annotate(
        reg_count=Count('registrations', distinct=True),
        enquiry_count=Count('vendorenquiry', distinct=True),
        listing_count=Count('exchange_listings', distinct=True)
    ).order_by('-reg_count')[:10]

    context = {
        'total_schools': total_schools,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_events': total_events,
        'total_registrations': total_registrations,
        'total_exchanges': total_exchanges,
        'matched_exchanges': matched_exchanges,
        'total_vendors': total_vendors,
        'total_enquiries': total_enquiries,
        'school_ranking': school_ranking,
    }
    
    return render(request, 'analytics/dashboard.html', context)
