from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vendor, VendorPromotion, VendorEnquiry, VendorCategory, EventInterest
from .forms import VendorRegistrationForm, VendorPromotionForm, VendorEnquiryForm, EventInterestForm
from tenants.models import Profile
from tenants.notifications import log_activity, notify_superadmins
from competitions.models import Event

@login_required
def vendor_list(request):
    """M10: Directory listing with search and filtering. Students don't have marketplace access."""
    profile = Profile.objects.filter(user=request.user).first()
    if profile and profile.role == 'student':
        return render(request, 'tenants/access_denied.html', {
            'message': 'The Vendor Marketplace is not available to students.'
        }, status=403)

    category = request.GET.get('category')
    query = request.GET.get('q')
    
    vendors = Vendor.objects.filter(is_approved=True)
    
    if category:
        vendors = vendors.filter(category=category)
    
    if query:
        vendors = vendors.filter(name__icontains=query)
    
    promotions = VendorPromotion.objects.filter(is_approved=True, placement='directory')
    
    return render(request, 'vendors/vendor_list.html', {
        'vendors': vendors,
        'categories': VendorCategory.choices,
        'promotions': promotions,
        'selected_category': category,
        'query': query
    })

@login_required
def vendor_detail(request, pk):
    """M10: Vendor profile with enquiry form. Students don't have marketplace access."""
    profile = Profile.objects.filter(user=request.user).first()
    if profile and profile.role == 'student':
        return render(request, 'tenants/access_denied.html', {
            'message': 'The Vendor Marketplace is not available to students.'
        }, status=403)

    vendor = get_object_or_404(Vendor, pk=pk, is_approved=True)
    form = VendorEnquiryForm()
    
    if request.method == 'POST':
        form = VendorEnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save(commit=False)
            enquiry.vendor = vendor
            enquiry.user = request.user
            enquiry.school = request.user.profile.school
            enquiry.save()
            log_activity(request.user, f"Sent enquiry to vendor '{vendor.name}'", school=enquiry.school)
            messages.success(request, f"Your enquiry has been sent to {vendor.name}.")
            return redirect('vendor_detail', pk=pk)
            
    return render(request, 'vendors/vendor_detail.html', {
        'vendor': vendor,
        'form': form
    })

@login_required
def vendor_signup(request):
    """M10: Self-registration for vendors. Students don't have marketplace access."""
    profile = Profile.objects.filter(user=request.user).first()
    if profile and profile.role == 'student':
        return render(request, 'tenants/access_denied.html', {
            'message': 'The Vendor Marketplace is not available to students.'
        }, status=403)

    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            vendor = form.save(commit=False)
            # Link to user if we want them to manage it later
            vendor.save()
            log_activity(request.user, f"Vendor '{vendor.name}' signed up, pending approval")
            messages.success(request, "Your registration has been submitted for approval.")
            return redirect('vendor_list')
    else:
        form = VendorRegistrationForm()
    
    return render(request, 'vendors/vendor_signup.html', {'form': form})

@login_required
def my_requests(request):
    """M10: 'Requests' tab — the school's own enquiries sent to vendors, with status.
    Students don't have marketplace access."""
    profile = Profile.objects.filter(user=request.user).first()
    if profile and profile.role == 'student':
        return render(request, 'tenants/access_denied.html', {
            'message': 'The Vendor Marketplace is not available to students.'
        }, status=403)

    school = request.user.profile.school
    enquiries = VendorEnquiry.objects.filter(school=school).select_related('vendor').order_by('-created_at')
    return render(request, 'vendors/my_requests.html', {'enquiries': enquiries})


@login_required
def event_interest_submit(request, event_pk):
    """Vendor applies to be part of an upcoming Yarra event; Super Admin is notified.
    Students don't have marketplace access."""
    profile = Profile.objects.filter(user=request.user).first()
    if profile and profile.role == 'student':
        return render(request, 'tenants/access_denied.html', {
            'message': 'The Vendor Marketplace is not available to students.'
        }, status=403)

    event = get_object_or_404(Event, pk=event_pk)
    approved_vendors = Vendor.objects.filter(is_approved=True).order_by('name')

    if request.method == 'POST':
        vendor = get_object_or_404(Vendor, pk=request.POST.get('vendor'), is_approved=True)
        form = EventInterestForm(request.POST)
        if form.is_valid():
            interest = form.save(commit=False)
            interest.vendor = vendor
            interest.event = event
            interest.submitted_by = request.user
            interest.save()
            notify_superadmins(
                title='Vendor event interest',
                message=f"{vendor.name} marked interest in participating in '{event.title}'.",
                target_url=event.get_absolute_url(),
            )
            log_activity(request.user, f"Vendor '{vendor.name}' applied for event '{event.title}'")
            messages.success(request, f"Your interest in {event.title} has been submitted.")
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventInterestForm()

    return render(request, 'vendors/event_interest_form.html', {
        'form': form, 'event': event, 'approved_vendors': approved_vendors,
    })


@login_required
def vendor_promotion_create(request, vendor_id):
    """M11: Create a promotion campaign."""
    vendor = get_object_or_404(Vendor, pk=vendor_id)
    # Check if user has permission to manage this vendor (omitted for brevity)
    
    if request.method == 'POST':
        form = VendorPromotionForm(request.POST, request.FILES)
        if form.is_valid():
            promotion = form.save(commit=False)
            promotion.vendor = vendor
            promotion.save()
            messages.success(request, "Promotion submitted for review.")
            return redirect('vendor_detail', pk=vendor_id)
    else:
        form = VendorPromotionForm()
        
    return render(request, 'vendors/promotion_form.html', {
        'form': form,
        'vendor': vendor
    })
