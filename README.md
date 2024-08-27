# Mock Server Guide for Game Service

생성일: 2024년 8월 27일 오전 10:25

### 설치 파일

```bash
// requirements
asgiref==3.8.1
attrs==23.2.0
autobahn==23.6.2
Automat==22.10.0
cffi==1.16.0
channels==4.1.0
constantly==23.10.4
cryptography==43.0.0
daphne==4.1.2
Django==5.0.7
djangorestframework==3.15.2
djangorestframework-simplejwt==5.3.1
hyperlink==21.0.0
idna==3.7
incremental==22.10.0
psycopg2==2.9.9
psycopg2-binary==2.9.9
pyasn1==0.6.0
pyasn1_modules==0.4.0
pycparser==2.22
PyJWT==2.9.0
pyOpenSSL==24.2.1
service-identity==24.1.0
six==1.16.0
sqlparse==0.5.1
Twisted==24.3.0
txaio==23.1.1
typing_extensions==4.12.2
zope.interface==6.4.post2
```

### 서버 실행 안내

아래 명령어를 사용하여 서버를 실행하세요:

```bash
python manage.py runserver 8001
```

> 주의: 포트 번호는 자유롭게 변경할 수 있습니다.
> 
- **디렉토리 경로**: `/ft_transcendence/mysite`

### WebSocket 연결 안내

서버에 WebSocket으로 연결하려면 아래의 URL 패턴을 사용하세요:

```bash
bash코드 복사
ws://${websocket_url}:${websocket_port}/ws/game/${session_id}/?token=${jwt_token}

```

- **URL 구성 요소**:
    - `${websocket_url}`: WebSocket 서버의 URL (예: `127.0.0.1`)
    - `${websocket_port}`: WebSocket 서버의 포트 번호 (예: `8001`)
    - `${session_id}`: 게임 세션의 ID
        
        (예: `session_1` )
        
        > **주의:** session_{숫자} 형태로 들어와야 하며, 현재까지 1~8 까지의 숫자만 가능합니다.
        > 
    - `${jwt_token}`: JWT 인증 토큰
        
        > **주의:** JWT 토큰이 없을 시 인증이 안됩니다.
        > 

**예시**: 만약 `websocket_url`이 `127.0.0.1`, `websocket_port`가 `8001`, `session_id`가 `session_1`, `jwt_token`이 `abc123`라면:

```bash
ws://127.0.0.1:8001/ws/game/session_1/?token=abc123
```

**URL 패턴**:

이 URL 패턴은 `TranscendenceConsumer`에 연결되며, 게임 기능을 관리합니다.

```python
websocket_urlpatterns = [
    re_path(r'ws/game/(?P<session_id>\w+)/$', GameConsumer.as_asgi()),
]
```

이 URL 패턴에 따라 WebSocket 연결을 요청하세요.

### 게임 로직 흐름

1. **연결 시 인증 작업**
    - 클라이언트가 서버에 WebSocket으로 연결할 때, JWT 토큰을 통해 인증이 자동으로 처리됩니다.
2. **다른 플레이어 대기**
    - 연결 후 10초 동안 다른 플레이어를 기다립니다.
3. **자동 시작 조건**
    - 10초 내에 4명의 플레이어가 모두 모이지 않으면 게임이 자동으로 시작됩니다.
    - 부족한 플레이어는 컴퓨터가 대신하여 게임을 진행합니다.
4. **게임 시작 알림**
    - 게임이 시작될 때, 클라이언트들에게 게임이 시작되었다는 메시지를 전송합니다.
5. **게임 패킷 주고받기**
    - 게임 진행 중에 클라이언트와 서버 간에 게임 패킷을 주고받습니다.
6. **매치 종료**
    - 하나의 Match가 끝나면, 클라이언트들에게 해당 Match가 종료되었음을 알리는 메시지를 전송합니다.
7. **토너먼트 종료**
    - 게임(전체 토너먼트)이 끝나면, 클라이언트들에게 게임이 끝났다는 메시지를 전송합니다.
8. **연결 해제**
    - 게임이 끝나면 클라이언트와 서버 간의 WebSocket 연결을 해제합니다.

### 패킷 내용

- 게임 시작 안내

```json
/*
* 서버 -> 클라이언트
* 매치 하나에 대한 정보 (초기화 시 사용하면 좋을 듯
* 합니다)
*/
{
  "matchId": "A",
  "player1": {
    "username": "player1_username",
    "paddle_pos": {
      "x": 100,
      "y": 200
    },
    "score": 0
  },
  "player2": {
    "username": "player2_username",
    "paddle_pos": {
      "x": 300,
      "y": 200
    },
    "score": 0
  },
  "event": "start"
}
```

- 게임 상태 정보

```json
/*
* 서버->클라이언트 : 평균 0.05초 마다 보내짐
* 매치 하나의 상태 정보가 담겨져 있습니다.
*/
{
	"matchId": "A",
  "player1": {
    "username": "player1_username",
    "paddle_pos": {
      "x": 120,
      "y": 200
    },
    "score": 3
  },
  "player2": {
    "username": "player2_username",
    "paddle_pos": {
      "x": 280,
      "y": 200
    },
    "score": 5
  },
  "ball": {
    "pos": {
      "x": 200,
      "y": 150
    }
  }
}

```

- 예상 입력 (클라이언트 → 서버)

```json
/*
* 클라이언트->서버 : 클라이언트가 입력을 할 때마다 주어지는 기대되는 JSON
*/
{
  "username": "username",
  "action": "l" // "l": left || "r": right
}
```

> 해당 방식으로 서버로 메시지가 주어져야 움직임이 반영됩니다.
> 
- 매치 종료 시 (매치)

```json
{
  "matchId": "A",
  "winner": "player1_username"
}
```

- 게임 종료 시 (세션: 토너먼트 종료)

```json
{
  "event": "session_end"
}
```

### 주의 사항

- 서버를 시작하자마자 바로 연결을 시도하지 마세요.
    - 2초간의 설정 시간이 필요합니다.

### 깃 허브 주소

[GitHub - dkglee/ft_transendence: PingPong-Logic-Server](https://github.com/dkglee/ft_transendence)
