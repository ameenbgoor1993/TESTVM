from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password',
            'first_name_en', 'middle_name_en', 'last_name_en',
            'first_name_ar', 'middle_name_ar', 'last_name_ar',
            'gender', 'birthdate', 'nationality', 'national_id',
            'profession', 'mobile_no', 'address', 'emergency_contact',
            'city', 'age_range', 'has_volunteered_before', 'experience_description', 'work_link',
            'joining_reasons', 'possible_participation_days', 'possible_participation_time',
            'skills'
        )
        extra_kwargs = {
            'first_name_en': {'required': False},
            'last_name_en': {'required': False},
            'joining_reasons': {'required': False},
            'skills': {'required': False},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        joining_reasons = validated_data.pop('joining_reasons', [])
        skills = validated_data.pop('skills', [])
        
        user = User.objects.create_user(**validated_data)
        
        if password:
            user.set_password(password)
            user.save()
            
        if joining_reasons:
            user.joining_reasons.set(joining_reasons)
            
        if skills:
            user.skills.set(skills)
            
        return user
