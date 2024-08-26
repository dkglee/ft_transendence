from queue import Queue
from threading import Lock
from .models import Match, Player, SessionHistory
import threading

class DBWorker:
	def __init__(self):
		# python의 Queue는 thread-safe하다. 즉, mutex가 필요 없다.ㄷㄷ
		self.match_history = Queue()
		self.event = threading.Event()
		self.postgres = None
		self.initialize()

	def initialize(self):
		threading.Thread(target=self.run).start()
	
	def save_match_history(self):
		while True:
			if not self.match_history.empty():
				# match_history Queue에 데이터가 있으면 DB에 저장
				matches = self.match_history.get()
				if isinstance(matches, list):
					for match in matches:
						print(f"Saving match haha {str(match)} to DB")
					# DB에 저장하는 함수 호출
					self.save_to_db(matches)
				else:
					print("No Matches to save")

	def run(self):
		# Producer-Consumer 패턴을 사용하여 DB에 데이터를 저장
		while True:
			self.event.wait()
			self.save_match_history()
			self.event.clear()

	def save_to_db(self, match):
		# DB에 저장하는 코드
		History = SessionHistory.objects.create()
		for m in match:
			print(f"Saving match {str(m)} to DB")
			match_history = Match.objects.create(
				player1=m.player[0],
				player2=m.player[1],
				winner=m.winner
			)
			History.match.add(match_history)
			History.save()
			print(f"Match {match_history} saved to DB")
