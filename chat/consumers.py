import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Message
from tickets.models import Ticket


class TicketChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.ticket_id = self.scope['url_route']['kwargs']['ticket_id']
        self.room_group_name = f'ticket_{self.ticket_id}'
        user = self.scope['user']

        if not user.is_authenticated:
            await self.close()
            return

        has_access = await self.check_access(user)
        if not has_access:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        text = data.get('text', '').strip()
        if not text:
            return

        user = self.scope['user']
        message = await self.save_message(user, text)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'text': message.text,
                'sender': user.username,
                'created_at': message.created_at.isoformat(),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'text': event['text'],
            'sender': event['sender'],
            'created_at': event['created_at'],
        }))

    @database_sync_to_async
    def check_access(self, user):
        try:
            ticket = Ticket.objects.get(pk=self.ticket_id)
        except Ticket.DoesNotExist:
            return False
        if user.role == 'admin':
            return True
        if user.role == 'operator':
            return ticket.operator_id == user.id
        return ticket.client_id == user.id

    @database_sync_to_async
    def save_message(self, user, text):
        return Message.objects.create(ticket_id=self.ticket_id, sender=user, text=text)