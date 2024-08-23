import json
import asyncio
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from .models import GameSession, Player
from .service import GameServiceSingleton
import time

@sync_to_async
def SetSessionActive(session_id, handshake):
    session = GameSession.objects.filter(session_id=session_id).first()
    if session:
        # 예제에서는 handshake로 처리하지만 실제로는 다른 로직이 있을 수 있습니다.
        session.is_active = True
        session.players.add(Player.objects.create(username=handshake))
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
    latency_start_time = None

    async def measure_latency(self):
        while True:
            self.latency_start_time = time.time()
            await self.send(text_data=json.dumps({"type": "ping"}))
            await asyncio.sleep(10)

    async def IsUserInSession(self, user):
        session = GameSession.objects.filter(session_id=self.session_id).first()
        if session:
            if session.players.filter(username=user.username).exists():
                player = Player.objects.filter(username=user.username).first()
                session.players_connected.add(player)
                session.save()
                return True
        else:
            return False

    async def remove_user_from_session(self, user):
        session = GameSession.objects.filter(session_id=self.session_id).first()
        if session:
            if session.players_connected.filter(username=user.username).exists():
                player = Player.objects.filter(username=user.username).first()
                session.players_connected.remove(player)
                session.save()

    async def connect(self):
        # jwt token을 통해 사용자를 인증합니다. #
        # user = self.scope["user"]
        # if user.is_anonymous:
        #     await self.close()

        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        self.roomGroupName = f"game_{self.session_id}"

        # 게임 세션(Thread)과 연결되어 있는 Mutex를 가져옵니다.        
        mutex = getattr(settings, 'GLOBAL_MUTEX', None)
        if mutex is None:
            print("Global mutex not found")
            await self.close()
            return
        else:
           self.mutex = mutex[self.session_id]

        # 게임 세션과 연결되어 있는 Double Buffer(Read, Write)를 가져옵니다
        session_queues = getattr(settings, 'SESSION_QUEUES', None)
        if session_queues:
            self.queue = session_queues.get(self.session_id)
        else:
            self.queue = None

        if self.queue is None:
            print(f"Session {self.session_id} does not exist")
            await self.close()
            return
        else:
            # 해당 유저를 채널 그룹에 추가함. JWT 토큰 구현 이후에는 불필요 #
            await self.channel_layer.group_add(
                self.roomGroupName,
                self.channel_name
            )
            await self.accept()

        self.ping_task = asyncio.create_task(self.measure_latency())        

        # JWT 토큰 구현 이후 #
        # if self.IsUserInSession(user):
        #     await self.channel_layer.group_add(
        #         self.roomGroupName,
        #         self.channel_name
        #     )
        #     await self.accept()
        # else:
        #     await self.close()


    async def disconnect(self, close_code):
        if self.ping_task:
            self.ping_task.cancel()
        user = self.scope["user"]
        await self.channel_layer.group_discard(
            self.roomGroupName,
            self.channel_name
        )
        # JWT 토큰 구현 이후 #
        # self.remove_user_from_session(user)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        print(f"Received message: {text_data} for session: {self.session_id}")

        # pong 메시지 처리
        if "type" in text_data_json and text_data_json["type"] == "pong":
            if self.latency_start_time:
                latency = (time.time() - self.latency_start_time)

                Service = GameServiceSingleton()
                # change player1 to user.username after jwt token implementation
                Service.set_latency(self.session_id, "player1", latency)

                print(f"Latency: {latency}")
                self.latency_start_time = None
            return json.dumps({"type": "pong"})

        # 첫 메시지로 handshake 받기 : JWT 토큰 구현 이후에는 불필요 #
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
            print(f"Received message: {text_data} for session: {self.session_id}")

            if self.queue:
                with self.mutex:
                # 0 -> read, 1 -> write
                    print(f"queue0: {self.queue[0].qsize()}, queue1: {self.queue[1].qsize()}")
                    self.queue[1].put(text_data)

    async def sendMessage(self, event):
        message = event["message"]
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
            await asyncio.sleep(5)
            print(f"Session {self.session_id} did not fill up in time. Starting game...")
            await self.start_game(self.session_id)
        except asyncio.CancelledError:
            print(f"Session {self.session_id} was filled in time. Timer cancelled.")
        finally:
            if self.session_id in GameConsumer.session_timers:
                del GameConsumer.session_timers[self.session_id]
