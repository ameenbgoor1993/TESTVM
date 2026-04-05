from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .authentication import VolunteerTokenAuthentication
from .serializers import (
    VolunteerRegistrationStep1Serializer,
    VolunteerRegistrationStep2Serializer,
    VolunteerRegistrationStep3Serializer,
    VolunteerProfileCreateSerializer
)
from .models import Volunteer, VolunteerToken, VolunteerProfile
from config.renderers import CustomJSONRenderer

class CustomLoginView(APIView):
    renderer_classes = [CustomJSONRenderer]
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'Please provide username/email and password.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Login via username or email
            volunteer = Volunteer.objects.get(username=username)
        except Volunteer.DoesNotExist:
            try:
                volunteer = Volunteer.objects.get(email=username)
            except Volunteer.DoesNotExist:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
            
        if not volunteer.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
            
        token, _ = VolunteerToken.objects.get_or_create(volunteer=volunteer)
        
        # Return profiles so frontend can let user select which one
        profiles = list(volunteer.profiles.values('id', 'first_name_en', 'user_type'))
        
        return Response({
            'token': token.key,
            'account_id': volunteer.pk,
            'email': volunteer.email,
            'profiles': profiles
        })

class RegisterStep1View(generics.CreateAPIView):
    serializer_class = VolunteerRegistrationStep1Serializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = serializer.save()
        token, _ = VolunteerToken.objects.get_or_create(volunteer=account)
        
        # Return the default profile id
        default_profile = account.profiles.first()
        
        return Response({
            'message': 'Step 1 complete. Account and initial profile created.',
            'token': token.key,
            'account_id': account.pk,
            'default_profile_id': default_profile.pk if default_profile else None
        }, status=status.HTTP_201_CREATED)

class RegisterStep2View(generics.UpdateAPIView):
    serializer_class = VolunteerRegistrationStep2Serializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [VolunteerTokenAuthentication]

    def get_object(self):
        # Update the default profile for onboarding
        return getattr(self.request.user, 'volunteer', self.request.user).profiles.first()
        
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({'message': 'Profile user type assigned.', 'data': response.data})

class RegisterStep3View(generics.UpdateAPIView):
    serializer_class = VolunteerRegistrationStep3Serializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [VolunteerTokenAuthentication]

    def get_object(self):
        # Usually step 3 completes the onboarding of the initial profile
        return getattr(self.request.user, 'volunteer', self.request.user).profiles.first()
        
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({'message': 'Profile completed successfully.', 'data': response.data})

class CreateChildProfileView(generics.CreateAPIView):
    serializer_class = VolunteerProfileCreateSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [VolunteerTokenAuthentication]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'Child profile added.',
            'profile': serializer.data
        }, status=status.HTTP_201_CREATED)
