import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatRoom, Message, ChatNotification


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time chat functionality.
    """
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        message = text_data_json.get('message', '')
        sender = self.scope['user']

        if message_type == 'chat_message':
            # Save message to database
            await self.save_message(sender, message)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender.get_full_name(),
                    'timestamp': timezone.now().isoformat()
                }
            )
        elif message_type == 'typing':
            # Broadcast typing status
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing',
                    'user': sender.get_full_name(),
                    'is_typing': text_data_json.get('is_typing', False)
                }
            )

    async def chat_message(self, event):
        """
        Send message to WebSocket.
        """
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp']
        }))

    async def typing(self, event):
        """
        Send typing status to WebSocket.
        """
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user': event['user'],
            'is_typing': event['is_typing']
        }))

    @database_sync_to_async
    def save_message(self, sender, message):
        """
        Save message to database.
        """
        chat_room = ChatRoom.objects.get(id=self.room_name)
        message_obj = Message.objects.create(
            chat_room=chat_room,
            sender=sender,
            content=message
        )
        
        # Create notification for other users in the chat
        recipients = [chat_room.customer, chat_room.business.owner]
        for recipient in recipients:
            if recipient != sender:
                ChatNotification.objects.create(
                    chat_room=chat_room,
                    recipient=recipient,
                    notification_type='new_message'
                )
        
        return message_obj 