import atexit
from django.apps import AppConfig
from django.core.management import call_command

class TranscendenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transcendence'

    def ready(self):
        # Django 앱이 시작될 때 startgameservice 커맨드를 호출합니다.
        atexit.register(self.cleanup_db)
        try:
            call_command('startgameservice')
        except Exception as e:
            # 에러 핸들링을 추가할 수 있습니다.
            print(f"Error starting game service: {e}")

    def cleanup_db(self):
        # Django 앱이 종료될 때 호출되는 함수입니다.
        from transcendence.models import GameSession
        print("Cleaning up database...")
        GameSession.objects.all().delete()
