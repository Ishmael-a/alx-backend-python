from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework.response import Response


class MessagePagination(PageNumberPagination):
    """
    Custom pagination for messages.
    Returns 20 messages per page with custom response format.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })


class ConversationPagination(PageNumberPagination):
    """
    Custom pagination for conversations.
    Returns 10 conversations per page.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })


class MessageCursorPagination(CursorPagination):
    """
    Cursor-based pagination for messages (better for real-time chat).
    Ordered by creation time, most recent first.
    """
    page_size = 20
    ordering = '-sent_at'  # Newest first
    cursor_query_param = 'cursor'
    
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })