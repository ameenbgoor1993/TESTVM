from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm, AdminUserCreationForm
from . import constants

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ('username', 'email', 'is_staff', 'is_volunteer')
    
    # Define fieldsets explicitly to remove default "Personal info" and reorganize
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Contact Info', {'fields': ('email',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'is_volunteer'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'is_staff', 'is_volunteer'), 
        }),
    )

from .models import AdminUser, VolunteerRegistration, AcceptedVolunteer

@admin.register(AdminUser)
class AdminUserAdmin(UserAdmin):
    add_form = AdminUserCreationForm
    form = CustomUserChangeForm
    add_form_template = 'admin/change_form.html' # Force standard form rendering to bypass two-step process
    list_display = ('username', 'email', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Contact Info', {'fields': ('email',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Detailed add_fieldsets matching the form fields + passwords
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email',
                'password1', 'password2',
                'is_staff', 'is_superuser', 'groups'
            ),
        }),
    )

# Removed duplicate CustomUserAdmin




# -------------------------------------------------------------
# Global Message Sending Action
# -------------------------------------------------------------
def send_message_action(modeladmin, request, queryset):
    from django.shortcuts import render, redirect
    from django.contrib import messages
    from .forms import SendCommunicationForm
    from django.core.mail import send_mass_mail
    from django.conf import settings
    from services.sms import SMSService

    if 'apply' in request.POST:
        form = SendCommunicationForm(request.POST)
        if form.is_valid():
            msg_type = form.cleaned_data['message_type']
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['message']
            
            success_count = 0
            error_count = 0
            
            # --- EMAIL ---
            if msg_type in ['email', 'both']:
                from .models import MessageLog
                recipients_with_email = [u for u in queryset if getattr(u, 'email', None)]
                
                for user in recipients_with_email:
                    try:
                        from django.core.mail import send_mail
                        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                        success_count += 1
                        # Log success
                        MessageLog.objects.create(
                            message_type='email',
                            subject=subject,
                            message=body,
                            recipient=user if isinstance(user, User) else None,
                            recipient_email=user.email,
                            status='success',
                            sent_by=request.user
                        )
                    except Exception as e:
                        error_count += 1
                        # Log failure
                        MessageLog.objects.create(
                            message_type='email',
                            subject=subject,
                            message=body,
                            recipient=user if isinstance(user, User) else None,
                            recipient_email=user.email,
                            status='failed',
                            error_message=str(e),
                            sent_by=request.user
                        )

            # --- SMS ---
            if msg_type in ['sms', 'both']:
                from .models import MessageLog
                sms = SMSService()
                # Use mobile_no directly (from Volunteer)
                recipients_with_mobile = [u for u in queryset if getattr(u, 'mobile_no', None)]
                
                for user in recipients_with_mobile:
                    success, response_msg = sms.send_message([user.mobile_no], body)
                    if success:
                        success_count += 1
                        # Log success
                        MessageLog.objects.create(
                            message_type='sms',
                            subject=subject,
                            message=body,
                            recipient=user if isinstance(user, User) else None,
                            recipient_mobile=user.mobile_no,
                            status='success',
                            sent_by=request.user
                        )
                    else:
                        error_count += 1
                        # Log failure
                        MessageLog.objects.create(
                            message_type='sms',
                            subject=subject,
                            message=body,
                            recipient=user if isinstance(user, User) else None,
                            recipient_mobile=user.mobile_no,
                            status='failed',
                            error_message=response_msg,
                            sent_by=request.user
                        )
            
            if error_count == 0:
                modeladmin.message_user(request, f"Message '{subject}' processed for {queryset.count()} users.", messages.SUCCESS)
            
            return redirect(request.get_full_path())
    else:
        form = SendCommunicationForm()

    return render(request, 'admin/users/send_message.html', {
        'form': form,
        'recipients': queryset,
        'selected_ids': request.POST.getlist('_selected_action')
    })
send_message_action.short_description = "Send Message (SMS/Email)"


# -------------------------------------------------------------
# Volunteer Export Actions
# -------------------------------------------------------------
def export_volunteers_to_excel(modeladmin, request, queryset):
    """Export volunteers to Excel"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment
    from django.http import HttpResponse
    
    # If no items selected, export all (filtered)
    if not queryset.exists():
        queryset = modeladmin.get_queryset(request)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Volunteers"
    
    # Headers
    headers = ['Username', 'Email', 'Mobile', 'Gender', 'Birthdate', 'City', 'Age Range', 
               'Nationality', 'National ID', 'Profession', 'Marital Status', 'Volunteer Status', 
               'Has Volunteered Before', 'Skills', 'Date Joined']
    ws.append(headers)
    
    # Style headers
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    # Data rows
    for vol in queryset:
        skills = ', '.join([s.name_en for s in vol.skills.all()])
        ws.append([
            vol.username,
            vol.email,
            vol.mobile_no,
            vol.get_gender_display() if vol.gender else '',
            vol.birthdate.strftime('%Y-%m-%d') if vol.birthdate else '',
            vol.city.name_en if vol.city else '',
            vol.get_age_range_display() if vol.age_range else '',
            vol.nationality,
            vol.national_id,
            vol.profession,
            vol.get_marital_status_display() if vol.marital_status else '',
            vol.get_volunteer_status_display(),
            'Yes' if vol.has_volunteered_before else 'No',
            skills,
            vol.date_joined.strftime('%Y-%m-%d %H:%M')
        ])
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="volunteers.xlsx"'
    wb.save(response)
    return response
export_volunteers_to_excel.short_description = "Export to Excel"


def export_volunteers_to_pdf(modeladmin, request, queryset):
    """Export volunteers to PDF"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from django.http import HttpResponse
    from io import BytesIO
    
    # If no items selected, export all (filtered)
    if not queryset.exists():
        queryset = modeladmin.get_queryset(request)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []
    
    # Title
    styles = getSampleStyleSheet()
    title = Paragraph("<b>Volunteers Report</b>", styles['Title'])
    elements.append(title)
    elements.append(Paragraph("<br/>", styles['Normal']))
    
    # Table data
    data = [['Username', 'Email', 'Mobile', 'Gender', 'City', 'Status', 'Skills']]
    
    for vol in queryset:
        skills = ', '.join([s.name_en for s in vol.skills.all()][:3])  # Limit skills for PDF
        data.append([
            vol.username[:20],
            vol.email[:25],
            vol.mobile_no,
            vol.get_gender_display() if vol.gender else '',
            vol.city.name_en[:15] if vol.city else '',
            vol.get_volunteer_status_display(),
            skills[:30]
        ])
    
    # Create table
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="volunteers.pdf"'
    return response
export_volunteers_to_pdf.short_description = "Export to PDF"


# Export All Actions (ignores selection)
def export_all_volunteers_to_excel(modeladmin, request, queryset):
    """Export ALL volunteers to Excel (ignores selection)"""
    # Always use full queryset
    return export_volunteers_to_excel(modeladmin, request, modeladmin.get_queryset(request))
export_all_volunteers_to_excel.short_description = "Export ALL to Excel"


def export_all_volunteers_to_pdf(modeladmin, request, queryset):
    """Export ALL volunteers to PDF (ignores selection)"""
    # Always use full queryset
    return export_volunteers_to_pdf(modeladmin, request, modeladmin.get_queryset(request))
export_all_volunteers_to_pdf.short_description = "Export ALL to PDF"


from .models import Volunteer

@admin.register(VolunteerRegistration)
class VolunteerRegistrationAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'mobile_no', 'marital_status', 'volunteer_status', 'date_joined')
    search_fields = ('username', 'email', 'first_name_en', 'first_name_ar', 'mobile_no')
    ordering = ('-date_joined',)
    actions = ['accept_volunteer', send_message_action, export_volunteers_to_excel, export_volunteers_to_pdf]
    filter_horizontal = ('skills', 'joining_reasons')
    
    fieldsets = (
         (None, {'fields': ('username', 'email', 'password', 'is_active', 'volunteer_status')}),
         ('Name', {'fields': ('first_name_en', 'middle_name_en', 'last_name_en', 'first_name_ar', 'middle_name_ar', 'last_name_ar')}),
         ('Personal Details', {'fields': ('gender', 'birthdate', 'nationality', 'national_id', 'profession', 'marital_status')}),
         ('Contact Info', {'fields': ('mobile_no', 'address', 'emergency_contact')}),
         ('Extra Experience Info', {'fields': ('city', 'age_range', 'has_volunteered_before', 'experience_description', 'work_link', 'joining_reasons', 'possible_participation_days', 'possible_participation_time')}),
         ('Skills', {'fields': ('skills',)}),
    )

    def has_add_permission(self, request):
        return False
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['username', 'email', 'password']
        return []

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
        return super().changelist_view(request, extra_context)

@admin.register(AcceptedVolunteer)
class AcceptedVolunteerAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'mobile_no', 'marital_status', 'volunteer_status', 'date_joined')
    search_fields = ('username', 'email', 'first_name_en', 'first_name_ar', 'mobile_no')
    ordering = ('-date_joined',)
    actions = ['reject_volunteer', send_message_action, export_volunteers_to_excel, export_volunteers_to_pdf]
    filter_horizontal = ('skills', 'joining_reasons')
    
    fieldsets = (
         (None, {'fields': ('username', 'email', 'password', 'is_active', 'volunteer_status')}),
         ('Name', {'fields': ('first_name_en', 'middle_name_en', 'last_name_en', 'first_name_ar', 'middle_name_ar', 'last_name_ar')}),
         ('Personal Details', {'fields': ('gender', 'birthdate', 'nationality', 'national_id', 'profession', 'marital_status')}),
         ('Contact Info', {'fields': ('mobile_no', 'address', 'emergency_contact')}),
         ('Extra Experience Info', {'fields': ('city', 'age_range', 'has_volunteered_before', 'experience_description', 'work_link', 'joining_reasons', 'possible_participation_days', 'possible_participation_time')}),
         ('Skills', {'fields': ('skills',)}),
    )

    def has_add_permission(self, request):
        return False
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['username', 'email', 'password']
        return []

    def reject_volunteer(self, request, queryset):
        queryset.update(volunteer_status=constants.VOLUNTEER_STATUS_REJECTED)
    reject_volunteer.short_description = "Reject selected volunteers (Move to Registrations)"
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('export-all-excel/', self.admin_site.admin_view(self.export_all_excel_view), name='accepted-volunteer-export-all-excel'),
            path('export-all-pdf/', self.admin_site.admin_view(self.export_all_pdf_view), name='accepted-volunteer-export-all-pdf'),
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
        return super().changelist_view(request, extra_context)

# -------------------------------------------------------------
# Message Log Admin
# -------------------------------------------------------------
from .models import MessageLog
import csv
from django.http import HttpResponse

def export_messages_to_csv(modeladmin, request, queryset):
    """Export selected messages to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="message_logs.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Type', 'Subject', 'Message', 'Recipient', 'Email', 'Mobile', 'Status', 'Error', 'Sent By', 'Sent At'])
    
    for log in queryset:
        writer.writerow([
            log.id,
            log.get_message_type_display(),
            log.subject,
            log.message,
            log.recipient.username if log.recipient else 'N/A',
            log.recipient_email,
            log.recipient_mobile,
            log.get_status_display(),
            log.error_message,
            log.sent_by.username if log.sent_by else 'N/A',
            log.sent_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response
export_messages_to_csv.short_description = "Export to CSV"

@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'message_type', 'subject', 'recipient', 'recipient_email', 'recipient_mobile', 'status', 'sent_by', 'sent_at')
    list_filter = ('message_type', 'status', 'sent_at')
    search_fields = ('subject', 'message', 'recipient__username', 'recipient_email', 'recipient_mobile', 'sent_by__username')
    readonly_fields = ('message_type', 'subject', 'message', 'recipient', 'recipient_email', 'recipient_mobile', 'status', 'error_message', 'sent_by', 'sent_at')
    date_hierarchy = 'sent_at'
    actions = [export_messages_to_csv]
    
    fieldsets = (
        ('Message Details', {
            'fields': ('message_type', 'subject', 'message')
        }),
        ('Recipient Info', {
            'fields': ('recipient', 'recipient_email', 'recipient_mobile')
        }),
        ('Status', {
            'fields': ('status', 'error_message')
        }),
        ('Metadata', {
            'fields': ('sent_by', 'sent_at')
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete logs
        return request.user.is_superuser
