from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username', 'email',
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
