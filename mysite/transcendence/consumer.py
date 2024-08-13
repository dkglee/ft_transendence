import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # URL에서 세션 id 추출
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        self.roomGroupName = f"game_{self.session_id}"

        # settings에서 session_queues 가져오기
        session_queues = getattr(settings, 'SESSION_QUEUES', None)
        if session_queues:
            self.queue = session_queues.get(self.session_id)
        else:
            self.queue = None

        if self.queue is None:
            print(f"Session {self.session_id} does not exist")
            await self.close()
        else:
            await self.channel_layer.group_add(
                self.roomGroupName,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.roomGroupName,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print(f"Received message: {message} for session: {self.session_id}")
        
        # 큐를 통해 세션 스레드에 데이터 전달
        if self.queue:
            self.queue.put(message)

        await self.channel_layer.group_send(
            self.roomGroupName, {
                "type": "sendMessage",
                "message": message,
            })

    async def sendMessage(self, event):
        # message = event["message"]
        message = "Pong"
        await self.send(text_data=json.dumps({"message": message}))
