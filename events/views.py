from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.dateparse import parse_date
from .models import Event, VolunteerApplication
from .serializers import EventSerializer, VolunteerApplicationSerializer
from . import constants
from users import constants as users_constants


class EventListView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny] # Or IsAuthenticatedOrReadOnly if preferred


class EventDetailView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]


from users.authentication import VolunteerTokenAuthentication

class JoinEventView(generics.CreateAPIView):
    queryset = VolunteerApplication.objects.all()
    serializer_class = VolunteerApplicationSerializer
    authentication_classes = [VolunteerTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # 1. Custom Validations before creating
        event_id = request.data.get('event')

        
        if not event_id:
            return Response({'error': 'Event ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
            
        from django.utils import timezone
        now = timezone.now()
        
        # Date Validation
        if event.registration_start_datetime and now < event.registration_start_datetime:
            return Response({'error': 'Registration has not started yet'}, status=status.HTTP_400_BAD_REQUEST)
        if event.registration_end_datetime and now > event.registration_end_datetime:
             return Response({'error': 'Registration has ended'}, status=status.HTTP_400_BAD_REQUEST)
             
        # Age Range Validation
        user_age_range = request.user.age_range
        if event.age_range != constants.AGE_RANGE_ALL:
            if not user_age_range:
                return Response({'error': 'Please update your profile with your Age Group to join this event'}, status=status.HTTP_400_BAD_REQUEST)
            if user_age_range != event.age_range:
                return Response({'error': f'This event is for specific age group: {event.get_age_range_display()}. Your profile does not match.'}, status=status.HTTP_400_BAD_REQUEST)

        # City Validation
        user_city = request.user.city
        event_cities = event.cities.all()
        if event_cities.exists():
            if not user_city:
                 return Response({'error': 'Please update your profile with your City to join this event'}, status=status.HTTP_400_BAD_REQUEST)
            if not event_cities.filter(id=user_city.id).exists():
                 return Response({'error': 'This event is not available in your city.'}, status=status.HTTP_400_BAD_REQUEST)

             
        # Skills Validation (Intersection)
        user_skills = request.user.skills.all()
        event_skills = event.skills.all()
        if event_skills.exists():
            if not user_skills.filter(pk__in=event_skills).exists():
                 return Response({'error': 'You do not have any of the required skills for this event'}, status=status.HTTP_400_BAD_REQUEST)

        # Capacity & Gender Validation
        user_gender = request.user.gender # 1 or 2 based on Volunteer model
        
        if event.gender_preference == constants.GENDER_PREF_SPECIFIC:
            if not user_gender:
                return Response({'error': 'Please update your profile with your gender to join this event'}, status=status.HTTP_400_BAD_REQUEST)
                
            if user_gender == users_constants.GENDER_MALE:
                required = event.required_males
                extra = event.extra_males
                # Count current male applications
                current_count = event.applications.filter(volunteer__gender=users_constants.GENDER_MALE).exclude(status=constants.APP_STATUS_REJECTED).count()
            elif user_gender == users_constants.GENDER_FEMALE:
                required = event.required_females
                extra = event.extra_females
                current_count = event.applications.filter(volunteer__gender=users_constants.GENDER_FEMALE).exclude(status=constants.APP_STATUS_REJECTED).count()
            else:
                return Response({'error': 'Gender not supported for this event criteria'}, status=status.HTTP_400_BAD_REQUEST)
                
            total_limit = required + extra
            if current_count >= total_limit:
                 return Response({'error': 'Event capacity reached for your gender'}, status=status.HTTP_400_BAD_REQUEST)
                 
        else: # GENERAL
            required = event.required_volunteers
            extra = event.extra_volunteers
            current_count = event.applications.exclude(status=constants.APP_STATUS_REJECTED).count()
            
            total_limit = required + extra
            # If both are 0, does it mean unlimited? Usually yes, or manually managed. 
            # Assuming if limits are defined (>0) we enforce them. If 0, maybe unlimited? 
            # Or 0 means 0 allowed? Standard VMS usually 0 means 0 allowed (closed).
            # But let's assume strict enforcement if limits are set.
            if total_limit > 0 and current_count >= total_limit:
                return Response({'error': 'Event capacity reached'}, status=status.HTTP_400_BAD_REQUEST)

        # Participation Slots Validation



        # Standard Create Logic
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            if 'unique constraint' in str(e).lower() or 'integrityerror' in str(type(e)).lower():
                 return Response({"detail": "You have already applied for this event."}, status=status.HTTP_400_BAD_REQUEST)
            raise e

    def perform_create(self, serializer):
        serializer.save(volunteer=self.request.user)

class EventCheckInStatsView(APIView):
    permission_classes = [permissions.AllowAny] # Adjust as needed

    def get(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
            
            # Base query
            query = VolunteerApplication.objects.filter(event=event, checked_in=True)
            
            # Date filtering if provided
            from_date = request.query_params.get('from')
            to_date = request.query_params.get('to')
            
            if from_date:
                query = query.filter(updated_at__gte=parse_date(from_date))
            if to_date:
                query = query.filter(updated_at__lte=parse_date(to_date))
                
            count = query.count()
            
            return Response({'check_in_count': count})
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

from .models import Skills
from .serializers import SkillsSerializer

class SkillsListView(generics.ListAPIView):
    queryset = Skills.objects.all()
    serializer_class = SkillsSerializer
    permission_classes = [permissions.AllowAny]
