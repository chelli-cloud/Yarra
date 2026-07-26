from django import apps
from django import forms
from django.contrib.auth.models import User
from .models import School, Profile, Invitation, SchoolProfileExtended, Payment

class SchoolRegistrationForm(forms.ModelForm):
    admin_email = forms.EmailField(label="Admin Email")
    admin_password = forms.CharField(widget=forms.PasswordInput, label="Admin Password")

    class Meta:
        model = School
        fields = ['name', 'address', 'phone', 'email', 'location', 'contact_person', 'logo']

class SchoolCreateForm(forms.ModelForm):
    """Super Admin's minimal school creation form (name, state/country, Yarra Coordinator)."""

    class Meta:
        model = School
        fields = ['name', 'state', 'country', 'yarra_coordinator_name', 'yarra_coordinator_email', 'yarra_coordinator_phone']

class SchoolProfileExtendedForm(forms.ModelForm):
    class Meta:
        model = SchoolProfileExtended
        exclude = ['school', 'updated_at']

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['school', 'amount', 'method', 'notes', 'receipt']

class InvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['email', 'role']

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
