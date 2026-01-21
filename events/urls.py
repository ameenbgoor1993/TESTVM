from django.urls import path
from .views import EventListView, EventDetailView, JoinEventView, EventCheckInStatsView, SkillsListView

urlpatterns = [
    path('events/', EventListView.as_view(), name='event-list'),
    path('events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('events/join/', JoinEventView.as_view(), name='join-event'),
    path('events/<int:event_id>/check-in-stats/', EventCheckInStatsView.as_view(), name='event-check-in-stats'),
    path('skills/', SkillsListView.as_view(), name='skills-list'),
]
