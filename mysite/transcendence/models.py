from django.db import models

# Create your models here.
class GameSession(models.Model):
	session_id = models.CharField(max_length=100, unique=True)
	websockets_url = models.URLField()
	websockets_port = models.IntegerField()
	is_active = models.BooleanField(default=False)
	players = models.ManyToManyField('Player', related_name='game_sessions')

	def __str__(self):
		return f"Session {self.session_id} - Active: {self.is_active} - Players: {self.players.all()}"

class Player(models.Model):
	username = models.CharField(max_length=100, unique=True)
	score = models.IntegerField(default=0)

	def __str__(self):
		return f"Player {self.username} - Score: {self.score}"
