from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from transcendence.middleware import JWTAuthMiddleware  # JWTAuthMiddleware import
import os
import ChitChat.routing
import transcendence.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoChat.settings')

# ProtocolTypeRouter 설정
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(  # AuthMiddlewareStack을 사용하여 기본 인증 처리
            JWTAuthMiddleware(  # JWTAuthMiddleware를 추가하여 JWT 인증 처리
                URLRouter(
                    ChitChat.routing.websocket_urlpatterns + transcendence.routing.websocket_urlpatterns
                )
            )
        ),
    }
)
