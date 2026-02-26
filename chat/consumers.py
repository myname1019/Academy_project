# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    """
    현재 프로젝트는 HTTP 기반 DM을 사용 중이라 WebSocket은 필수는 아닙니다.
    다만 chat/routing.py, config/asgi.py에서 consumers.ChatConsumer를 import하므로
    import 에러 방지를 위해 최소 Consumer를 제공합니다.
    """

    async def connect(self):
        await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        pass

    async def disconnect(self, close_code):
        pass