import math
import random

class Subject:
	def __init__(self):
		self._observers = []

	def attach(self, observer):
		if observer not in self._observers:
			self._observers.append(observer)

	def detach(self, observer):
		try:
			self._observers.remove(observer)
		except ValueError:
			pass

	def notify(self, value, winner):
		print(f"Notifying observers: {value} {self._observers}")
		for observer in self._observers:
			observer.update(value, winner)
		print("Notifying observers1")

class GameLogic(Subject):
	def __init__(self):
		super().__init__()
		self.max_score = 1
		self.player = [self.Paddle(350, 580, 100, 10), self.Paddle(350, 10, 100, 10)]
		self.ball = self.Ball(400, 300, 10, 5, 5, 5)
		self.canvas_width = 600
		self.canvas_height = 800
		self.player_score = [0, 0]  # 각 플레이어의 점수를 저장하는 배열
		self.isComputer = False  # 두 번째 플레이어가 컴퓨터인지 여부
		self.matchId = None

	class Paddle:
		def __init__(self, x, y, width, height):
			self.x = x
			self.y = y
			self.width = width
			self.height = height
			self.dx = 0  # 수평 속도 초기화

	class Ball:
		def __init__(self, x, y, radius, speed, velocityX, velocityY):
			self.x = x
			self.y = y
			self.radius = radius
			self.speed = speed
			self.velocityX = velocityX
			self.velocityY = velocityY

	def ray_intersects_rectangle(self, ray_origin, ray_end, rect):
		dx = ray_end[0] - ray_origin[0]
		if dx == 0:
			return False
		
		tmin = (rect['left'] - ray_origin[0]) / (ray_end[0] - ray_origin[0])
		tmax = (rect['right'] - ray_origin[0]) / (ray_end[0] - ray_origin[0])

		if tmin > tmax:
			tmin, tmax = tmax, tmin

		dy = ray_end[1] - ray_origin[1]
		if dy == 0:
			return False
		tymin = (rect['top'] - ray_origin[1]) / (ray_end[1] - ray_origin[1])
		tymax = (rect['bottom'] - ray_origin[1]) / (ray_end[1] - ray_origin[1])

		if tymin > tymax:
			tymin, tymax = tymax, tymin

		if tmin > tymax or tymin > tmax:
			return False
		
		if tymin > tmin:
			tmin = tymin
		if tymax < tmax:
			tmax = tymax
		
		return tmin >= 0 and tmin <= 1

	def collision_ray_casting(self, ball, paddle):
		ballPrev = [ball.prevX, ball.prevY]
		ballPos = [ball.x, ball.y]

		paddleRect = {
			'left': paddle.x - ball.radius,
			'right': paddle.x + paddle.width + ball.radius,
			'top': paddle.y - ball.radius,
			'bottom': paddle.y + paddle.height + ball.radius
		}

		return self.ray_intersects_rectangle(ballPrev, ballPos, paddleRect)

	def update(self):
		# 공의 현재 위치
		self.ball.prevX = self.ball.x
		self.ball.prevY = self.ball.y

		# 공의 위치 업데이트
		self.ball.x += self.ball.velocityX
		self.ball.y += self.ball.velocityY

		# 컴퓨터 패들 위치 업데이트 (자동으로 움직임)
		if self.isComputer:
			self.player[1].x += (self.ball.x - (self.player[1].x + self.player[1].width / 2)) * 0.1

		# 공이 좌우 벽에 충돌하면 속도 반전
		if self.ball.x + self.ball.radius > self.canvas_width:
			self.ball.velocityX = -self.ball.velocityX
			self.ball.x = self.canvas_width - self.ball.radius
		elif self.ball.x - self.ball.radius < 0:
			self.ball.velocityX = -self.ball.velocityX
			self.ball.x = self.ball.radius

		# 충돌 검사
		player_index = 0 if self.ball.y > self.canvas_height / 2 else 1
		player_paddle = self.player[player_index]

		if self.collision_ray_casting(self.ball, player_paddle):
			collide_point = self.ball.x - (player_paddle.x + player_paddle.width / 2)
			collide_point = collide_point / (player_paddle.width / 2)

			angle_rad = (math.pi / 4) * collide_point

			direction = -1 if self.ball.y > self.canvas_height / 2 else 1
			self.ball.velocityY = direction * self.ball.speed * math.cos(angle_rad)
			self.ball.velocityX = self.ball.speed * math.sin(angle_rad)

			self.ball.speed += 0.5

			self.ball.x = self.ball.prevX
			self.ball.y = self.ball.prevY
		# 점수 계산 및 공 리셋
		if self.ball.y - self.ball.radius < 0:
			self.player_score[0] += 1  # 아래쪽 플레이어 점수
			self.reset_ball()
		elif self.ball.y + self.ball.radius > self.canvas_height:
			self.player_score[1] += 1  # 위쪽 플레이어 점수
			self.reset_ball()

		if self.player_score[0] >= self.max_score or self.player_score[1] >= self.max_score:
			print("Game Over")
			if self.player_score[0] > self.player_score[1]:
				self.notify(self.matchId, 0)
			else:
				self.notify(self.matchId, 1)

		# 플레이어의 패들 이동
		for i in range(2):
			self.player[i].x += self.player[i].dx

			# 패들이 화면 밖으로 나가지 않도록 제한
			if self.player[i].x < 0:
				self.player[i].x = 0
			if self.player[i].x + self.player[i].width > self.canvas_width:
				self.player[i].x = self.canvas_width - self.player[i].width
			self.player[i].dx = 0

	def reset_ball(self):
		self.ball.x = self.canvas_width / 2
		self.ball.y = self.canvas_height / 2
		self.ball.speed = 5
		self.ball.velocity_x = 5 * (1 if random.random() > 0.5 else -1)
		self.ball.velocity_y = 5 * (1 if random.random() > 0.5 else -1)
