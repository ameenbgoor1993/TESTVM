from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model for VMS.
    """
    pass

    first_name_en = models.CharField(max_length=50, blank=True)
    middle_name_en = models.CharField(max_length=50, blank=True)
    last_name_en = models.CharField(max_length=50, blank=True)
    
    first_name_ar = models.CharField(max_length=50, blank=True)
    middle_name_ar = models.CharField(max_length=50, blank=True)
    last_name_ar = models.CharField(max_length=50, blank=True)
    
    GENDER_CHOICES = [

        ('M', 'Male'),
        ('F', 'Female'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    birthdate = models.DateField(null=True, blank=True)
    
    nationality = models.CharField(max_length=100, blank=True)
    national_id = models.CharField(max_length=50, blank=True, unique=True, null=True)
    profession = models.CharField(max_length=100, blank=True)
    mobile_no = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    
    # New Fields
    MARITAL_STATUS_CHOICES = [
        ('Single', 'Single'),
        ('Married', 'Married'),
    ]
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, blank=True, null=True)
    skills = models.ManyToManyField('events.Skills', blank=True, related_name='volunteers')
    is_volunteer = models.BooleanField(default=True)
    
    VOLUNTEER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]
    volunteer_status = models.CharField(max_length=20, choices=VOLUNTEER_STATUS_CHOICES, default='PENDING')

    # Enhanced Volunteer Profile
    city = models.ForeignKey('events.City', on_delete=models.SET_NULL, null=True, blank=True, related_name='volunteers')
    has_volunteered_before = models.BooleanField(default=False, verbose_name="Have you volunteered before?")
    experience_description = models.TextField(blank=True, verbose_name="Experience Description")
    work_link = models.URLField(blank=True, verbose_name="Work/Portfolio Link")
    joining_reasons = models.ManyToManyField('core_settings.JoiningReason', blank=True, related_name='volunteers')
    
    # Participation Preferences
    DAYS_CHOICES = [
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]
    # Storing as comma-separated values for simplicity
    possible_participation_days = models.CharField(max_length=255, blank=True, help_text="Select multiple days (comma separated)")

    TIME_CHOICES = [
        ('Morning', 'Morning'),
        ('Evening', 'Evening'),
    ]
    possible_participation_time = models.CharField(max_length=255, blank=True, help_text="Select preferred times")

    AGE_RANGE_CHOICES = [
        ('ALL', 'All'),
        ('lt_7', '< 7'),
        ('7_12', '7 - 12'),
        ('12_15', '12 - 15'),
        ('15_18', '15 - 18'),
        ('18_28', '18 - 28'),
        ('28_39', '28 - 39'),
        ('39_50', '39 - 50'),
        ('gt_50', '> 50'),
    ]
    age_range = models.CharField(max_length=20, choices=AGE_RANGE_CHOICES, blank=True, null=True, verbose_name="Age Group")

    def __str__(self):
        return self.username

class AdminUserManager(models.Manager):
    def get_queryset(self):
        # Strict separation: Admins are staff and NOT volunteers (as per request)
        return super().get_queryset().filter(is_staff=True, is_volunteer=False)

class VolunteerRegistrationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_volunteer=True).exclude(volunteer_status='ACCEPTED')

class AcceptedVolunteerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_volunteer=True, volunteer_status='ACCEPTED')

class AdminUser(User):
    objects = AdminUserManager()
    class Meta:
        proxy = True
        verbose_name = "Admin"
        verbose_name_plural = "Admins"

class VolunteerRegistration(User):
    objects = VolunteerRegistrationManager()
    class Meta:
        proxy = True
        verbose_name = "Volunteer Registration"
        verbose_name_plural = "Volunteer Registrations"

class AcceptedVolunteer(User):
    objects = AcceptedVolunteerManager()
    class Meta:
        proxy = True
        verbose_name = "Volunteer"
        verbose_name_plural = "Volunteers"

class MessageLog(models.Model):
    """Log of all messages sent via admin panel"""
    MESSAGE_TYPE_CHOICES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
    ]
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES)
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    recipient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='received_messages')
    recipient_email = models.EmailField(blank=True)
    recipient_mobile = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    error_message = models.TextField(blank=True)
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_messages')
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = "Message Log"
        verbose_name_plural = "Message Logs"
    
    def __str__(self):
        return f"{self.get_message_type_display()} to {self.recipient} - {self.sent_at.strftime('%Y-%m-%d %H:%M')}"
