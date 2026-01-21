from django.contrib import admin
from django.template.response import TemplateResponse
from users.models import User
from events.models import VolunteerApplication

class VMSAdminSite(admin.AdminSite):
    site_header = "Volunteer Management"
    site_title = "VMS Admin"
    index_title = "Dashboard"

    def index(self, request, extra_context=None):
        # Gather stats
        # Real data
        try:
            pending_volunteers = VolunteerApplication.objects.filter(status='PENDING').count()
        except Exception:
            pending_volunteers = 0
            
        # Static data for missing models/features
        context = {
            'pending_evaluations': 1,
            'pending_interviews': 9,
            'volunteers_to_accept': pending_volunteers,
            'volunteer_enquiries': 51,
            'general_enquiries': 12,
            
            'volunteering_hours': 3956,
            'checked_in_volunteers': 118,
            
            'training_enrollments': 0, 
            # Check-in section data can be static for now as seen in image
        }
        
        if extra_context:
            context.update(extra_context)
            
        return super().index(request, extra_context=context)

vms_admin = VMSAdminSite(name='vms_admin')
