from django.db import models

# Create your models here.
class GameSession(models.Model):
	session_id = models.CharField(max_length=100, unique=True)
	websocket_url = models.URLField()
	websocket_port = models.IntegerField()
	is_active = models.BooleanField(default=False)
	players = models.ManyToManyField('Player', related_name='game_sessions')
	players_connected = models.ManyToManyField('Player', related_name='game_sessions_connected')

	def __str__(self):
		return f"Session {self.session_id} - Active: {self.is_active} - Players: {self.players.all()}"

class Player(models.Model):
	username = models.CharField(max_length=100, unique=True)
	score = models.IntegerField(default=0)

	def __str__(self):
		return f"Player {self.username} - Score: {self.score}"

class Match(models.Model):
	player1 = models.CharField(max_length=100, null=True, blank=True)
	player2 = models.CharField(max_length=100, null=True, blank=True)
	winner = models.CharField(max_length=100, null=True, blank=True)

	def __str__(self):
		player1_name = self.player1 if self.player1 else "Unknown"
		player2_name = self.player2 if self.player2 else "Unknown"
		return f"Match {self.id}: {player1_name} vs {player2_name}"


class SessionHistory(models.Model):
	match = models.ManyToManyField(Match, related_name='match_history')
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"SessionHistory {self.id} - Matches: {self.match.count()}"
