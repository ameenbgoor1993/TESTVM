from rest_framework import serializers
from events.models import City, Skills
from core_settings.models import JoiningReason
from .models import Volunteer

class VolunteerRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Volunteer
        fields = (
            'id', 'username', 'email', 'password',
            # We'll accept these in the request, but they belong to Volunteer now
            'first_name_en', 'middle_name_en', 'last_name_en',
            'first_name_ar', 'middle_name_ar', 'last_name_ar',
            'gender', 'birthdate', 'nationality', 'national_id',
            'profession', 'mobile_no', 'address', 'emergency_contact',
            'city', 'age_range', 'has_volunteered_before', 'experience_description', 'work_link',
            'joining_reasons', 'possible_participation_days', 'possible_participation_time',
            'skills'
        )
        # Explicitly declare all fields for Volunteer since they are now on the same model.
        # However, for simplicity without rewriting the whole serializer, we'll explicitly keep the current declarations.
    first_name_en = serializers.CharField(required=False, allow_blank=True)
    middle_name_en = serializers.CharField(required=False, allow_blank=True)
    last_name_en = serializers.CharField(required=False, allow_blank=True)
    first_name_ar = serializers.CharField(required=False, allow_blank=True)
    middle_name_ar = serializers.CharField(required=False, allow_blank=True)
    last_name_ar = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.CharField(required=False, allow_blank=True)
    birthdate = serializers.DateField(required=False, allow_null=True)
    nationality = serializers.CharField(required=False, allow_blank=True)
    national_id = serializers.CharField(required=False, allow_blank=True)
    profession = serializers.CharField(required=False, allow_blank=True)
    mobile_no = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    emergency_contact = serializers.CharField(required=False, allow_blank=True)
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), required=False, allow_null=True)
    age_range = serializers.CharField(required=False, allow_blank=True)
    has_volunteered_before = serializers.BooleanField(required=False, default=False)
    experience_description = serializers.CharField(required=False, allow_blank=True)
    work_link = serializers.URLField(required=False, allow_blank=True)
    joining_reasons = serializers.PrimaryKeyRelatedField(many=True, queryset=JoiningReason.objects.all(), required=False)
    possible_participation_days = serializers.CharField(required=False, allow_blank=True)
    possible_participation_time = serializers.CharField(required=False, allow_blank=True)
    skills = serializers.PrimaryKeyRelatedField(many=True, queryset=Skills.objects.all(), required=False)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        joining_reasons = validated_data.pop('joining_reasons', [])
        skills = validated_data.pop('skills', [])
        
        volunteer = Volunteer.objects.create(**validated_data)
        
        if password:
            volunteer.set_password(password)
            volunteer.save()
            
        if joining_reasons:
            volunteer.joining_reasons.set(joining_reasons)
            
        if skills:
            volunteer.skills.set(skills)
            
        return volunteer
