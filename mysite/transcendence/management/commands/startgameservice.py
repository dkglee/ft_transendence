from django.core.management.base import BaseCommand
from transcendence.service import start_game_service

class Command(BaseCommand):
    help = 'Starts the game service and initializes game sessions'

    def handle(self, *args, **kwargs):
        start_game_service()
        self.stdout.write(self.style.SUCCESS('Successfully started game service and initialized sessions'))
