import json
import asyncio
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from .models import GameSession, Player
from .service import GameServiceSingleton
import time

class GameConsumer(AsyncWebsocketConsumer):
    session_timers = {}
    latency_start_time = None

    async def measure_latency(self):
        while True:
            self.latency_start_time = time.time()
            await self.send(text_data=json.dumps({"type": "ping"}))
            await asyncio.sleep(10)
    
    @sync_to_async
    def get_session(self):
        return GameSession.objects.filter(session_id=self.session_id).first()

    @sync_to_async
    def get_player(self, username):
        return Player.objects.filter(username=username).first()

    @sync_to_async
    def create_player(self, username):
        return Player.objects.create(username=username)

    @sync_to_async
    def session_player_exists(self, session, username):
        return session.players.filter(username=username).exists()

    @sync_to_async
    def add_player_to_session(self, session, player):
        session.players.add(player)
        session.players_connected.add(player)
        session.is_active = True
        session.save()

    async def IsSessionFull(self):
        session = await self.get_session()
        if session:
            if await sync_to_async(session.players.count)() == 4:
                return True
            else:
                return False
        else:
            return False

    async def IsUserInSession(self, user):
        session = await self.get_session()
        player = await self.get_player(user.username)
        
        if session and player:
            if not await self.session_player_exists(session, user.username):
                await self.add_player_to_session(session, player)
            return True
        else:
            new_player = await self.create_player(user.username)
            await self.add_player_to_session(session, new_player)
            return True
        return True
    
        # Final Version #
            # if session:
            #     if session.players.filter(username=user.username).exists():
            #         player = Player.objects.filter(username=user.username).first()
            #         session.players_connected.add(player)
            #         session.save()
            #         return True
            # else:
            #     return False

    async def remove_user_from_session(self, user):
        session = await self.get_session()
        if session:
            player = await self.get_player(user.username)
            if player and session.players_connected.filter(username=user.username).exists():
                session.players_connected.remove(player)
                session.save()

    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()

        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        self.roomGroupName = f"game_{self.session_id}"

        self.username = user.username
        self.user_channel_name = f"user_{self.username}"

        print(f"User {self.username} connected to session {self.session_id}")

        mutex = getattr(settings, 'GLOBAL_MUTEX', None)
        if mutex is None:
            print("Global mutex not found")
            await self.close()
            return
        else:
            self.mutex = mutex[self.session_id]

        session_queues = getattr(settings, 'SESSION_QUEUES', None)
        if session_queues:
            self.queue = session_queues.get(self.session_id)
        else:
            self.queue = None

        if self.queue is None:
            print(f"Session {self.session_id} does not exist")
            await self.close()
            return

        if await self.IsUserInSession(user):
            await self.channel_layer.group_add(
                self.roomGroupName,
                self.channel_name
            )
            await self.channel_layer.group_add(
                self.user_channel_name,
                self.channel_name
            )
            await self.accept()

            bIsFull = await self.IsSessionFull()
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

            self.ping_task = asyncio.create_task(self.measure_latency())        
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'ping_task') and self.ping_task:
            self.ping_task.cancel()
        # user = self.scope["user"]
        await self.channel_layer.group_discard(
            self.roomGroupName,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            self.user_channel_name,
            self.channel_name
        )


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        if "type" in text_data_json and text_data_json["type"] == "pong":
            if self.latency_start_time:
                latency = (time.time() - self.latency_start_time)

                Service = GameServiceSingleton()
                Service.set_latency(self.session_id, self.username, latency)

                print(f"Latency: {latency}")
                self.latency_start_time = None
            return json.dumps({"type": "pong"})
        else:
            if self.queue:
                with self.mutex:
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

    async def disconnect_message(self, event):
        await self.close()
