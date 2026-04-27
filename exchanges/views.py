from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ExchangeListing, ExchangeApplication, ExchangeMessage, ExchangeType, ExchangeStatus
from tenants.models import Profile, Notification
from tenants.notifications import create_notification

@login_required
def exchange_list(request):
    listings = ExchangeListing.objects.filter(status='open').select_related('school')
    user_school = request.user.profile.school
    
    # Filter by type if provided
    exchange_type = request.GET.get('type')
    if exchange_type:
        listings = listings.filter(type=exchange_type)
        
    return render(request, 'exchanges/exchange_list.html', {
        'listings': listings,
        'types': ExchangeType.choices,
        'selected_type': exchange_type,
        'user_school': user_school
    })

@login_required
def exchange_detail(request, pk):
    listing = get_object_or_404(ExchangeListing, pk=pk)
    user_profile = request.user.profile
    user_school = user_profile.school
    
    # Check if already applied
    existing_application = ExchangeApplication.objects.filter(listing=listing, applicant_school=user_school).first()
    
    if request.method == 'POST' and not existing_application and listing.school != user_school:
        message = request.POST.get('message')
        if message:
            ExchangeApplication.objects.create(
                listing=listing,
                applicant_school=user_school,
                message=message
            )
            messages.success(request, "Your application for the exchange has been submitted.")
            return redirect('exchange_detail', pk=pk)
            
    return render(request, 'exchanges/exchange_detail.html', {
        'listing': listing,
        'existing_application': existing_application,
        'is_own_listing': listing.school == user_school
    })

@login_required
def my_exchanges(request):
    user_school = request.user.profile.school
    my_listings = ExchangeListing.objects.filter(school=user_school)
    my_applications = ExchangeApplication.objects.filter(applicant_school=user_school).select_related('listing', 'listing__school')
    
    return render(request, 'exchanges/my_exchanges.html', {
        'my_listings': my_listings,
        'my_applications': my_applications
    })

@login_required
def application_detail(request, pk):
    application = get_object_or_404(ExchangeApplication, pk=pk)
    user_school = request.user.profile.school
    
    # Only allow listing owner or applicant school to view
    if application.listing.school != user_school and application.applicant_school != user_school:
        messages.error(request, "You do not have permission to view this application.")
        return redirect('my_exchanges')
        
    if request.method == 'POST':
        # Handling status updates (only for listing owner)
        if application.listing.school == user_school:
            new_status = request.POST.get('status')
            if new_status in ['under_review', 'approved', 'rejected']:
                application.status = new_status
                application.save()
                
                # If approved, mark listing as matched
                if new_status == 'approved':
                    application.listing.status = 'matched'
                    application.listing.save()
                    
                    # Notify other applicants (optional, but good UX)
                    other_apps = application.listing.applications.exclude(pk=application.pk)
                    for other_app in other_apps:
                        if other_app.status == 'pending':
                            other_app.status = 'rejected'
                            other_app.save()

                # Notify applicant
                create_notification(
                    recipient=application.applicant_school.profiles.filter(role__in=['admin', 'school_leader']).first().user, # Simplification
                    title='Exchange Application Update',
                    message=f"Your application for {application.listing} has been {new_status}.",
                    level='info',
                    target_url=f"/exchanges/application/{application.pk}/"
                )
                
                messages.success(request, f"Application status updated to {application.get_status_display()}.")
                return redirect('application_detail', pk=pk)
        
        # Handling messaging
        content = request.POST.get('content')
        if content:
            ExchangeMessage.objects.create(
                application=application,
                sender=request.user,
                content=content
            )
            return redirect('application_detail', pk=pk)
            
    return render(request, 'exchanges/application_detail.html', {
        'application': application,
        'messages': application.messages.all().order_by('sent_at'),
        'is_owner': application.listing.school == user_school
    })

@login_required
def create_listing(request):
    if request.user.profile.role not in ['school_leader', 'admin']:
        messages.error(request, "Only school leaders or admins can create exchange listings.")
        return redirect('exchange_list')
        
    if request.method == 'POST':
        ExchangeListing.objects.create(
            school=request.user.profile.school,
            type=request.POST.get('type'),
            subject_grade=request.POST.get('subject_grade'),
            duration=request.POST.get('duration'),
            description=request.POST.get('description'),
            objectives=request.POST.get('objectives', '')
        )
        messages.success(request, "Your exchange listing has been posted.")
        return redirect('my_exchanges')
        
    return render(request, 'exchanges/create_listing.html', {'types': ExchangeType.choices})
