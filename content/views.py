from rest_framework import generics, permissions
from .models import Blog, Gallery, Slideshow, CodeOfConduct, HomePage
from .serializers import BlogSerializer, GallerySerializer, SlideshowSerializer, CodeOfConductSerializer, HomePageSerializer


class HomePageListView(generics.ListAPIView):
    queryset = HomePage.objects.all().order_by('-created_at')
    serializer_class = HomePageSerializer
    permission_classes = [permissions.AllowAny]


class HomePageDetailView(generics.RetrieveAPIView):
    queryset = HomePage.objects.all()
    serializer_class = HomePageSerializer
    permission_classes = [permissions.AllowAny]



class BlogListView(generics.ListAPIView):
    queryset = Blog.objects.all().order_by('-created_at')
    serializer_class = BlogSerializer
    permission_classes = [permissions.AllowAny]


class BlogDetailView(generics.RetrieveAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [permissions.AllowAny]


class GalleryListView(generics.ListAPIView):
    queryset = Gallery.objects.all().order_by('-created_at')
    serializer_class = GallerySerializer
    permission_classes = [permissions.AllowAny]


class GalleryDetailView(generics.RetrieveAPIView):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    permission_classes = [permissions.AllowAny]


class SlideshowListView(generics.ListAPIView):
    queryset = Slideshow.objects.all().order_by('-created_at')
    serializer_class = SlideshowSerializer
    permission_classes = [permissions.AllowAny]


class SlideshowDetailView(generics.RetrieveAPIView):
    queryset = Slideshow.objects.all()
    serializer_class = SlideshowSerializer
    permission_classes = [permissions.AllowAny]


class CodeOfConductListView(generics.ListAPIView):
    queryset = CodeOfConduct.objects.all().order_by('-created_at')
    serializer_class = CodeOfConductSerializer
    permission_classes = [permissions.AllowAny]


class CodeOfConductDetailView(generics.RetrieveAPIView):
    queryset = CodeOfConduct.objects.all()
    serializer_class = CodeOfConductSerializer
    permission_classes = [permissions.AllowAny]
