from django import forms
from .models import Vendor, VendorPromotion, VendorEnquiry, EventInterest

class VendorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = [
            'name', 'category', 'description', 'website',
            'contact_email', 'contact_phone', 'logo', 'brochure', 'catalog',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class VendorPromotionForm(forms.ModelForm):
    class Meta:
        model = VendorPromotion
        fields = [
            'title', 'offer_text', 'banner_image', 'cta_link', 
            'placement', 'start_date', 'end_date'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class VendorEnquiryForm(forms.ModelForm):
    class Meta:
        model = VendorEnquiry
        fields = ['subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }

class EventInterestForm(forms.ModelForm):
    class Meta:
        model = EventInterest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }
