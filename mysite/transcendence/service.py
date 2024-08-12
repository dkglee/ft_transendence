import threading
import time
from concurrent.futures import ThreadPoolExecutor
from .models import GameSession

def session_thread(session_id, websocket_url, websocket_port):
	# Session Logic Here
	while True:
		# print(f"Session {session_id} is running...")
		time.sleep(5)

def start_game_service():
	num_sessions = 8
	websockets_url = "127.0.0.1"
	websocket_port = 8001

	# 기존 세션 삭제
	GameSession.objects.all().delete()
	
	executor = ThreadPoolExecutor(max_workers=num_sessions)

	for i in range(num_sessions):
		session_id = f"session_{i+1}"

		# Create a new GameSession object
		GameSession.objects.create(
			session_id=session_id,
			websockets_url=websockets_url,
			websockets_port=websocket_port,
			is_active=False
		)

		executor.submit(session_thread, session_id, websockets_url, websocket_port)
