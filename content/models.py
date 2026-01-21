from django.db import models
from ckeditor.fields import RichTextField

class Blog(models.Model):
    title_ar = models.CharField(max_length=255, verbose_name="Title (Arabic)")
    title_en = models.CharField(max_length=255, verbose_name="Title (English)")
    content = RichTextField(verbose_name="Content")
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    video_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title_en

class Gallery(models.Model):
    title_ar = models.CharField(max_length=255, verbose_name="Title (Arabic)")
    title_en = models.CharField(max_length=255, verbose_name="Title (English)")
    image = models.ImageField(upload_to='gallery_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Galleries"

    def __str__(self):
        return self.title_en

class Slideshow(models.Model):
    title_ar = models.CharField(max_length=255, verbose_name="Title (Arabic)")
    title_en = models.CharField(max_length=255, verbose_name="Title (English)")
    description_ar = models.TextField(verbose_name="Description (Arabic)", blank=True)
    description_en = models.TextField(verbose_name="Description (English)", blank=True)
    image = models.ImageField(upload_to='slideshow_images/', blank=True, null=True)
    video_link = models.URLField(blank=True, null=True)
    link = models.URLField(blank=True, null=True, verbose_name="Link URL")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title_en

class CodeOfConduct(models.Model):
    title_ar = models.CharField(max_length=255, verbose_name="Title (Arabic)")
    title_en = models.CharField(max_length=255, verbose_name="Title (English)")
    content = RichTextField(verbose_name="Content")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Code of Conduct"

    def __str__(self):
        return self.title_en

class HomePage(models.Model):
    title_ar = models.CharField(max_length=255, verbose_name="Title (Arabic)")
    title_en = models.CharField(max_length=255, verbose_name="Title (English)")
    content_ar = RichTextField(verbose_name="Content (Arabic)")
    content_en = RichTextField(verbose_name="Content (English)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Home Page Content"

    def __str__(self):
        return self.title_en
