from django.contrib import admin
from .models import Blog, Gallery, Slideshow, CodeOfConduct, HomePage

@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'title_ar', 'created_at')
    search_fields = ('title_en', 'title_ar')


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'title_ar', 'created_at')
    search_fields = ('title_en', 'title_ar')

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'title_ar', 'created_at')
    search_fields = ('title_en', 'title_ar')

@admin.register(Slideshow)
class SlideshowAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'title_ar', 'created_at')
    search_fields = ('title_en', 'title_ar')

@admin.register(CodeOfConduct)
class CodeOfConductAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'title_ar', 'created_at')
    search_fields = ('title_en', 'title_ar')
