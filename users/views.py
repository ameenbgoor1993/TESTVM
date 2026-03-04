from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import VolunteerRegistrationSerializer
from .models import Volunteer, VolunteerToken
from config.renderers import CustomJSONRenderer

class RegisterView(generics.CreateAPIView):
    queryset = Volunteer.objects.all()
    serializer_class = VolunteerRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class CustomLoginView(APIView):
    renderer_classes = [CustomJSONRenderer]
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'Please provide username and password.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            volunteer = Volunteer.objects.get(username=username)
        except Volunteer.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
            
        if not volunteer.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
            
        token, _ = VolunteerToken.objects.get_or_create(volunteer=volunteer)
        return Response({
            'token': token.key,
            'volunteer_id': volunteer.pk,
            'email': volunteer.email
        })
