import math

class GameLogic:
	def __init__(self):
		self.player = [self.Paddle(350, 580, 100, 10), self.Paddle(350, 10, 100, 10)]
		self.ball = self.Ball(400, 300, 10, 5, 5, 5)
		self.canvas_width = 800
		self.canvas_height = 600
		self.player_score = [0, 0]  # 각 플레이어의 점수를 저장하는 배열
		self.isComputer = False  # 두 번째 플레이어가 컴퓨터인지 여부

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

	def update(self):
		# 공의 위치 업데이트
		self.ball.x += self.ball.velocityX
		self.ball.y += self.ball.velocityY

		# 컴퓨터 패들 위치 업데이트 (자동으로 움직임)
		if self.isComputer:
			self.player[1].x += (self.ball.x - (self.player[1].x + self.player[1].width / 2)) * 0.1

		# 공이 좌우 벽에 충돌하면 속도 반전
		if self.ball.x + self.ball.radius > self.canvas_width or self.ball.x - self.ball.radius < 0:
			self.ball.velocityX = -self.ball.velocityX

		# 충돌 검사
		def collision(ball, paddle):
			return (paddle.x < ball.x < paddle.x + paddle.width and
					paddle.y < ball.y < paddle.y + paddle.height)

		player_index = 0 if self.ball.y > self.canvas_height / 2 else 1
		player_paddle = self.player[player_index]

		if collision(self.ball, player_paddle):
			collide_point = self.ball.x - (player_paddle.x + player_paddle.width / 2)
			collide_point = collide_point / (player_paddle.width / 2)

			angle_rad = (math.pi / 4) * collide_point

			direction = 1 if self.ball.y > self.canvas_height / 2 else -1
			self.ball.velocityY = direction * self.ball.speed * math.cos(angle_rad)
			self.ball.velocityX = self.ball.speed * math.sin(angle_rad)

			self.ball.speed += 0.5

		# 점수 계산 및 공 리셋
		if self.ball.y - self.ball.radius < 0:
			self.player_score[0] += 1  # 아래쪽 플레이어 점수
			self.reset_ball()
		elif self.ball.y + self.ball.radius > self.canvas_height:
			self.player_score[1] += 1  # 위쪽 플레이어 점수
			self.reset_ball()

		# 플레이어의 패들 이동
		for i in range(2):
			self.player[i].x += self.player[i].dx

			# 패들이 화면 밖으로 나가지 않도록 제한
			if self.player[i].x < 0:
				self.player[i].x = 0
			if self.player[i].x + self.player[i].width > self.canvas_width:
				self.player[i].x = self.canvas_width - self.player[i].width

	def reset_ball(self):
		self.ball.x = self.canvas_width / 2
		self.ball.y = self.canvas_height / 2
		self.ball.speed = 5
		self.ball.velocityY = -self.ball.velocityY
