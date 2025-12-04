import django_filters
from django.db.models import Q
from .models import Message, Conversation


class MessageFilter(django_filters.FilterSet):
    """
    Filter class for messages.
    Allows filtering by:
    - Conversation
    - Sender
    - Date range
    - Message content (search)
    """
    # Filter by conversation
    conversation = django_filters.UUIDFilter(field_name='conversation__id')
    
    # Filter by sender
    sender = django_filters.CharFilter(field_name='sender__username', lookup_expr='icontains')
    sender_id = django_filters.NumberFilter(field_name='sender__id')
    
    # Date range filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    date_range = django_filters.DateFromToRangeFilter(field_name='created_at')
    
    # Search in message content
    search = django_filters.CharFilter(method='filter_search')
    
    # Filter by date (specific date)
    date = django_filters.DateFilter(field_name='created_at__date')
    
    class Meta:
        model = Message
        fields = ['conversation', 'sender', 'sender_id', 'created_after', 'created_before']
    
    def filter_search(self, queryset, name, value):
        """
        Custom search filter for message content.
        Searches in message body.
        """
        return queryset.filter(
            Q(message_body__icontains=value)
        )


class ConversationFilter(django_filters.FilterSet):
    """
    Filter class for conversations.
    Allows filtering by:
    - Participants
    - Creation date
    """
    # Filter by participant username
    participant = django_filters.CharFilter(method='filter_participant')
    
    # Filter by participant ID
    participant_id = django_filters.NumberFilter(method='filter_participant_id')
    
    # Date range filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Conversation
        fields = ['created_after', 'created_before']
    
    def filter_participant(self, queryset, name, value):
        """
        Filter conversations by participant username.
        """
        return queryset.filter(
            participants__username__icontains=value
        ).distinct()
    
    def filter_participant_id(self, queryset, name, value):
        """
        Filter conversations by participant ID.
        """
        return queryset.filter(
            participants__id=value
        ).distinct()


class UserMessageFilter(django_filters.FilterSet):
    """
    Filter for messages with specific user involvement.
    Useful for finding all messages to/from a specific user.
    """
    with_user = django_filters.NumberFilter(method='filter_with_user')
    from_user = django_filters.NumberFilter(field_name='sender__id')
    
    class Meta:
        model = Message
        fields = []
    
    def filter_with_user(self, queryset, name, value):
        """
        Filter messages in conversations where the specified user is a participant.
        """
        return queryset.filter(
            conversation__participants__id=value
        ).distinct()