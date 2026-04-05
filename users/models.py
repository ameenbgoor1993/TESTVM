from django.contrib.auth.models import AbstractUser
from django.db import models
from . import constants

class User(AbstractUser):
    """
    Custom User model for VMS.
    """
    is_volunteer = models.BooleanField(default=False)

    # Defaults for admin users if needed, but AbstractUser has is_staff etc.
    def save(self, *args, **kwargs):
        # Admin logic: if not a volunteer, ensure they are staff
        if not self.is_volunteer and not self.is_superuser:
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

from django.contrib.auth.hashers import make_password, check_password

class Volunteer(models.Model):
     # Core Auth fields for standalone volunteer account
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    mobile_no = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Account ({self.email})"

    @property
    def is_authenticated(self):
        return True

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

class VolunteerProfile(models.Model):
    account = models.ForeignKey(Volunteer, on_delete=models.CASCADE, related_name='profiles')
    user_type = models.IntegerField(choices=constants.USER_TYPE_CHOICES, default=constants.USER_TYPE_THEMSELF)
    
    first_name_en = models.CharField(max_length=50, blank=True)
    middle_name_en = models.CharField(max_length=50, blank=True)
    last_name_en = models.CharField(max_length=50, blank=True)
    
    first_name_ar = models.CharField(max_length=50, blank=True)
    middle_name_ar = models.CharField(max_length=50, blank=True)
    last_name_ar = models.CharField(max_length=50, blank=True)
    
    gender = models.IntegerField(choices=constants.GENDER_CHOICES, blank=True, null=True)
    birthdate = models.DateField(null=True, blank=True)
    
    nationality = models.CharField(max_length=100, blank=True)
    national_id = models.CharField(max_length=50, blank=True, unique=True, null=True)
    profession = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    
    marital_status = models.IntegerField(choices=constants.MARITAL_STATUS_CHOICES, blank=True, null=True)
    skills = models.ManyToManyField('events.Skills', blank=True, related_name='profiles')
    
    volunteer_status = models.IntegerField(choices=constants.VOLUNTEER_STATUS_CHOICES, default=constants.VOLUNTEER_STATUS_PENDING)

    city = models.ForeignKey('events.City', on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles')
    has_volunteered_before = models.BooleanField(default=False, verbose_name="Have you volunteered before?")
    experience_description = models.TextField(blank=True, verbose_name="Experience Description")
    work_link = models.URLField(blank=True, verbose_name="Work/Portfolio Link")
    joining_reasons = models.ManyToManyField('core_settings.JoiningReason', blank=True, related_name='profiles')
    
    possible_participation_days = models.CharField(max_length=255, blank=True, help_text="Select multiple days (comma separated)")
    possible_participation_time = models.CharField(max_length=255, blank=True, help_text="Select preferred times")

    age_range = models.IntegerField(choices=constants.AGE_RANGE_CHOICES, blank=True, null=True, verbose_name="Age Group")

    def __str__(self):
        name = self.first_name_en or self.first_name_ar or "Unknown"
        return f"{name} ({self.get_user_type_display()})"

class VolunteerToken(models.Model):
    key = models.CharField(max_length=40, primary_key=True)
    volunteer = models.OneToOneField(Volunteer, related_name='auth_token', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            import binascii
            import os
            self.key = binascii.hexlify(os.urandom(20)).decode()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.key

class AdminUserManager(models.Manager):
    def get_queryset(self):
        # Strict separation: Admins are staff and NOT volunteers (as per request)
        return super().get_queryset().filter(is_staff=True, is_volunteer=False)

class AdminUserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_staff=True, is_volunteer=False)

class AdminUser(User):
    objects = AdminUserManager()
    class Meta:
        proxy = True
        verbose_name = "Admin"
        verbose_name_plural = "Admins"

class VolunteerRegistrationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(volunteer_status=constants.VOLUNTEER_STATUS_PENDING)

class AcceptedVolunteerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(volunteer_status=constants.VOLUNTEER_STATUS_ACCEPTED)

class VolunteerRegistration(VolunteerProfile):
    objects = VolunteerRegistrationManager()
    class Meta:
        proxy = True
        verbose_name = "Volunteer Registration"
        verbose_name_plural = "Volunteer Registrations"

class AcceptedVolunteer(VolunteerProfile):
    objects = AcceptedVolunteerManager()
    class Meta:
        proxy = True
        verbose_name = "Volunteer"
        verbose_name_plural = "Volunteers"

class MessageLog(models.Model):
    """Log of all messages sent via admin panel"""
    message_type = models.IntegerField(choices=constants.MESSAGE_TYPE_CHOICES)
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    recipient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='received_messages')
    recipient_email = models.EmailField(blank=True)
    recipient_mobile = models.CharField(max_length=20, blank=True)
    status = models.IntegerField(choices=constants.MESSAGE_STATUS_CHOICES)
    error_message = models.TextField(blank=True)
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_messages')
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = "Message Log"
        verbose_name_plural = "Message Logs"
    
    def __str__(self):
        return f"{self.get_message_type_display()} to {self.recipient} - {self.sent_at.strftime('%Y-%m-%d %H:%M')}"
