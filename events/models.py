from django.db import models
from django.conf import settings

class City(models.Model):
    name_ar = models.CharField(max_length=100, verbose_name="Name (Arabic)")
    name_en = models.CharField(max_length=100, verbose_name="Name (English)")
    
    class Meta:
        verbose_name_plural = "Cities"
    
    def __str__(self):
        return self.name_en

class Skills(models.Model):
    name_ar = models.CharField(max_length=100, verbose_name="Name (Arabic)")
    name_en = models.CharField(max_length=100, verbose_name="Name (English)")
    
    class Meta:
        verbose_name_plural = "Skills"
    
    def __str__(self):
        return self.name_en

class Event(models.Model):
    CATEGORY_CHOICES = [
        ('Event', 'Event'),
        ('Talks', 'Talks'),
        ('International/VolunteerDay', 'International/VolunteerDay'),
        ('Ceremony', 'Ceremony'),
        ('Programs', 'Programs'),
        ('ProffisionalVolunteer', 'ProffisionalVolunteer'),
        ('Training', 'Training'),
        ('Workshop', 'Workshop'),
        ('Initiative', 'Initiative'),
        ('MeetingCycle', 'MeetingCycle'),
        ('Orientation', 'Orientation'),
    ]

    # Basic Info
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Event')
    cities = models.ManyToManyField(City, blank=True, related_name='events')
    location = models.CharField(max_length=255)
    
    # Dates
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    registration_start_datetime = models.DateTimeField(null=True, blank=True)
    registration_end_datetime = models.DateTimeField(null=True, blank=True)
    
    # Flags
    show_in_home_page = models.BooleanField(default=False)
    send_notification_to_volunteer = models.BooleanField(default=False)
    
    # Capacity & Requirements
    GENDER_PREFERENCE_CHOICES = [
        ('GENERAL', 'General'),
        ('SPECIFIC', 'Specify Gender'),
    ]
    gender_preference = models.CharField(max_length=10, choices=GENDER_PREFERENCE_CHOICES, default='GENERAL')
    
    required_volunteers = models.IntegerField(default=0)
    extra_volunteers = models.IntegerField(default=0, help_text="Extra numbers in the waiting list")
    
    required_males = models.IntegerField(default=0)
    required_females = models.IntegerField(default=0)
    extra_males = models.IntegerField(default=0, help_text="Extra seats males (waiting list)")
    extra_females = models.IntegerField(default=0, help_text="Extra seats females (waiting list)")

    extra_seats = models.IntegerField(default=0)
    extra_seats = models.IntegerField(default=0)
    min_participation_time_slots = models.IntegerField(default=1)

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
    age_range = models.CharField(max_length=20, choices=AGE_RANGE_CHOICES, default='ALL', verbose_name="Target Age Group")
    
    # Media
    featured_image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    
    # Administration
    event_admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'is_staff': True},
        related_name='managed_events'
    )
    
    # Proponent Info
    proponent_name = models.CharField(max_length=255, blank=True, default='')
    proponent_mobile = models.CharField(max_length=20, blank=True, default='')
    proponent_email = models.EmailField(blank=True, default='')
    
    # Relations
    skills = models.ManyToManyField(Skills, blank=True, related_name='events')
    areas = models.ManyToManyField('Area', blank=True, related_name='events')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Area(models.Model):
    # Removed event FK to make Area reusable
    name_ar = models.CharField(max_length=100, verbose_name="Name (Arabic)", default='')
    name_en = models.CharField(max_length=100, verbose_name="Name (English)", default='')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name_en

class VolunteerApplication(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='applications', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name='applications', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.status})"

class Attendance(models.Model):
    application = models.ForeignKey(VolunteerApplication, related_name='attendances', on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(verbose_name="Check-In Time")
    check_out_time = models.DateTimeField(null=True, blank=True, verbose_name="Check-Out Time")
    area = models.ForeignKey(Area, related_name='attendances', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, verbose_name="Notes")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-check_in_time']
        verbose_name = "Attendance Record"
        verbose_name_plural = "Attendance Records"

    def __str__(self):
        return f"{self.application.user.username} - {self.check_in_time.strftime('%Y-%m-%d %H:%M')}"

    @property
    def duration(self):
        if self.check_in_time and self.check_out_time:
            return self.check_out_time - self.check_in_time
        return None
