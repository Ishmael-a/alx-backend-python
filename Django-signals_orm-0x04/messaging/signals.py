from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
# from chats.models import Message, Notification, MessageHistory, User, Conversation
from .models import Message, Notification, MessageHistory, User, Conversation


# Task 0: Signal to create notification when new message is created
# @receiver(post_save, sender=Message)
# def create_notification_on_message(sender, instance, created, **kwargs):
#     """
#     Automatically create a notification when a new message is created.
#     """
#     if created:
#         Notification.objects.create(
#             user=instance.receiver,
#             message=instance,
#             content=f"You have a new message from {instance.sender.email}"
#         )

@receiver(post_save, sender=Message)
def notify_participants(sender, instance, created, **kwargs):
    if not created:
        return

    conversation = instance.conversation  
    sender_user = instance.sender

    # Notify all participants EXCEPT the sender
    participants = conversation.participants.exclude(user_id=sender_user.user_id)

    for user in participants:
        Notification.objects.create(
            user=user,
            message=instance,
            content=f"New message from {sender_user.email}"
        )



# Task 1: Signal to log message edits before updating
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Log the old content of a message before it's updated.
    """
    if instance.pk:  # Check if this is an update (not a new message)
        try:
            old_message = Message.objects.get(pk=instance.pk)
            
            # Check if content has changed
            if old_message.message_body != instance.message_body:
                # Save the old content to MessageHistory
                MessageHistory.objects.create(
                    message=old_message,
                    old_content=old_message.message_body
                )
                
                # Mark message as edited
                instance.edited = True
        except Message.DoesNotExist:
            pass


# Task 2: Signal to delete user-related data when user is deleted
@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    """
    Clean up all related data when a user is deleted.
    Deletes: messages (sent and received), notifications, and message histories.
    """
    # Delete all messages sent by the user
    Message.objects.filter(sender=instance).delete()
    
    # Remove user from all conversation participant lists
    for convo in Conversation.objects.filter(participants=instance):
        convo.participants.remove(instance)

        # Optional: delete empty conversation
        if convo.participants.count() == 0:
            convo.delete()
    
    # Delete all notifications for the user
    Notification.objects.filter(user=instance).delete()
    
    # Note: MessageHistory will be deleted automatically via CASCADE
    # when related messages are deleted