import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager, UnreadNotificationsManager, UnreadMessagesManager

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=150, null=False, blank=False)
    last_name = models.CharField(max_length=150, null=False, blank=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    # password_hash = models.CharField(max_length=128, null=False, blank=False)

    objects: UserManager = UserManager()


    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('moderator', 'Moderator'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest', null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    def __str__(self):
        return self.email
    


class Conversation(models.Model):
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        db_table = 'conversations'

    def __str__(self):
        return f"Conversation {self.conversation_id}"
    
    
class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read = models.BooleanField(default=False)
    # Track if message has been edited
    edited = models.BooleanField(default=False)

    unread = UnreadMessagesManager()

    parent_message = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )

    class Meta:
        ordering = ['-sent_at']
        db_table = 'messages'
        indexes = [
            models.Index(fields=['conversation', '-sent_at']),
            models.Index(fields=['parent_message']),
            models.Index(fields=['sender', '-sent_at']),
            # models.Index(fields=['receiver', '-sent_at']),
        ]

    def __str__(self):
        return f"Message from {self.sender.first_name} {self.sender.last_name} with email {self.sender.email}"


class Notification(models.Model):
    """Notification model to store user notifications"""
    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    unread = UnreadNotificationsManager()
    
    class Meta:
        ordering = ['-timestamp']
        db_table = 'notifications'
    
    def __str__(self):
        return f"Notification for {self.user.email}"
    

class MessageHistory(models.Model):
    """Store message edit history"""
    history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-edited_at']
        db_table = 'message_history'
    
    def __str__(self):
        return f"History for message {self.message.message_id}"