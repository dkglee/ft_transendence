import json
import asyncio
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from .models import GameSession, Player
from .service import GameServiceSingleton

@sync_to_async
def SetSessionActive(session_id, handshake):
    session = GameSession.objects.filter(session_id=session_id).first()
    if session:
        # 예제에서는 handshake로 처리하지만 실제로는 다른 로직이 있을 수 있습니다.
        session.is_active = True
        session.save()
    else:
        print(f"Session {session_id} does not exist")
        return False
    
    if session.players.count() == 4:
        return True
    else:
        return False

class GameConsumer(AsyncWebsocketConsumer):
    session_timers = {}

    async def connect(self):
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        self.roomGroupName = f"game_{self.session_id}"

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
        
        # 첫 메시지로 handshake 받기
        if "handshake" in text_data_json:
            handshake = text_data_json["handshake"]

            print(f"Received handshake: {handshake} for session {self.session_id}")

            bIsFull = await SetSessionActive(self.session_id, handshake)
            
            if bIsFull:
                print(f"Session {self.session_id} is full. Starting game...")
                await self.start_game(self.session_id)
                if self.session_id in GameConsumer.session_timers:
                    GameConsumer.session_timers[self.session_id].cancel()
                    del GameConsumer.session_timers[self.session_id]
            else:
                if self.session_id not in GameConsumer.session_timers:
                    timer_task = asyncio.create_task(self.start_game_after_timeout())
                    GameConsumer.session_timers[self.session_id] = timer_task

        # 그 외의 메시지 처리 (예: username 기반 메시지)
        else:
            message = text_data_json.get("message", "")
            print(f"Received message: {message} for session: {self.session_id}")
            
            if self.queue:
                self.queue.put(message)

            await self.channel_layer.group_send(
                self.roomGroupName, {
                    "type": "sendMessage",
                    "message": message,
                })
            
    async def sendMessage(self, event):
        message = "Pong"
        await self.send(text_data=json.dumps({"message": message}))

    async def start_game(self, session_id):
        GameServiceSingleton().start_game(session_id)
        await self.channel_layer.group_send(
            self.roomGroupName, {
                "type": "sendMessage",
                "message": "Game Started",
            })

    async def start_game_after_timeout(self):
        try:
            await asyncio.sleep(20)
            print(f"Session {self.session_id} did not fill up in time. Starting game...")
            await self.start_game(self.session_id)
        except asyncio.CancelledError:
            print(f"Session {self.session_id} was filled in time. Timer cancelled.")
        finally:
            if self.session_id in GameConsumer.session_timers:
                del GameConsumer.session_timers[self.session_id]
