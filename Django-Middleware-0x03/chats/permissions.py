from rest_framework import permissions    


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    
    - Users must be authenticated
    - Users can only access conversations they are part of
    - Users can only view/edit/delete messages in their conversations
    """
    
    message = "You must be a participant of this conversation to access it."


    def has_permission(self, request, view):
        """
        Check if user is authenticated.
        This is called before has_object_permission.
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is a participant of the conversation.
        Works for both Conversation and Message objects.
        """
        # If the object is a Message, check the conversation
        if hasattr(obj, 'conversation'):
            conversation = obj.conversation
        elif hasattr(obj, 'participants'):
            conversation = obj
        else:
            return False
        
        return conversation.participants.filter(id=request.user.id).exists()


class IsMessageSender(permissions.BasePermission):
    """
    Custom permission to only allow the sender of a message to edit or delete it.
    """
    
    message = "You can only edit or delete your own messages."
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Allow read access to any participant, but write access only to sender.
        """
        # Check if user is a participant first
        is_participant = obj.conversation.participants.filter(
            id=request.user.id
        ).exists()
        
        if not is_participant:
            return False
        
        # For safe methods (GET, HEAD, OPTIONS), allow all participants
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # For unsafe methods (PUT, PATCH, DELETE), only allow the sender
        return obj.sender == request.user
    

class IsConversationParticipant(permissions.BasePermission):
    """
    Permission to check if user is part of a conversation.
    Used specifically for conversation-level operations.
    """
    
    message = "You are not a participant of this conversation."
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user is in the conversation's participants."""
        return obj.participants.filter(id=request.user.id).exists()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Others can only read.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.sender == request.user or obj.created_by == request.user