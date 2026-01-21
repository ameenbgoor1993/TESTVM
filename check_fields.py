import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User
from events.models import Event

print("Checking User Fields:")
user_fields = [f.name for f in User._meta.fields]
if 'age_range' in user_fields:
    print("SUCCESS: 'age_range' found in User model.")
else:
    print("FAIL: 'age_range' NOT found in User model.")

print("\nChecking Event Fields:")
event_fields = [f.name for f in Event._meta.fields]
if 'age_range' in event_fields:
    print("SUCCESS: 'age_range' found in Event model.")
else:
    print("FAIL: 'age_range' NOT found in Event model.")
