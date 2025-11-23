from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["user_id", "email", "first_name", "last_name", "phone_number", "role", "created_at"]
        read_only_fields = ["user_id", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    sender_id = serializers.CharField(write_only=True, required=False)
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["message_id", "sender", "sender_id", "sender_name", "message_body", "sent_at"]
        read_only_fields = ["message_id", "sender", "sent_at"]

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
    participant_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
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
            "created_at"
        ]
        read_only_fields = ["conversation_id", "created_at"]

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
