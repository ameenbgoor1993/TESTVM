import re

with open("users/admin.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace exports
content = content.replace("vol.username,", "vol.account.username,")
content = content.replace("vol.email,", "vol.account.email,")
content = content.replace('vol.username[:20],', 'vol.account.username[:20],')
content = content.replace('vol.email[:25],', 'vol.account.email[:25],')
content = content.replace("vol.mobile_no,", "vol.account.mobile_no,")
content = content.replace("vol.date_joined.strftime", "vol.account.date_joined.strftime")

# Replace VolunteerRegistrationAdmin class
vr_admin_pattern = r"class VolunteerRegistrationAdmin\(admin\.ModelAdmin\):.+?def changelist_view.*?return super\(\)\.changelist_view\(request, extra_context\)"
import sys

NEW_VR_ADMIN = """class VolunteerRegistrationAdmin(admin.ModelAdmin):
    def username(self, obj): return obj.account.username
    username.admin_order_field = 'account__username'
    
    def email(self, obj): return obj.account.email
    email.admin_order_field = 'account__email'
    
    def mobile_no(self, obj): return obj.account.mobile_no
    mobile_no.admin_order_field = 'account__mobile_no'
    
    def date_joined(self, obj): return obj.account.date_joined
    date_joined.admin_order_field = 'account__date_joined'

    list_display = ('username', 'email', 'mobile_no', 'marital_status', 'volunteer_status', 'date_joined')
    search_fields = ('account__username', 'account__email', 'first_name_en', 'first_name_ar', 'account__mobile_no')
    ordering = ('-account__date_joined',)
    actions = ['accept_volunteer', send_message_action, export_volunteers_to_excel, export_volunteers_to_pdf]
    filter_horizontal = ('skills', 'joining_reasons')
    
    readonly_fields = ('username', 'email', 'mobile_no', 'date_joined')
    
    fieldsets = (
         ('Account Overview', {'fields': ('username', 'email', 'mobile_no', 'date_joined', 'volunteer_status')}),
         ('Name', {'fields': ('first_name_en', 'middle_name_en', 'last_name_en', 'first_name_ar', 'middle_name_ar', 'last_name_ar')}),
         ('Personal Details', {'fields': ('gender', 'birthdate', 'nationality', 'national_id', 'profession', 'marital_status')}),
         ('Contact Info', {'fields': ('address', 'emergency_contact')}),
         ('Extra Experience Info', {'fields': ('city', 'age_range', 'has_volunteered_before', 'experience_description', 'work_link', 'joining_reasons', 'possible_participation_days', 'possible_participation_time')}),
         ('Skills', {'fields': ('skills',)}),
    )

    def has_add_permission(self, request):
        return False

    def accept_volunteer(self, request, queryset):
        queryset.update(volunteer_status=constants.VOLUNTEER_STATUS_ACCEPTED)
    accept_volunteer.short_description = "Accept selected volunteers"
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('export-all-excel/', self.admin_site.admin_view(self.export_all_excel_view), name='volunteer-export-all-excel'),
            path('export-all-pdf/', self.admin_site.admin_view(self.export_all_pdf_view), name='volunteer-export-all-pdf'),
        ]
        return custom_urls + urls
    
    def export_all_excel_view(self, request):
        queryset = self.get_queryset(request)
        return export_volunteers_to_excel(self, request, queryset)
    
    def export_all_pdf_view(self, request):
        queryset = self.get_queryset(request)
        return export_volunteers_to_pdf(self, request, queryset)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['export_all_excel_url'] = 'export-all-excel/'
        extra_context['export_all_pdf_url'] = 'export-all-pdf/'
        return super().changelist_view(request, extra_context)"""

content = re.sub(vr_admin_pattern, NEW_VR_ADMIN, content, flags=re.DOTALL)

NEW_ACC_ADMIN = NEW_VR_ADMIN.replace("VolunteerRegistrationAdmin", "AcceptedVolunteerAdmin").replace(
    "accept_volunteer", "reject_volunteer"
).replace(
    "Accept selected volunteers", "Reject selected volunteers (Move to Registrations)"
).replace(
    "queryset.update(volunteer_status=constants.VOLUNTEER_STATUS_ACCEPTED)", "queryset.update(volunteer_status=constants.VOLUNTEER_STATUS_REJECTED)"
).replace("name='volunteer-export", "name='accepted-volunteer-export")

acc_admin_pattern = r"class AcceptedVolunteerAdmin\(admin\.ModelAdmin\):.+?def changelist_view.*?return super\(\)\.changelist_view\(request, extra_context\)"
content = re.sub(acc_admin_pattern, NEW_ACC_ADMIN, content, flags=re.DOTALL)

with open("users/admin.py", "w", encoding="utf-8") as f:
    f.write(content)
print("done rewriting users/admin.py")
