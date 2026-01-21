
import os
import django
import sys
from datetime import timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from users.models import User
from events.models import Event, Area, VolunteerApplication, Attendance

def verify_attendance():
    print("Verifying Attendance Model...")

    # 1. Create or get test data
    # Admin User
    admin_user, _ = User.objects.get_or_create(username='admin_test', defaults={'email': 'admin@test.com', 'is_staff': True, 'is_volunteer': False})
    
    # Volunteer User
    vol_user, _ = User.objects.get_or_create(username='vol_test', defaults={'email': 'vol@test.com', 'is_volunteer': True})
    
    # Event
    event, _ = Event.objects.get_or_create(
        title='Test Event',
        defaults={
            'description': 'Test Event Description',
            'start_date': timezone.now(),
            'end_date': timezone.now() + timedelta(days=1),
            'event_admin': admin_user
        }
    )
    
    # Area
    area1, _ = Area.objects.get_or_create(name_en='Reception', defaults={'name_ar': 'Reception AR'})
    area2, _ = Area.objects.get_or_create(name_en='Hall', defaults={'name_ar': 'Hall AR'})
    event.areas.add(area1, area2)

    # Application
    app, created = VolunteerApplication.objects.get_or_create(user=vol_user, event=event)
    if created:
        print("Created new application.")
    else:
        print("Using existing application.")

    # 2. Create Attendance Records
    # Record 1: Check in/out in Area 1
    check_in_1 = timezone.now() - timedelta(hours=4)
    check_out_1 = timezone.now() - timedelta(hours=2)
    
    att1 = Attendance.objects.create(
        application=app,
        check_in_time=check_in_1,
        check_out_time=check_out_1,
        area=area1,
        notes="First shift"
    )
    print(f"Created Attendance 1: {att1} | Duration: {att1.duration}")

    # Record 2: Check in/out in Area 2
    check_in_2 = timezone.now() - timedelta(hours=1)
    
    att2 = Attendance.objects.create(
        application=app,
        check_in_time=check_in_2,
        area=area2, # No check out yet
        notes="Second shift"
    )
    print(f"Created Attendance 2: {att2} | Duration: {att2.duration}") # Should be None

    # 3. Verify relationships
    print(f"Application has {app.attendances.count()} attendance records.")
    
    # 4. Update Record 2 (Check out)
    att2.check_out_time = timezone.now()
    att2.save()
    print(f"Updated Attendance 2: Duration: {att2.duration}")

    # 5. Verify Total Hours Calculation (if added to admin or verified manually here)
    total_duration = att1.duration + att2.duration
    print(f"Total verified duration: {total_duration}")
    
    print("Verification Successful!")

if __name__ == '__main__':
    verify_attendance()
