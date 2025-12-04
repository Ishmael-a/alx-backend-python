from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["user_id", "email", "first_name", "last_name", "phone_number", "role", "created_at"]
        read_only_fields = ["user_id", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='sender',
        write_only=True,
        required=False
    )
    sender_name = serializers.SerializerMethodField()
    conversation_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Message
        fields = [
            'message_id',
            'conversation',
            'conversation_id',
            'sender',
            'sender_id',
            'message_body',
            'is_read',
            'sent_at',
            'updated_at'
        ]
        read_only_fields = ["message_id", "sender", "sent_at", "updated_at"]

    def create(self, validated_data):
        """
        Create a message and associate it with a conversation.
        """
        conversation_id = validated_data.pop('conversation_id')
        
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except Conversation.DoesNotExist:
            raise serializers.ValidationError({
                'conversation_id': 'Conversation does not exist'
            })
        
        # Verify sender is a participant
        sender = validated_data.get('sender')
        if sender and not conversation.participants.filter(id=sender.id).exists():
            raise serializers.ValidationError({
                'conversation': 'You are not a participant of this conversation'
            })
        
        message = Message.objects.create(
            conversation=conversation,
            **validated_data
        )
        return message

    def get_sender_name(self, obj):
        return f"{obj.sender.first_name} {obj.sender.last_name}"

    def validate_message_body(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")
        if len(value) > 5000:
            raise serializers.ValidationError("Message body cannot exceed 5000 characters.")
        return value


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        source='participants'
    )
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "participant_ids",
            "messages",
            "message_count",
            "last_message",
            "created_at",
            "updated_at"
        ]
        read_only_fields = ["conversation_id", "created_at","updated_at"]

    def get_message_count(self, obj):
        return obj.messages.count()

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-sent_at').first()
        return MessageSerializer(last_msg).data if last_msg else None

    def validate_participant_ids(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("A conversation must have at least 2 participants.")
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate participants are not allowed.")
        return value
