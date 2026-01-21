from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username', 'email',
            'first_name_en', 'middle_name_en', 'last_name_en',
            'first_name_ar', 'middle_name_ar', 'last_name_ar',
            'gender', 'birthdate', 'nationality', 'national_id',
            'profession', 'mobile_no', 'address', 'emergency_contact',
            'is_staff', 'is_volunteer'
        )

class AdminUserCreationForm(UserCreationForm):
    # Form specifically for creating Admin users
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
    )
    class Meta:
        model = User
        fields = (
            'username', 'email', 
            'first_name_en', 'last_name_en', 
            'first_name_ar', 'last_name_ar',
            'gender', 'birthdate', 
            'mobile_no', 'national_id',
            'is_staff', 'is_superuser', 'groups'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True # Force staff status for Admins
        user.is_volunteer = False # Ensure not flagged as volunteer, to appear in Admin list
        if commit:
            user.save()
            self.save_m2m() # Save groups
        return user

    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        if not national_id:
            return None  # Save as NULL to avoid unique constraint violation
        return national_id

class SendCommunicationForm(forms.Form):
    MESSAGE_TYPES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('both', 'Both (SMS & Email)'),
    ]
    message_type = forms.ChoiceField(choices=MESSAGE_TYPES, widget=forms.RadioSelect, initial='email')
    subject = forms.CharField(max_length=255, required=False, help_text="Required for Email")
    message = forms.CharField(widget=forms.Textarea, help_text="Content of the message/SMS")

    def clean(self):
        cleaned_data = super().clean()
        msg_type = cleaned_data.get('message_type')
        subject = cleaned_data.get('subject')
        
        if msg_type in ['email', 'both'] and not subject:
             self.add_error('subject', 'Subject is required for Email.')
        return cleaned_data

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'
