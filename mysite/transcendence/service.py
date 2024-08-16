import json
import queue
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings
from queue import Queue
from django.apps import apps  # Django 앱을 지연 초기화하는데 사용
from .logics import GameLogic
from threading import Event
from threading import Lock

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
        match = []
        player_contoller = {}
        self.events[session_id].wait()
        # Session Logic Here
        while True:
            if len(match) == 0:
                self.set_match(session_id, match)
                self.match_playercontroller(session_id, match, player_contoller)
            else:
                self.update_match(session_id, match, player_contoller, double_queue, mutex)
        self.bGameStarted[session_id] = False
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

    def set_match(self, session_id, match):
        try:
            GameSession = apps.get_model('transcendence', 'GameSession')

            session = GameSession.objects.get(session_id=session_id)
            if session.players.count() >= 2:
                match.append(GameLogic())
                if (session.players.count() == 2):
                    return None
                match.append(GameLogic())
                if (session.players.count() == 3):
                    match[1].isComputer = True
            else:
                match.append(GameLogic())
                match[0].isComputer = True
        except Exception as e:
            print(f"Error occurred: {e}")

    def match_playercontroller(self, session_id, match, player_controller):
        try:
            GameSession = apps.get_model('transcendence', 'GameSession')

            session = GameSession.objects.get(session_id=session_id)
            
            players = session.players.all()

            for i in range(len(players)):
                player_controller[players[i].username] = match[i // 2].player[i % 2]
        except Exception as e:
            print(f"Error occurred: {e}")

    def update_match(self, session_id, match, player_controller, double_queue, mutex):
        # 0 -> read, 1 -> write
        with mutex:
            double_queue[0], double_queue[1] = double_queue[1], double_queue[0]

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

                print(f"Received message1: {data} for session: {session_id}")

                if username and action:
                    if username in player_controller:
                        player = player_controller[username]
                        if action == "l":
                            print(f"left")
                            player.dx = -5
                        elif action == "r":
                            print(f"right")
                            player.dx = 5
            except queue.Empty:
                # 큐가 비어 있으면 반복문 종료
                break
        
        # 게임 로직 업데이트
        for game in match:
            game.update()
