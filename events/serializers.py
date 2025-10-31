from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Event, RSVP, Review


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile data"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'full_name', 'bio', 'location', 'profile_picture']


class UserBasicSerializer(serializers.ModelSerializer):
    """Lightweight user serializer for nested representations"""
    full_name = serializers.CharField(source='profile.full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for event reviews"""
    user = UserBasicSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Review
        fields = ['id', 'event', 'user', 'user_id', 'rating', 'comment', 'created_at']
        read_only_fields = ['event', 'user', 'created_at']
    
    def validate_rating(self, value):
        """Ensure rating is between 1 and 5"""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def create(self, validated_data):
        # Remove user_id if present, we'll use context
        validated_data.pop('user_id', None)
        validated_data['user'] = self.context['request'].user
        validated_data['event'] = self.context['event']
        return super().create(validated_data)


class RSVPSerializer(serializers.ModelSerializer):
    """Serializer for RSVP responses"""
    user = UserBasicSerializer(read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    
    class Meta:
        model = RSVP
        fields = ['id', 'event', 'event_title', 'user', 'status', 'created_at', 'updated_at']
        read_only_fields = ['event', 'user', 'created_at', 'updated_at']
    
    def validate_status(self, value):
        """Ensure status is valid"""
        valid_statuses = [choice[0] for choice in RSVP.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value


class EventListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing events"""
    organizer = UserBasicSerializer(read_only=True)
    rsvp_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'location', 'start_time', 'end_time', 
            'organizer', 'is_public', 'rsvp_count', 'average_rating'
        ]


class EventDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with all event information and relations"""
    organizer = UserBasicSerializer(read_only=True)
    rsvp_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    user_rsvp_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'organizer', 'location',
            'start_time', 'end_time', 'is_public', 'created_at', 
            'updated_at', 'rsvp_count', 'average_rating', 'reviews',
            'user_rsvp_status'
        ]
        read_only_fields = ['organizer', 'created_at', 'updated_at']
    
    def get_user_rsvp_status(self, obj):
        """Get current user's RSVP status for this event"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            rsvp = obj.rsvps.filter(user=request.user).first()
            if rsvp:
                return rsvp.status
        return None
    
    def validate(self, data):
        """Ensure end_time is after start_time"""
        if 'start_time' in data and 'end_time' in data:
            if data['end_time'] <= data['start_time']:
                raise serializers.ValidationError({
                    'end_time': 'End time must be after start time.'
                })
        return data
    
    def create(self, validated_data):
        """Set organizer to current user"""
        validated_data['organizer'] = self.context['request'].user
        return super().create(validated_data)


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating events"""
    
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'location', 
            'start_time', 'end_time', 'is_public'
        ]
    
    def validate(self, data):
        """Ensure end_time is after start_time"""
        start = data.get('start_time') or (self.instance.start_time if self.instance else None)
        end = data.get('end_time') or (self.instance.end_time if self.instance else None)
        
        if start and end and end <= start:
            raise serializers.ValidationError({
                'end_time': 'End time must be after start time.'
            })
        return data