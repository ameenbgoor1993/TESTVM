import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.forms import AdminUserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

with open("debug_output.txt", "w") as f:
    f.write(f"Parent UserCreationForm Fields: {list(UserCreationForm().fields.keys())}\n")
    form = AdminUserCreationForm(data=data)
    f.write(f"Form Fields: {list(form.fields.keys())}\n")
    f.write(f"Form Valid? {form.is_valid()}\n")

    if not form.is_valid():
        f.write("Errors:\n")
        f.write(form.errors.as_text())
    else:
        f.write("Form is valid!\n")
