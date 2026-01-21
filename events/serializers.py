from rest_framework import serializers
from .models import Event, Area, VolunteerApplication, City, Skills

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name_ar', 'name_en']

class SkillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skills
        fields = ['id', 'name_ar', 'name_en']

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['id', 'name_ar', 'name_en', 'description']

class EventSerializer(serializers.ModelSerializer):
    areas = AreaSerializer(many=True, read_only=True)
    cities = CitySerializer(many=True, read_only=True)
    skills = SkillsSerializer(many=True, read_only=True)
    event_admin_username = serializers.CharField(source='event_admin.username', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'category', 'cities', 'location', 'areas',
            'start_date', 'end_date', 'registration_start_datetime', 'registration_end_datetime',
            'show_in_home_page', 'send_notification_to_volunteer',
            'gender_preference', 'age_range',
            'required_volunteers', 'extra_volunteers', 'required_males', 'required_females', 'extra_males', 'extra_females',
            'extra_seats', 'min_participation_time_slots',
            'featured_image', 'event_admin', 'event_admin_username',
            'proponent_name', 'proponent_mobile', 'proponent_email',
            'skills', 'areas'
        ]

class VolunteerApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerApplication
        fields = ['id', 'event', 'status']
        read_only_fields = ['status', 'user'] # user is set in view
