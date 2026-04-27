from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vendor, VendorPromotion, VendorEnquiry, VendorCategory
from .forms import VendorRegistrationForm, VendorPromotionForm, VendorEnquiryForm
from tenants.models import Profile

@login_required
def vendor_list(request):
    """M10: Directory listing with search and filtering."""
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
    """M10: Vendor profile with enquiry form."""
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
            messages.success(request, f"Your enquiry has been sent to {vendor.name}.")
            return redirect('vendor_detail', pk=pk)
            
    return render(request, 'vendors/vendor_detail.html', {
        'vendor': vendor,
        'form': form
    })

@login_required
def vendor_signup(request):
    """M10: Self-registration for vendors."""
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            vendor = form.save(commit=False)
            # Link to user if we want them to manage it later
            vendor.save()
            messages.success(request, "Your registration has been submitted for approval.")
            return redirect('vendor_list')
    else:
        form = VendorRegistrationForm()
    
    return render(request, 'vendors/vendor_signup.html', {'form': form})

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
