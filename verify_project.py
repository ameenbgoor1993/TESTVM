import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from events.models import Event, Area, VolunteerApplication
from events import constants as events_constants
from django.utils import timezone
from django.utils import timezone
import datetime
from users.models import Volunteer

User = get_user_model()

import json

def get_data(response):
    if hasattr(response, 'data'):
        return response.data
    try:
        return json.loads(response.content)
    except:
        return {}

def run_verification():
    print("--- Starting Verification ---")
    
    # Clean up previous runs
    Volunteer.objects.filter(username='volunteer1').delete()
    Event.objects.filter(title='Charity Run').delete()

    # 1. Setup Data
    print("1. Setting up admin and event...")
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'password')
    
    if not Event.objects.filter(title="Charity Run").exists():
        event = Event.objects.create(
            title="Charity Run",
            description="5k run",
            start_date=timezone.now() + datetime.timedelta(days=1),
            end_date=timezone.now() + datetime.timedelta(days=1, hours=4),
            location="Central Park"
        )
        area = Area.objects.create(name_en="Water Station", name_ar="محطة مياه")
        event.areas.add(area)
        print(f"   Event created: {event.title} with Area: {area.name_en}")
    else:
        event = Event.objects.get(title="Charity Run")
        area = event.areas.first()
        print("   Event already exists.")

    # 2. Test Registration API
    print("2. Testing Registration API...")
    client = APIClient()
    reg_data = {
        "username": "volunteer1",
        "email": "vol1@example.com",
        "password": "strongpassword123"
    }
    
    # Check if user exists first to avoid fail on re-run
    if not Volunteer.objects.filter(username="volunteer1").exists():
        response = client.post('/api/register/', reg_data)
        if response.status_code == 201:
            print("   Registration Successful")
        else:
            print(f"   Registration Failed: {get_data(response)}")
            return
    else:
        print("   User volunteer1 already exists.")

    # Login
    resp_login = client.post('/api/login/', {'username': 'volunteer1', 'password': 'strongpassword123'})
    
    if resp_login.status_code == 200:
        data = get_data(resp_login)
        token = data.get('data', {}).get('token')
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        print("   Login Successful, Token received.")
    else:
        print(f"   Login Failed: {resp_login.content}")
        return

    # 3. Test List Events API
    print("3. Testing List Events API...")
    resp_events = client.get('/api/events/')
    data_events = get_data(resp_events)
    if resp_events.status_code == 200 and len(data_events) > 0:
        print(f"   Events retrieved: {len(data_events)}")
    else:
        print(f"   Failed to list events: {data_events}")

    # 4. Test Join Event API
    print("4. Testing Join Event API...")
    join_data = {'event': event.id}
    # Check if already joined
    if not VolunteerApplication.objects.filter(volunteer__username='volunteer1', event=event).exists():
        resp_join = client.post('/api/events/join/', join_data)
        if resp_join.status_code == 201:
            print("   Joined Event Successful")
        else:
            print(f"   Failed to join event: {get_data(resp_join)}")
            return
    else:
        print("   Already joined event.")
    
    # 5. Verify Application Pending
    app = VolunteerApplication.objects.get(volunteer__username='volunteer1', event=event)
    print(f"   Application Status: {app.status}")
    
    # 6. Admin Action (Simulate)
    print("6. Simulating Admin Acceptance...")
    app.status = events_constants.APP_STATUS_ACCEPTED
    app.save()
    
    app.refresh_from_db()
    print(f"   Updated Application Status: {app.status}")
    
    print("--- Verification Complete ---")

if __name__ == '__main__':
    try:
        run_verification()
    except Exception as e:
        print(f"An error occurred: {e}")
