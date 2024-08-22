import json
import queue
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings
from queue import Queue
from django.apps import apps  # Django 앱을 지연 초기화하는데 사용
from .logics import GameLogic
from threading import Event
from threading import Lock
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time

class MatchMetaData:
    def __init__(self):
        self.id = None
        self.player = []
        self.GameLogic = None
        self.winner = None

class GameService:
    def __init__(self):
        self.matches = {}
        self.player_controller = {}
        self.match_num = 0
        self.match_done = 0
        self.winner_queue = Queue()
        self.history = []
        self.session_done = False
    
    def run(self, session_id, double_queue, mutex):
        while not self.session_done:
            if not self.matches:
                print("Setting match")
                self.set_match(session_id)
            else:
                self.update_match(session_id, double_queue, mutex)
                time.sleep(0.05)
        print("Session ended")
        # 세션 종료 후에는 모든 게임 정보를 DB에 저장함
        self.save_game_history()

    def make_match(self, matchId, player1, player2=None):
        match = MatchMetaData()
        match.id = matchId
        match.GameLogic = GameLogic()
        match.GameLogic.matchId = matchId
        match.player.append(player1)
        self.player_controller[player1] = match.GameLogic.player[0]
        if player2:
            match.player.append(player2)
            self.player_controller[player2] = match.GameLogic.player[1]
        else:
            match.GameLogic.isComputer = True
            match.player.append("Computer")
        match.GameLogic.attach(self)
        return match

    def set_match(self, session_id):
        try:
            GameSession = apps.get_model('transcendence', 'GameSession')

            session = GameSession.objects.get(session_id=session_id)

            players = session.players.all()

            if len(players) < 2:
                match = self.make_match('A', players[0].username)
                self.matches['A'] = match
                self.match_num += 1
            if len(players) >= 2:
                match = self.make_match('A', players[0].username, players[1].username)
                self.matches['A'] = match
                self.match_num += 1
            if len(players) == 3:
                match = self.make_match('B', players[2].username)
                self.matches['B'] = match
                self.match_num += 1
            if len(players) == 4:
                match = self.make_match('B', players[2].username, players[3].username)
                self.matches['B'] = match
                self.match_num += 1
        except Exception as e:
            print(f"Error occurred: {e}")

    def update_match(self, session_id, double_queue, mutex):
        # 0 -> read, 1 -> write
        with mutex:
            double_queue[0], double_queue[1] = double_queue[1], double_queue[0]

        # print(f"queue0: {double_queue[0].qsize()}, queue1: {double_queue[1].qsize()}")
        # 0번 큐에서 메시지를 모두 읽어 들이기
        while True:
            try:
                # 0번 큐에서 데이터를 가져옴
                data = double_queue[0].get_nowait()
                
                # 데이터를 JSON으로 파싱한다고 가정
                data_json = json.loads(data)

                # username과 action을 추출
                username = data_json.get("username")
                action = data_json.get("action")

                # print(f"Received message1: {data} for session: {session_id} in Thread")

                if username and action:
                    if username in self.player_controller:
                        player = self.player_controller[username]
                        if action == "l":
                            print(f"left")
                            player.dx = -5
                        elif action == "r":
                            print(f"right")
                            player.dx = 5
            except queue.Empty:
                break
        
        # 게임 로직 업데이트
        try:
            for game in self.matches.values():
                # print("hi")
                game.GameLogic.update()
                # print("bye")
            self.send_update_message(session_id)
        except Exception as e:
            print(f"Error occurred: {e}")

    def send_update_message(self, session_id):
        # 게임 상태를 클라이언트에게 전송하는 로직
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"game_{session_id}",
            {
                "type": "sendMessage",
                "message": "update"
            }
        )

    # 게임이 끝났을 때 호출되는 함수
    def update(self, matchId, winner):
        print(f"Match {matchId} ended")
        finished_match = self.matches.pop(matchId)
        self.match_done += 1
        self.winner_queue.put(finished_match.player[winner])
        # 게임이 끝났다는 것을 클라이언트에게 알리는 로직 필요함
        
        # 게임의 정보를 기록하는 로직
        finished_match.GameLogic.detach(self)
        finished_match.GameLogic = None
        finished_match.winner = finished_match.player[winner]
        print(f"Winner: {finished_match.winner}")
        self.history.append(finished_match)
        
        # 결승전을 세팅함
        if self.match_done == self.match_num and self.match_num == 2:
            match = self.make_match('F', self.winner_queue.get(), self.winner_queue.get())
            self.matches['F'] = match
        elif self.match_done == self.match_num and self.match_num == 1:
            # 애초에 매치가 1개밖에 없었을 경우
            print("Only one match")
            self.match_done = 0
            self.match_num = 0
            self.session_done = True
        # 결승전이 끝났을 경우의 로직을 작성함
        if (matchId == 'F'):
            self.session_done = True
    
    def save_game_history(self):
        # 게임의 히스토리를 DB에 저장하는 로직
        # TODO: GameHistory 모델을 만들어야 함
        try:
            GameHistory = apps.get_model('transcendence', 'GameHistory')
            for match in self.history:
                game_history = GameHistory(
                    match_id=match.id,
                    player1=match.player[0],
                    player2=match.player[1],
                    winner=match.winner
                )
                game_history.save()
        except Exception as e:
            print(f"Error occurred: {e}")

class GameServiceSingleton:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameServiceSingleton, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.bGameStarted = {}
            self.events = {}
            self.mutex = {}
            self.session_queues = self.start_service()
            self._initialized = True

    def start_service(self):
        # Django 앱이 완전히 로드된 후에 모델을 가져오기 위해 apps.get_model 사용
        print("Starting game service...")

        try:
            GameSession = apps.get_model('transcendence', 'GameSession')
            num_sessions = 8
            websocket_url = "127.0.0.1"
            websocket_port = 8001

            # 기존 세션 삭제
            GameSession.objects.all().delete()

            executor = ThreadPoolExecutor(max_workers=num_sessions)
            session_queues = {}

            for i in range(num_sessions):
                session_id = f"session_{i+1}"
                GameSession.objects.create(
                    session_id=session_id,
                    websocket_url=websocket_url,
                    websocket_port=websocket_port,
                    is_active=False
                )
                queue_read = Queue()
                queue_write = Queue()
                session_queues[session_id] = [queue_read, queue_write]
                self.bGameStarted[session_id] = False
                self.events[session_id] = Event()
                self.mutex[session_id] = Lock()
                executor.submit(self.session_thread, session_id, session_queues[session_id], websocket_url, websocket_port, self.mutex[session_id])

            settings.GLOBAL_MUTEX = self.mutex

            return session_queues
        
        except Exception as e:
            print(f"Error starting game service: {e}")

    def session_thread(self, session_id, double_queue, websocket_url, websocket_port, mutex):
        while True:
            self.events[session_id].wait()
            print("Game started")
            Service = GameService()
            Service.run(session_id, double_queue, mutex)
            self.events[session_id].clear()

    def get_session_queues(self):
        return self.session_queues

    def start_game(self, session_id):
        if session_id in self.session_queues:
            self.bGameStarted[session_id] = True
            self.events[session_id].set()
            print(f"Starting game in session {session_id}")
        else:
            print(f"Session {session_id} not found")
    
    def set_max_match(self, max_match):
        self.max_match = max_match
