import atexit
from django.apps import AppConfig
from django.db.models.signals import post_migrate
import time
import threading

class TranscendenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transcendence'

    def ready(self):
        atexit.register(self.cleanup_db)
        print("Am I Doing Again?")

        # 1초 후에 로직을 실행하는 스레드를 시작
        threading.Thread(target=self.delayed_start_service).start()
    
    def delayed_start_service(self):
        # 1초 대기
        time.sleep(1)
        try:
            # Singleton 인스턴스를 통해 session_queues를 초기화
            from transcendence.service import GameServiceSingleton
            service_instance = GameServiceSingleton()
            self.session_queues = service_instance.start_service()

            from django.conf import settings
            settings.SESSION_QUEUES = self.session_queues

            print("Service started after 2 seconds")
        except Exception as e:
            print(f"Error starting game service: {e}")

    def cleanup_db(self):
        # 데이터베이스 정리
        try:
            from transcendence.models import GameSession, Player
            print("Cleaning up database...")
            GameSession.objects.all().delete()
            Player.objects.filter(game_sessions__isnull=True).delete()
            print("Clean Done")
        except Exception as e:
            print(f"Error during cleanup: {e}")
