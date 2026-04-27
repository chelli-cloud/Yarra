from django import apps
from django import forms
from django.contrib.auth.models import User
from .models import School, Profile, Invitation

class SchoolRegistrationForm(forms.ModelForm):
    admin_email = forms.EmailField(label="Admin Email")
    admin_password = forms.CharField(widget=forms.PasswordInput, label="Admin Password")

    class Meta:
        model = School
        fields = ['name', 'address', 'phone', 'email', 'location', 'contact_person', 'logo']

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
