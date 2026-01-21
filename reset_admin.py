import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'admin'
password = 'admin123'
email = 'admin@example.com'

try:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"Successfully updated password for existing user '{username}'.")
except User.DoesNotExist:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Successfully created new superuser '{username}'.")
except Exception as e:
    print(f"Error: {e}")
