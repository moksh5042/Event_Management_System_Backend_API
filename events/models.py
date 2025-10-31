from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class UserProfile(models.Model):
    """
    Extended user profile to store additional information.
    Linked one-to-one with Django's built-in User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True, help_text="Short bio about the user")
    location = models.CharField(max_length=255, blank=True)
    profile_picture = models.URLField(blank=True, help_text="URL to profile image")
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class Event(models.Model):
    """
    Main event model. Organizers can create events and manage them.
    Events can be public or private.
    """
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    organizer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='organized_events',
        help_text="User who created this event"
    )
    location = models.CharField(max_length=255, db_index=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_public = models.BooleanField(
        default=True, 
        help_text="Whether this event is visible to all users"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['start_time', 'is_public']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def rsvp_count(self):
        """Get count of users who RSVPed as 'Going'"""
        return self.rsvps.filter(status='Going').count()
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return None


class RSVP(models.Model):
    """
    Tracks user responses to events.
    Each user can have only one RSVP per event.
    """
    STATUS_CHOICES = [
        ('Going', 'Going'),
        ('Maybe', 'Maybe'),
        ('Not Going', 'Not Going'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rsvps')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Maybe')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['event', 'user']
        verbose_name = "RSVP"
        verbose_name_plural = "RSVPs"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.status})"


class Review(models.Model):
    """
    User reviews for events they attended.
    Includes rating (1-5) and optional comment.
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['event', 'user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.rating}★)"