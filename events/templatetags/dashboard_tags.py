from django import template
from events.models import VolunteerApplication
import datetime

register = template.Library()

@register.simple_tag
def get_dashboard_stats():
    from events.models import VolunteerApplication, Event, Area
    from django.db.models import Sum, Count
    import json
    from events import constants as events_constants

    # 1. Volunteers to be Accepted (Pending Applications)
    volunteers_to_accept = VolunteerApplication.objects.filter(status=events_constants.APP_STATUS_PENDING).count()

    # 2. Checked-In Volunteers (Grand Total)
    # Count applications that have at least one attendance record
    checked_in_volunteers = VolunteerApplication.objects.filter(attendances__isnull=False).distinct().count()

    # 3. Training Enrollments (Category='Training')
    training_enrollments = VolunteerApplication.objects.filter(
        event__category='Training'
    ).count()

    # 4. Volunteering Hours (Sum of Attendance durations)
    from events.models import Attendance
    total_duration = datetime.timedelta(0)
    # Aggregate in Python for now to support timedelta sum if DB backend doesn't support it easily
    # Or iterate.
    all_attendances = Attendance.objects.exclude(check_out_time__isnull=True)
    
    # Calculate total seconds
    total_seconds = 0
    for att in all_attendances:
        if att.duration:
            total_seconds += att.duration.total_seconds()
    
    volunteering_hours = round(total_seconds / 3600, 2)

    # 5. Chart Data (Volunteers per Event per Area)
    # Structure: labels: [Event1, Event2...], datasets: [{label: AreaName, data: [count, count...]}, ...]
    chart_data = {
        'labels': [],
        'datasets': []
    }

    try:
        events = Event.objects.all().order_by('start_date')
        event_titles = [e.title for e in events]
        chart_data['labels'] = event_titles

        # Get all unique area names (from Area model directly, not proxy)
        # We use Area.objects rather than AreaProxy to ensure compatibility if imports vary
        area_names = Area.objects.values_list('name_en', flat=True).distinct() 
        # Note: using name_en as label. If name_ar is preferred, logic changes.
        
        # Colors for the chart
        colors = ['#1976D2', '#2196F3', '#4CAF50', '#FFC107', '#FF5722', '#9C27B0', '#00BCD4', '#009688']
        
        for i, area_name in enumerate(area_names):
            data_points = []
            for event in events:
                # Count attendance records in this area for this event
                count = Attendance.objects.filter(
                    application__event=event,
                    area__name_en=area_name
                ).count()
                data_points.append(count)
            
            # Only add dataset if it has any data to avoid clutter
            if any(data_points):
                chart_data['datasets'].append({
                    'label': area_name,
                    'data': data_points,
                    'backgroundColor': colors[i % len(colors)]
                })
                
    except Exception as e:
        print(f"Error generating chart data: {e}")
        chart_data = {'labels': [], 'datasets': []}

    # Get all events for dropdown
    all_events = Event.objects.all().values('id', 'title')
    
    # Missing models (Placeholders set to 0 as requested "real data" implies existing data)
    # If specific models for Evaluations/Interviews/Enquiries created later, update here.
    return {
        'pending_evaluations': 0, 
        'pending_interviews': 0,
        'volunteers_to_accept': volunteers_to_accept,
        'volunteer_enquiries': 0,
        'general_enquiries': 0,
        'volunteering_hours': volunteering_hours,
        'checked_in_volunteers': checked_in_volunteers,
        'training_enrollments': training_enrollments,
        'chart_data_json': json.dumps(chart_data),
        'all_events': all_events
    }
