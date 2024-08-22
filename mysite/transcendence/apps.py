import atexit
from django.apps import AppConfig
from transcendence.service import GameServiceSingleton

class TranscendenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transcendence'

    def ready(self):
        # Django 앱이 시작될 때 startgameservice 커맨드를 호출합니다.
        atexit.register(self.cleanup_db)
        try:
            # Singleton 인스턴스를 통해 session_queues를 초기화
            service_instance = GameServiceSingleton()
            self.session_queues = service_instance.get_session_queues()

            # self.session_queues를 Django의 메인 settings 객체에 추가 (전역적으로 접근 가능)
            from django.conf import settings
            settings.SESSION_QUEUES = self.session_queues

        except Exception as e:
            print(f"Error starting game service: {e}")

    def cleanup_db(self):
        # Django 앱이 종료될 때 호출되는 함수입니다.
        from transcendence.models import GameSession, Player
        print("Cleaning up database...")
        GameSession.objects.all().delete()
        Player.objects.filter(game_sessions__isnull=True).delete()
        