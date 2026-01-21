from django.db import models

# Import existing models for Proxy definitions
from events.models import Skills, Area, City

class BaseLookupModel(models.Model):
    """Abstract base class for simple lookup models with Arabic/English titles"""
    title_ar = models.CharField(max_length=255, verbose_name="Title (Arabic)")
    title_en = models.CharField(max_length=255, verbose_name="Title (English)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title_en

class AcceptReason(BaseLookupModel):
    class Meta:
        verbose_name = "Accept Reason"
        verbose_name_plural = "Accept Reasons"

class JoiningReason(BaseLookupModel):
    class Meta:
        verbose_name = "Joining Reason"
        verbose_name_plural = "Joining Reasons"

class RejectReason(BaseLookupModel):
    class Meta:
        verbose_name = "Reject Reason"
        verbose_name_plural = "Reject Reasons"

class Clinic(BaseLookupModel):
    class Meta:
        verbose_name = "Clinic"
        verbose_name_plural = "Clinics"

class Profession(BaseLookupModel):
    class Meta:
        verbose_name = "Profession"
        verbose_name_plural = "Professions"

# Proxy Models to move existing models to "Settings" app in Admin
class SkillsProxy(Skills):
    class Meta:
        proxy = True
        verbose_name = "Skill"
        verbose_name_plural = "Skills"

class AreaProxy(Area):
    class Meta:
        proxy = True
        verbose_name = "Area"
        verbose_name_plural = "Areas"

class CityProxy(City):
    class Meta:
        proxy = True
        verbose_name = "City"
        verbose_name_plural = "Cities"
