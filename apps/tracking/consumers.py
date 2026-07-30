import json
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()


class TrackingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'tracking_live'

        params = parse_qs(self.scope['query_string'].decode())
        tokens = params.get('token', [])
        if not tokens:
            await self.close()
            return
        token = tokens[0]

        try:
            access = AccessToken(token)
            user = await self.get_user(access['user_id'])
            if not user or not user.is_active:
                await self.close()
                return
            self.scope['user'] = user
        except (TokenError, KeyError):
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def location_update(self, event):
        await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
