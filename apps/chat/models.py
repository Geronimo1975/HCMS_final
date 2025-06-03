from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.businesses.models import Business


class ChatRoom(models.Model):
    """
    Model for managing chat rooms between customers and businesses.
    """
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_chat_rooms'
    )
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='business_chat_rooms'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('chat room')
        verbose_name_plural = _('chat rooms')
        unique_together = ['customer', 'business']
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat: {self.customer.get_full_name()} - {self.business.name}"


class Message(models.Model):
    """
    Model for storing chat messages.
    """
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.get_full_name()} in {self.chat_room}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update chat room's updated_at timestamp
        self.chat_room.save()


class MessageAttachment(models.Model):
    """
    Model for storing message attachments.
    """
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to='chat_attachments/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    file_size = models.IntegerField()  # Size in bytes
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('message attachment')
        verbose_name_plural = _('message attachments')
        ordering = ['created_at']

    def __str__(self):
        return f"Attachment: {self.file_name} for {self.message}"


class ChatNotification(models.Model):
    """
    Model for managing chat notifications.
    """
    class NotificationType(models.TextChoices):
        NEW_MESSAGE = 'new_message', _('New Message')
        MESSAGE_READ = 'message_read', _('Message Read')
        TYPING = 'typing', _('Typing')

    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_notifications'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('chat notification')
        verbose_name_plural = _('chat notifications')
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"{self.get_notification_type_display()} - "
            f"{self.chat_room} - {self.recipient.get_full_name()}"
        ) 