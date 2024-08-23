from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f"user_{self.user_id}"

        # Join the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'task_id': event['task_id'],
            'task_title': event['task_title'],
            'status': event['status'],
        }))

    @staticmethod
    def notify(group_name, message):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(group_name, {
            'type': 'send_notification',
            'message': message['message'],
            'task_id': message['task_id'],
            'task_title': message['task_title'],
            'status': message['status'],
        })

    @staticmethod
    @receiver(post_save, sender=Task)
    def task_changes(sender, instance, created, update_fields=None, **kwargs):
        assigned_user = instance.assigned_to

        if created:
            if assigned_user:
                NotificationConsumer.notify(f"user_{assigned_user.id}", {
                    "message": "You have been assigned a new task.",
                    "task_id": instance.id,
                    "task_title": instance.title,
                    "status": instance.status,
                })
        else:
            if update_fields:
                if 'assigned_to' in update_fields and assigned_user:
                    NotificationConsumer.notify(f"user_{assigned_user.id}", {
                        "message": "Task assignment has been changed.",
                        "task_id": instance.id,
                        "task_title": instance.title,
                        "status": instance.status,
                    })
                elif 'status' in update_fields and assigned_user:
                    NotificationConsumer.notify(f"user_{assigned_user.id}", {
                        "message": "Task status has been updated.",
                        "task_id": instance.id,
                        "task_title": instance.title,
                        "status": instance.status,
                    })
            else:
                if assigned_user:
                    NotificationConsumer.notify(f"user_{assigned_user.id}", {
                        "message": "Task has been updated.",
                        "task_id": instance.id,
                        "task_title": instance.title,
                        "status": instance.status,
                    })
