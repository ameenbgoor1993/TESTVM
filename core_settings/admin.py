from django.contrib import admin
from .models import (
    AcceptReason, JoiningReason, RejectReason, Clinic, Profession,
    SkillsProxy, AreaProxy, CityProxy
)

class LookupModelAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'title_ar', 'created_at')
    search_fields = ('title_en', 'title_ar')

@admin.register(AcceptReason)
class AcceptReasonAdmin(LookupModelAdmin):
    pass

@admin.register(JoiningReason)
class JoiningReasonAdmin(LookupModelAdmin):
    pass

@admin.register(RejectReason)
class RejectReasonAdmin(LookupModelAdmin):
    pass

@admin.register(Clinic)
class ClinicAdmin(LookupModelAdmin):
    pass

@admin.register(Profession)
class ProfessionAdmin(LookupModelAdmin):
    pass

# Proxy Admin Registrations
@admin.register(SkillsProxy)
class SkillsProxyAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ar')
    search_fields = ('name_en', 'name_ar')

@admin.register(AreaProxy)
class AreaProxyAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ar')
    search_fields = ('name_en', 'name_ar')
    # list_filter = ('city',)  # City field does not exist on Area model currently


@admin.register(CityProxy)
class CityProxyAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ar')
    search_fields = ('name_en', 'name_ar')
