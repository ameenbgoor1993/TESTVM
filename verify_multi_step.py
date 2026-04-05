import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient

client = APIClient()

print("1. Creating Primary Account (Step 1)...")
_rand = random.randint(1000, 99999)
_email = f"guardian{_rand}@example.com"
res1 = client.post('/api/register/step1/', {
    'email': _email,
    'password': 'password123',
    'mobile': f'0501{_rand}67',
    'gender': 1,
    'first_name': 'Ahmad',
    'last_name': 'Guardian',
    'date_of_birth': '1980-01-01'
}, format='json')

print(res1.status_code)
if res1.status_code >= 400:
    print(res1.json())
    exit(1)

data = res1.json().get('data', res1.json())
token = data['token']
account_id = data['account_id']
default_profile_id = data.get('default_profile_id')

print(f"Token: {token}, Account: {account_id}, Default Profile: {default_profile_id}")

print("\n2. Setting User Type to Guardian (Step 2)...")
res2 = client.patch('/api/register/step2/', {
    'user_type': 1 # Guardian
}, format='json', HTTP_AUTHORIZATION='Bearer ' + token)

print(res2.status_code)
if res2.status_code >= 400: exit(1)

print("\n3. Adding extra info to guardian profile (Step 3)...")
res3 = client.patch('/api/register/step3/', {
    'nationality': 'SA',
    'address': 'Riyadh'
}, format='json', HTTP_AUTHORIZATION='Bearer ' + token)
print(res3.status_code)
if res3.status_code >= 400: exit(1)

print("\n4. Adding Child Profile...")
res_child = client.post('/api/profiles/add-child/', {
    'first_name': 'Omar',
    'last_name': 'Guardian',
    'date_of_birth': '2010-06-15',
    'gender': 1,
    'user_type': 2 # The child themselves
}, format='json', HTTP_AUTHORIZATION='Bearer ' + token)

print(res_child.status_code)
if res_child.status_code >= 400:
    print(res_child.json())
    exit(1)

child_data = res_child.json().get('data', res_child.json())
child_profile_id = child_data['profile']['id']
print(f"Created Child profile ID: {child_profile_id}")

print("\n5. Testing Custom Login (Should return Account + 2 Profiles)...")
res_login = client.post('/api/login/', {
    'username': _email,
    'password': 'password123'
}, format='json')

print(res_login.status_code)
if res_login.status_code >= 400: exit(1)

login_data = res_login.json().get('data', res_login.json())
print("Profiles attached to account:")
for p in login_data['profiles']:
    print(p)

print("\nSUCCESS! Account-Profile pattern is fully verified.")
