import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User
from events.models import Event, Area, VolunteerApplication

class Command(BaseCommand):
    help = 'Seeds the database with sample events and volunteer data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        # 1. Create Users
        volunteers = []
        for i in range(20):
            username = f'volunteer_{i}'
            email = f'volunteer_{i}@example.com'
            user, created = User.objects.get_or_create(username=username, email=email)
            if created:
                user.set_password('password123')
                user.save()
            volunteers.append(user)
        self.stdout.write(f'Created/Loaded {len(volunteers)} volunteers.')

        # 2. Create Events
        event_names = [
            'Summer Code Camp', 
            'Tech Conference 2026', 
            'Charity Run', 
            'Community Cleanup',
            'Music Festival'
        ]
        
        events = []
        now = timezone.now()
        
        for i, name in enumerate(event_names):
            start_date = now + timedelta(days=i*10)
            end_date = start_date + timedelta(days=2)
            event, created = Event.objects.get_or_create(
                title=name,
                defaults={
                    'description': f'Description for {name}',
                    'start_date': start_date,
                    'end_date': end_date,
                    'location': 'City Center'
                }
            )
            events.append(event)
        self.stdout.write(f'Created/Loaded {len(events)} events.')

        # 3. Create Areas for each event
        area_names = ['Registration', 'Logistics', 'Catering', 'Security', 'First Aid']
        
        for event in events:
            # Randomly pick 3-5 areas for this event
            selected_areas = random.sample(area_names, k=random.randint(3, 5))
            for area_name in selected_areas:
                area, _ = Area.objects.get_or_create(
                    event=event,
                    name=area_name,
                    defaults={'description': f'{area_name} duties'}
                )
                
                # 4. Assign Volunteers to this Area (Accepted applications)
                # Randomly assign 2-5 volunteers per area
                assigned_volunteers = random.sample(volunteers, k=random.randint(2, 5))
                for volunteer in assigned_volunteers:
                    # Randomly check-in some volunteers (e.g., 60% chance)
                    is_checked_in = random.choice([True, False, True, True, False])
                    
                    VolunteerApplication.objects.get_or_create(
                        user=volunteer,
                        event=event,
                        defaults={
                            'status': 'ACCEPTED',
                            'assigned_area': area,
                            'checked_in': is_checked_in
                        }
                    )
                    # Update if exists
                    VolunteerApplication.objects.filter(user=volunteer, event=event).update(
                        status='ACCEPTED',
                        assigned_area=area,
                        checked_in=is_checked_in
                    )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with events and accepted volunteers.'))
