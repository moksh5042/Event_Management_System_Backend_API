from django.contrib import admin
from .models import UserProfile, Event, RSVP, Review


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'location']
    search_fields = ['user__username', 'full_name', 'location']
    list_filter = ['location']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'location', 'start_time', 'is_public', 'created_at']
    search_fields = ['title', 'description', 'location', 'organizer__username']
    list_filter = ['is_public', 'start_time', 'location']
    date_hierarchy = 'start_time'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'description', 'organizer')
        }),
        ('Location & Time', {
            'fields': ('location', 'start_time', 'end_time')
        }),
        ('Visibility', {
            'fields': ('is_public',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'status', 'created_at']
    search_fields = ['user__username', 'event__title']
    list_filter = ['status', 'created_at']
    date_hierarchy = 'created_at'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'rating', 'created_at']
    search_fields = ['user__username', 'event__title', 'comment']
    list_filter = ['rating', 'created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']