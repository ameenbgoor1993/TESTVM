from django.urls import path
from .views import (
    BlogListView, BlogDetailView,
    GalleryListView, GalleryDetailView,
    SlideshowListView, SlideshowDetailView,
    SlideshowListView, SlideshowDetailView,
    CodeOfConductListView, CodeOfConductDetailView,
    HomePageListView, HomePageDetailView
)

urlpatterns = [
    path('home-page/', HomePageListView.as_view(), name='home-page-list'),
    path('home-page/<int:pk>/', HomePageDetailView.as_view(), name='home-page-detail'),

    path('blogs/', BlogListView.as_view(), name='blog-list'),
    path('blogs/<int:pk>/', BlogDetailView.as_view(), name='blog-detail'),
    
    path('galleries/', GalleryListView.as_view(), name='gallery-list'),
    path('galleries/<int:pk>/', GalleryDetailView.as_view(), name='gallery-detail'),
    
    path('slideshows/', SlideshowListView.as_view(), name='slideshow-list'),
    path('slideshows/<int:pk>/', SlideshowDetailView.as_view(), name='slideshow-detail'),
    
    path('code-of-conduct/', CodeOfConductListView.as_view(), name='code-of-conduct-list'),
    path('code-of-conduct/<int:pk>/', CodeOfConductDetailView.as_view(), name='code-of-conduct-detail'),
]
