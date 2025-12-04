from django.db import models
from django.contrib.auth.models import BaseUserManager
# from .models import Message



class UserManager(BaseUserManager):
    def get_by_natural_key(self, username):
        return self.get(email=username.lower())

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_password(password)   # uses hashed password field
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


# Custom Manager for Unread Messages (Task 4)
class UnreadNotificationsManager(models.Manager):
    def unread_for_user(self, user):
        return self.filter(user=user, is_read=False).select_related('message', 'message__sender', 'message__conversation')
    

class UnreadMessagesManager(models.Manager):
    def unread_for_user(self, user):
        """Return unread messages for a user"""
        from .models import Message
        return Message.objects.filter(
            notifications__user=user,
            notifications__is_read=False
        ).select_related('sender', 'conversation'
        ).prefetch_related('replies'
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
        ).distinct()
