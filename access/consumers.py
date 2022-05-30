import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer


class AccessConsumer(AsyncWebsocketConsumer):
    LOGGER = logging.getLogger('django')

    def __init__(self, *args, **kwargs):
        self.group_name = None
        super().__init__(*args, **kwargs)

    async def connect(self):
        user = self.scope['user']
        self.LOGGER.info('user is %s', user)
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.group_name = f'group_{self.group_name}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.say_hi()

    async def say_hi(self):
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'handle_message',
                'message': f'{self.channel_name} joined!',
            },
        )

    async def say_bye(self):
        await self.channel_layer.group_send(
            self.group_name,
            {'type': 'handle_message', 'message': f'{self.channel_name} left!'},
        )

    async def disconnect(self, code):
        await self.say_bye()
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = text_data or bytes_data
        text_data_json = json.loads(data)
        message = text_data_json['message']
        await self.channel_layer.group_send(
            self.group_name, {'type': 'handle_message', 'message': message}
        )

    async def handle_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))
