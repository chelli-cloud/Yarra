from django import apps
from django import forms
from django.contrib.auth.models import User
from .models import School, Profile, Invitation, SchoolProfileExtended, Payment, GRADE_LEVELS

class SchoolRegistrationForm(forms.ModelForm):
    admin_email = forms.EmailField(label="Admin Email")
    admin_password = forms.CharField(widget=forms.PasswordInput, label="Admin Password")

    class Meta:
        model = School
        fields = ['name', 'address', 'phone', 'email', 'location', 'contact_person', 'logo']

class SchoolCreateForm(forms.ModelForm):
    """Super Admin's minimal school creation form (name, state/country, Yarra Coordinator, membership tier)."""

    class Meta:
        model = School
        fields = [
            'name', 'state', 'country', 'yarra_coordinator_name', 'yarra_coordinator_email',
            'yarra_coordinator_phone', 'membership_tier',
        ]

def _grade_field_name(level):
    return f"gs_{level.lower().replace(' ', '_')}"


class SchoolProfileExtendedForm(forms.ModelForm):
    """Adds one required student-count field per grade level (Pre KG through Grade 12,
    stored as SchoolProfileExtended.grade_strength) and validates the Mixed/Other
    curriculum 'specify' field, on top of the plain model fields."""

    class Meta:
        model = SchoolProfileExtended
        exclude = ['school', 'updated_at', 'grade_strength']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        existing_grades = self.instance.grade_strength if self.instance and self.instance.pk else {}
        for level in GRADE_LEVELS:
            self.fields[_grade_field_name(level)] = forms.IntegerField(
                label=level, min_value=0, required=True,
                initial=existing_grades.get(level),
            )

    def clean(self):
        cleaned_data = super().clean()
        curriculum = cleaned_data.get('curriculum_adopted')
        if curriculum in ('mixed', 'other') and not cleaned_data.get('curriculum_adopted_other'):
            self.add_error('curriculum_adopted_other', "Please specify your school's curriculum.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.grade_strength = {
            level: self.cleaned_data.get(_grade_field_name(level)) for level in GRADE_LEVELS
        }
        if commit:
            instance.save()
        return instance

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Login email must match the invited email (e.g. the Yarra Coordinator email
        # on file for a School Admin) -- shown but not editable.
        self.fields['email'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
