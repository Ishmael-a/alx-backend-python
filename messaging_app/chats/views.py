from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from rest_framework import viewsets, filters

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["participants__first_name", "participants__last_name"]
    ordering_fields = ["created_at"]

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
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["sent_at"]

    def create(self, request, *args, **kwargs):
        sender_id = request.data.get("sender_id")
        conversation_id = request.data.get("conversation_id")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = Message.objects.create(
            sender_id=sender_id,
            conversation_id=conversation_id,
            message_body=serializer.validated_data["message_body"]
        )

        return Response(self.get_serializer(message).data, status=201)
