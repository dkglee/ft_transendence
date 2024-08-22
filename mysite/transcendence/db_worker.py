from queue import Queue
from threading import Lock
import threading

class DBWorker:
	def __init__(self):
		self.match_history = Queue()
		# python의 Queue는 thread-safe하다. 즉, mutex가 필요 없다.ㄷㄷ
		# self.mutex = Lock()
		# 연결되어 있는 DB
		# TODO: Docker Compose를 사용하여 PostgreSQL을 실행하고, 이를 연결하는 코드 작성
		self.postgres = None
		self.initialize()

	def initialize(self):
		# DB 연결
		# self.postgres = self.connect_to_db()

		threading.Thread(target=self.run).start()
	
	def run(self):
		# Producer-Consumer 패턴을 사용하여 DB에 데이터를 저장
		while True:
			if not self.match_history.empty():
				# match_history Queue에 데이터가 있으면 DB에 저장
				match = self.match_history.get()
				print(f"Saving match {match} to DB")
				# DB에 저장하는 함수 호출
				self.save_to_db(match)

	def save_to_db(self, match):
		# DB에 데이터를 저장하는 로직
		# self.postgres.save(match)
		pass
