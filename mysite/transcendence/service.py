from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from django.apps import apps  # Django 앱을 지연 초기화하는데 사용

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
                queue = Queue()
                session_queues[session_id] = queue
                self.bGameStarted[session_id] = False
                executor.submit(self.session_thread, session_id, queue, websocket_url, websocket_port)

            return session_queues
        
        except Exception as e:
            print(f"Error starting game service: {e}")

    def session_thread(self, session_id, queue, websocket_url, websocket_port):
        # Session Logic Here
        while True:
            if self.bGameStarted[session_id]:
                print(f"Session {session_id} started")
            try:
                data = queue.get(timeout=1)
                if data is not None:
                    print(f"Session {session_id} received data: {data}")
            except:
                pass

    def get_session_queues(self):
        return self.session_queues

    def start_game(self, session_id):
        if session_id in self.session_queues:
            self.bGameStarted[session_id] = True
            print(f"Starting game in session {session_id}")
        else:
            print(f"Session {session_id} not found")
