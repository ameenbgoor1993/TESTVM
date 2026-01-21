import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Find all staff users who are currently incorrectly marked as volunteers
staff_users = User.objects.filter(is_staff=True, is_volunteer=True)
count = staff_users.count()

print(f"Found {count} staff users marked as volunteers.")

if count > 0:
    rows = staff_users.update(is_volunteer=False)
    print(f"Updated {rows} users. They should now appear in the Admin list.")
else:
    print("No users needed updating. Check if your user is actually is_staff=True.")
