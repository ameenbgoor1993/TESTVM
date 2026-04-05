from django.contrib import admin
from django import forms
from django.db import models
from .models import Event, VolunteerApplication, Area
from .filters import EventTimeFilter

# -------------------------------------------------------------
# Event Export Actions
# -------------------------------------------------------------
def export_events_to_excel(modeladmin, request, queryset):
    """Export events to Excel"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment
    from django.http import HttpResponse
    
    # If no items selected, export all (filtered)
    if not queryset.exists():
        queryset = modeladmin.get_queryset(request)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Events"
    
    # Headers
    headers = ['Title', 'Category', 'Location', 'Start Date', 'End Date', 
               'Registration Start', 'Registration End', 'Gender Preference', 'Age Range',
               'Required Volunteers', 'Extra Volunteers', 'Cities', 'Skills', 'Event Admin']
    ws.append(headers)
    
    # Style headers
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    # Data rows
    for event in queryset:
        cities = ', '.join([c.name_en for c in event.cities.all()])
        skills = ', '.join([s.name_en for s in event.skills.all()])
        ws.append([
            event.title,
            event.get_category_display(),
            event.location,
            event.start_date.strftime('%Y-%m-%d %H:%M'),
            event.end_date.strftime('%Y-%m-%d %H:%M'),
            event.registration_start_datetime.strftime('%Y-%m-%d %H:%M') if event.registration_start_datetime else '',
            event.registration_end_datetime.strftime('%Y-%m-%d %H:%M') if event.registration_end_datetime else '',
            event.get_gender_preference_display(),
            event.get_age_range_display(),
            event.required_volunteers,
            event.extra_volunteers,
            cities,
            skills,
            event.event_admin.username if event.event_admin else ''
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
    response['Content-Disposition'] = 'attachment; filename="events.xlsx"'
    wb.save(response)
    return response
export_events_to_excel.short_description = "Export to Excel"


def export_events_to_pdf(modeladmin, request, queryset):
    """Export events to PDF"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
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
    title = Paragraph("<b>Events Report</b>", styles['Title'])
    elements.append(title)
    elements.append(Paragraph("<br/>", styles['Normal']))
    
    # Table data
    data = [['Title', 'Category', 'Location', 'Start Date', 'End Date', 'Volunteers', 'Status']]
    
    for event in queryset:
        data.append([
            event.title[:30],
            event.get_category_display()[:15],
            event.location[:20],
            event.start_date.strftime('%Y-%m-%d'),
            event.end_date.strftime('%Y-%m-%d'),
            str(event.required_volunteers),
            'Active' if event.show_in_home_page else 'Hidden'
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
    response['Content-Disposition'] = 'attachment; filename="events.pdf"'
    return response
export_events_to_pdf.short_description = "Export to PDF"


# Export All Actions (ignores selection)
def export_all_events_to_excel(modeladmin, request, queryset):
    """Export ALL events to Excel (ignores selection)"""
    # Always use full queryset
    return export_events_to_excel(modeladmin, request, modeladmin.get_queryset(request))
export_all_events_to_excel.short_description = "Export ALL to Excel"


def export_all_events_to_pdf(modeladmin, request, queryset):
    """Export ALL events to PDF (ignores selection)"""
    # Always use full queryset
    return export_events_to_pdf(modeladmin, request, modeladmin.get_queryset(request))
export_all_events_to_pdf.short_description = "Export ALL to PDF"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'start_date', 'end_date', 'show_in_home_page')
    list_filter = (EventTimeFilter, 'category', 'show_in_home_page', 'start_date')
    search_fields = ('title', 'location')
    filter_horizontal = ('skills', 'cities', 'areas')
    actions = [export_events_to_excel, export_events_to_pdf]
    
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput}, # Default
    }

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['gender_preference'].widget = forms.RadioSelect(choices=Event.GENDER_PREFERENCE_CHOICES)
        return form

    class Media:
        js = ('events/js/event_admin.js',)
        css = {
            'all': ('events/css/event_admin.css',)
        }
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'cities', 'areas', 'location')
        }),
        ('Dates & Registration', {
            'fields': ('start_date', 'end_date', 'registration_start_datetime', 'registration_end_datetime')
        }),
        ('Capacity & Requirements', {
            'fields': (
                'gender_preference',
                ('required_volunteers', 'extra_volunteers'),
                ('required_males', 'required_females'),
                ('extra_males', 'extra_females'),
                'min_participation_time_slots', 'skills'
            )
        }),
        ('Flags', {
            'fields': ('show_in_home_page', 'send_notification_to_volunteer')
        }),
        ('Media', {
            'fields': ('featured_image',)
        }),
        ('Administration', {
            'fields': ('event_admin',)
        }),
        ('Proponent Information', {
            'fields': ('proponent_name', 'proponent_mobile', 'proponent_email')
        }),
        ('Target Audience', {
            'fields': ('age_range',)
        }),
    )
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('export-all-excel/', self.admin_site.admin_view(self.export_all_excel_view), name='event-export-all-excel'),
            path('export-all-pdf/', self.admin_site.admin_view(self.export_all_pdf_view), name='event-export-all-pdf'),
        ]
        return custom_urls + urls
    
    def export_all_excel_view(self, request):
        queryset = self.get_queryset(request)
        return export_events_to_excel(self, request, queryset)
    
    def export_all_pdf_view(self, request):
        queryset = self.get_queryset(request)
        return export_events_to_pdf(self, request, queryset)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['export_all_excel_url'] = 'export-all-excel/'
        extra_context['export_all_pdf_url'] = 'export-all-pdf/'
        return super().changelist_view(request, extra_context)



@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    search_fields = ('name_en', 'name_ar')
    list_display = ('name_en', 'name_ar')

from .models import Attendance

class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 1
    fields = ('check_in_time', 'check_out_time', 'area', 'notes', 'duration_display')
    readonly_fields = ('duration_display',)
    autocomplete_fields = ['area']

    def duration_display(self, obj):
        return obj.duration
    duration_display.short_description = "Duration"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "area":
            # Try to filter areas by the parent application's event
            # In Inline, getting the parent object is tricky.
            # We can rely on autocomplete_fields or use a trick if needed.
            # For now, let's list all areas or rely on standard behavior.
            # Ideally we want `kwargs['queryset'] = Area.objects.filter(events=parent_event)`
            pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Re-register with the new configuration
@admin.register(VolunteerApplication)
class VolunteerApplicationAdmin(admin.ModelAdmin):
    list_display = ('volunteer', 'event', 'status', 'total_hours_display')
    list_filter = ('status', 'event')
    search_fields = ('volunteer__account__username', 'volunteer__first_name_en', 'event__title')
    readonly_fields = ('volunteer', 'event') 
    actions = ['accept_application', 'reject_application']
    inlines = [AttendanceInline]

    def total_hours_display(self, obj):
        import datetime
        durations = [a.duration for a in obj.attendances.all() if a.duration]
        return sum(durations, datetime.timedelta(0))
    total_hours_display.short_description = "Total Hours"

    def accept_application(self, request, queryset):
        queryset.update(status=constants.APP_STATUS_ACCEPTED)
    accept_application.short_description = "Accept selected applications"

    def reject_application(self, request, queryset):
        queryset.update(status=constants.APP_STATUS_REJECTED)
    reject_application.short_description = "Reject selected applications"
