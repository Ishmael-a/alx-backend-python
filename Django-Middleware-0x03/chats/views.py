from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.exceptions import PermissionDenied


from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .permissions import IsParticipantOfConversation, IsMessageSender
from rest_framework.permissions import IsAuthenticated
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

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Get all messages for a specific conversation.
        GET /api/conversations/{id}/messages/
        """
        conversation = self.get_object()

        if not conversation.participants.filter(id=request.user.id).exists():
            return Response(
                {'error': 'You are not allowed to access this conversation.'},
                status=status.HTTP_403_FORBIDDEN
            )
            # raise PermissionDenied(detail="You are not allowed to access this conversation.")

        messages = conversation.messages.all()
        
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
        ).select_related('sender', 'conversation').distinct()
    
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


