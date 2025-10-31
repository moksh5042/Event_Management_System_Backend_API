from rest_framework import permissions


class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow organizers of an event to edit/delete it.
    Read permissions are allowed to any authenticated user.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for safe methods (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for the event organizer
        return obj.organizer == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Generic permission to only allow owners of an object to edit it.
    Assumes the object has a 'user' field.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for safe methods
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for the owner
        return obj.user == request.user