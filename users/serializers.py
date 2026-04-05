from rest_framework import serializers
from events.models import City, Skills
from core_settings.models import JoiningReason
from .models import Volunteer, VolunteerProfile
import uuid

class VolunteerRegistrationStep1Serializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    mobile = serializers.CharField(required=True)
    
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    gender = serializers.IntegerField(required=True)
    date_of_birth = serializers.DateField(required=True)
    
    def validate_email(self, value):
        if Volunteer.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_mobile(self, value):
        if Volunteer.objects.filter(mobile_no=value).exists():
            raise serializers.ValidationError("An account with this mobile number already exists.")
        return value

    def create(self, validated_data):
        email = validated_data.get('email')
        mobile = validated_data.get('mobile')
        password = validated_data.get('password')
        
        username = email
        if Volunteer.objects.filter(username=username).exists():
            username = f"{email}_{str(uuid.uuid4())[:8]}"

        # Create Account
        account = Volunteer.objects.create(
            username=username,
            email=email,
            mobile_no=mobile
        )
        account.set_password(password)
        account.save()
        
        # Create Initial Profile
        VolunteerProfile.objects.create(
            account=account,
            first_name_en=validated_data.get('first_name'),
            last_name_en=validated_data.get('last_name'),
            gender=validated_data.get('gender'),
            birthdate=validated_data.get('date_of_birth'),
            user_type=2 # Default to Themself
        )
        
        return account

class VolunteerProfileCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='first_name_en', required=True)
    last_name = serializers.CharField(source='last_name_en', required=True)
    date_of_birth = serializers.DateField(source='birthdate', required=True)

    class Meta:
        model = VolunteerProfile
        fields = ('id', 'first_name', 'last_name', 'gender', 'date_of_birth', 'user_type')
        read_only_fields = ('id',)

    def create(self, validated_data):
        account = self.context['request'].user
        validated_data['account'] = account
        return super().create(validated_data)

class VolunteerProfileUpdateSerializer(serializers.ModelSerializer):
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), required=False, allow_null=True)
    joining_reasons = serializers.PrimaryKeyRelatedField(many=True, queryset=JoiningReason.objects.all(), required=False)
    skills = serializers.PrimaryKeyRelatedField(many=True, queryset=Skills.objects.all(), required=False)

    class Meta:
        model = VolunteerProfile
        fields = (
            'id', 'user_type',
            'first_name_en', 'last_name_en', 'gender', 'birthdate',
            'first_name_ar', 'middle_name_en', 'middle_name_ar', 'last_name_ar',
            'nationality', 'national_id', 'profession', 'address', 'emergency_contact',
            'city', 'age_range', 'has_volunteered_before', 'experience_description', 'work_link',
            'joining_reasons', 'possible_participation_days', 'possible_participation_time',
            'skills'
        )
        read_only_fields = ('id',)

class VolunteerRegistrationStep2Serializer(serializers.ModelSerializer):
    # This was originally used to specify the user_type. We can update the main profile.
    user_type = serializers.IntegerField(required=True)
    class Meta:
        model = VolunteerProfile
        fields = ('user_type',)

class VolunteerRegistrationStep3Serializer(VolunteerProfileUpdateSerializer):
    pass
