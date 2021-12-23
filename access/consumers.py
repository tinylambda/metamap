import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer


class AccessConsumer(AsyncWebsocketConsumer):
    LOGGER = logging.getLogger('django')

    def __init__(self, *args, **kwargs):
        self.group_name = None
        super().__init__(*args, **kwargs)

    async def connect(self):
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.group_name = f'group_{self.group_name}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = text_data or bytes_data
        text_data_json = json.loads(data)
        message = text_data_json['message']
        await self.channel_layer.group_send(self.group_name, {
            'type': 'handle_message',
            'message': message
        })

    async def handle_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
