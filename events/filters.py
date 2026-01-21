from django.contrib import admin
from django.utils import timezone

class EventTimeFilter(admin.SimpleListFilter):
    title = 'Event Time'
    parameter_name = 'event_time'

    def lookups(self, request, model_admin):
        return (
            ('upcoming', 'Upcoming'),
            ('current', 'Current'),
            ('past', 'Past'),
            ('all', 'All'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        
        if self.value() == 'upcoming':
            return queryset.filter(start_date__gt=now)
        elif self.value() == 'current':
            return queryset.filter(start_date__lte=now, end_date__gte=now)
        elif self.value() == 'past':
            return queryset.filter(end_date__lt=now)
        elif self.value() == 'all':
            return queryset
        
        # Default: show all
        return queryset
