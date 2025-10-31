from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, RSVPViewSet, ReviewViewSet, UserProfileViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'rsvps', RSVPViewSet, basename='rsvp')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'profiles', UserProfileViewSet, basename='profile')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]