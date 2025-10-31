from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models  
from rest_framework import viewsets, status, filters
from rest_framework import serializers  
from rest_framework.exceptions import PermissionDenied  

from .models import Event, RSVP, Review, UserProfile
from .serializers import (
    EventListSerializer, 
    EventDetailSerializer,
    EventCreateUpdateSerializer,
    RSVPSerializer, 
    ReviewSerializer,
    UserProfileSerializer
)
from .permissions import IsOrganizerOrReadOnly


class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing events.
    List and retrieve are public, create/update/delete require authentication.
    Only organizers can modify their own events.
    """
    permission_classes = [IsAuthenticatedOrReadOnly, IsOrganizerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location', 'organizer', 'is_public']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['start_time', 'created_at', 'title']
    ordering = ['-start_time']
    
    def get_queryset(self):
        """
        Filter events based on visibility.
        Unauthenticated users see only public events.
        Authenticated users see public events + their own private events.
        """
        queryset = Event.objects.select_related('organizer', 'organizer__profile')
        
        if not self.request.user.is_authenticated:
            return queryset.filter(is_public=True)
        
        # Show public events + user's own events (public or private)
        return queryset.filter(
            models.Q(is_public=True) | models.Q(organizer=self.request.user)
        )
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return EventListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EventCreateUpdateSerializer
        return EventDetailSerializer
    
    def perform_create(self, serializer):
        """Set the organizer to the current user"""
        serializer.save(organizer=self.request.user)
    
    @action(detail=True, methods=['post', 'patch'], permission_classes=[IsAuthenticated])
    def rsvp(self, request, pk=None):
        """
        Handle RSVP to an event.
        POST: Create new RSVP
        PATCH: Update existing RSVP
        """
        event = self.get_object()
        user = request.user
        
        # Check if RSVP already exists
        rsvp, created = RSVP.objects.get_or_create(
            event=event,
            user=user,
            defaults={'status': request.data.get('status', 'Maybe')}
        )
        
        if not created:
            # Update existing RSVP
            serializer = RSVPSerializer(rsvp, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Return newly created RSVP
        serializer = RSVPSerializer(rsvp)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def reviews(self, request, pk=None):
        """
        GET: List all reviews for an event
        POST: Add a review for an event (authenticated users only)
        """
        event = self.get_object()
        
        if request.method == 'GET':
            reviews = event.reviews.select_related('user', 'user__profile').all()
            page = self.paginate_queryset(reviews)
            if page is not None:
                serializer = ReviewSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Check if user already reviewed this event
            if Review.objects.filter(event=event, user=request.user).exists():
                return Response(
                    {'detail': 'You have already reviewed this event.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = ReviewSerializer(
                data=request.data,
                context={'request': request, 'event': event}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class RSVPViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing RSVPs.
    Creating and updating RSVPs is handled through EventViewSet.
    """
    serializer_class = RSVPSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return RSVPs for the current user"""
        return RSVP.objects.filter(user=self.request.user).select_related(
            'event', 'event__organizer'
        )


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reviews.
    Users can only edit/delete their own reviews.
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Return all reviews, filtered by event if specified"""
        queryset = Review.objects.select_related('user', 'user__profile', 'event')
        event_id = self.request.query_params.get('event', None)
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset
    
    def perform_create(self, serializer):
        """Set the user to the current user"""
        event_id = self.request.data.get('event')
        event = get_object_or_404(Event, id=event_id)
        
        # Check if user already reviewed this event
        if Review.objects.filter(event=event, user=self.request.user).exists():
            raise serializers.ValidationError('You have already reviewed this event.')
        
        serializer.save(user=self.request.user, event=event)
    
    def update(self, request, *args, **kwargs):
        """Only allow users to update their own reviews"""
        review = self.get_object()
        if review.user != request.user:
            return Response(
                {'detail': 'You can only edit your own reviews.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Only allow users to delete their own reviews"""
        review = self.get_object()
        if review.user != request.user:
            return Response(
                {'detail': 'You can only delete your own reviews.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user profiles.
    Users can view any profile but only edit their own.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return UserProfile.objects.select_related('user').all()
    
    def perform_update(self, serializer):
        """Ensure users can only update their own profile"""
        if serializer.instance.user != self.request.user:
            raise PermissionDenied('You can only edit your own profile.')
        serializer.save()