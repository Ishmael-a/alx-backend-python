from rest_framework.response import Response
from rest_framework import status, viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, api_view, permission_classes

from django.db.models import Q, Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

from .permissions import IsParticipantOfConversation, IsMessageSender
from .pagination import MessagePagination, ConversationPagination
from .filters import MessageFilter, ConversationFilter

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    
    list: Get all conversations for the authenticated user
    retrieve: Get a specific conversation
    create: Create a new conversation
    update: Update a conversation
    destroy: Delete a conversation
    """
    # queryset = Conversation.objects.all()

    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    lookup_field = "conversation_id"
    lookup_url_kwarg = "conversation_id"

    pagination_class = ConversationPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ConversationFilter

    search_fields = ["participants__first_name", "participants__last_name"]
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        """
        Return only conversations where the user is a participant.
        """
        return Conversation.objects.filter(participants=self.request.user).prefetch_related('participants', 'messages').distinct()

    def perform_create(self, serializer):
        """
        Automatically add the current user as a participant when creating.
        """
        conversation = serializer.save()
        conversation.participants.add(self.request.user)


    # Task 5: Cache the messages view for 60 seconds
    @method_decorator(cache_page(60))
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Get all messages for a specific conversation.
        Cached for 60 seconds.
        GET /api/conversations/{id}/messages/
        """
        conversation = self.get_object()

        if not conversation.participants.filter(id=request.user.id).exists():
            return Response(
                {'error': 'You are not allowed to access this conversation.'},
                status=status.HTTP_403_FORBIDDEN
            )
            # raise PermissionDenied(detail="You are not allowed to access this conversation.")

        # messages = conversation.messages.all()

        # Task 3: Use prefetch_related for optimization with threaded messages
        messages = conversation.messages.prefetch_related(
            'replies',
            'sender',
        ).select_related('sender').filter(parent_message__isnull=True)
        
        # Apply pagination
        paginator = MessagePagination()
        page = paginator.paginate_queryset(messages, request)
        
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """
        Add a participant to the conversation.
        POST /api/conversations/{id}/add_participant/
        Body: {"user_id": 123}
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')

        if not conversation.participants.filter(id=request.user.id).exists():
            return Response(
                {'error': 'You are not allowed to access this conversation.'},
                status=status.HTTP_403_FORBIDDEN
            )
            # raise PermissionDenied(detail="You are not allowed to access this conversation.")
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
            conversation.participants.add(user)
            return Response(
                {'message': f'User {user.username} added to conversation'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        """
        Remove a participant from the conversation.
        POST /api/conversations/{id}/remove_participant/
        Body: {"user_id": 123}
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')

        if not conversation.participants.filter(id=request.user.id).exists():
            return Response(
                {'error': 'You are not allowed to access this conversation.'},
                status=status.HTTP_403_FORBIDDEN
            )
            # raise PermissionDenied(detail="You are not allowed to access this conversation.")
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
            conversation.participants.remove(user)
            return Response(
                {'message': f'User {user.username} removed from conversation'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request, *args, **kwargs):
        participant_ids = request.data.get("participant_ids", [])

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create conversation
        conversation = Conversation.objects.create()
        conversation.participants.set(participant_ids)
        conversation.save()

        return Response(self.get_serializer(conversation).data, status=201)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages.
    
    list: Get all messages (filtered by conversations user is part of)
    retrieve: Get a specific message
    create: Send a new message
    update: Update a message (only sender)
    destroy: Delete a message (only sender)
    """
    # queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ['message_body', 'sender__username']
    ordering_fields = ['sent_at', 'updated_at']
    ordering = ['-sent_at']

    def get_queryset(self):
        """
        Return only messages from conversations where the user is a participant.
        """
        return Message.objects.filter(
            conversation__participants=self.request.user
        ).select_related('sender', 'conversation').prefetch_related('replies').distinct()
    
    def get_permissions(self):
        """
        Use IsMessageSender permission for update and delete operations.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsMessageSender()]
        return [IsAuthenticated(), IsParticipantOfConversation()]
    
    def perform_create(self, serializer):
        """
        Set the sender to the current user when creating a message.
        """
        serializer.save(sender=self.request.user)

    # Task 4: Endpoint to get unread messages using custom manager
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        Get all unread messages for the current user using custom manager.
        GET /api/messages/unread/
        """
        # Use custom manager with .only() optimization
        messages = Message.unread.unread_for_user(request.user)
        
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(messages, request)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    

    # Task 3: Get threaded conversation with replies
    @action(detail=True, methods=['get'])
    def thread(self, request, pk=None):
        """
        Get a message with all its replies in threaded format.
        Uses prefetch_related for optimization.
        GET /api/messages/{id}/thread/
        """
        message = self.get_object()
        
        # Recursively get all replies using prefetch_related
        # messages_with_replies = Message.objects.filter(
        #     pk=message.pk
        # ).prefetch_related(
        #     Prefetch('replies', queryset=Message.objects.select_related('sender'))
        # )

        # Prefetch all replies recursively
        message_with_replies = Message.objects.filter(
            pk=message.pk
        ).select_related('sender', 'conversation').prefetch_related(
            'replies__sender',
            'replies__replies__sender',  # 2 levels deep
            'replies__replies__replies__sender'  # 3 levels deep
        ).only(
            'message_id',
            'message_body',
            'sent_at',
            'updated_at',
            'read',
            'edited',
            'sender__user_id',
            'sender__first_name',
            'sender__last_name',
            'sender__email',
            'conversation__conversation_id'
        ).first()
        
        serializer = self.get_serializer(message_with_replies)
        return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    """
    Task 2: Allow a user to delete their account.
    The post_delete signal will automatically clean up related data.
    DELETE /api/users/delete/
    """
    user = request.user
    
    try:
        user.delete()
        return Response(
            {'message': 'User account and all related data deleted successfully'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
