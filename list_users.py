import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
users = User.objects.all()

print(f"{'Username':<20} {'Email':<30} {'Is Superuser':<15} {'Is Staff':<15}")
print("-" * 80)
for user in users:
    print(f"{user.username:<20} {user.email:<30} {str(user.is_superuser):<15} {str(user.is_staff):<15}")
