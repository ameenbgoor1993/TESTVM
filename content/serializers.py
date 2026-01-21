from rest_framework import serializers
from .models import Blog, Gallery, Slideshow, CodeOfConduct, HomePage

class HomePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePage
        fields = '__all__'


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'

class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = '__all__'

class SlideshowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slideshow
        fields = '__all__'

class CodeOfConductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeOfConduct
        fields = '__all__'
