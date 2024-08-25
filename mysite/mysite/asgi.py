from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
# from transcendence.middleware import JWTAuthMiddleware # JWTAuthMiddleware import
import os
import ChitChat.routing
import transcendence.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoChat.settings')

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                ChitChat.routing.websocket_urlpatterns + transcendence.routing.websocket_urlpatterns
            )
        ),
    }
)

# JWTAuthMiddleware를 사용하여 WebSocket 요청을 처리
# application = ProtocolTypeRouter(
#     {
#         "http": get_asgi_application(),
#         "websocket": JWTAuthMiddleware(  # JWTAuthMiddleware를 사용하여 WebSocket 요청을 처리
#             URLRouter(
#                 ChitChat.routing.websocket_urlpatterns + transcendence.routing.websocket_urlpatterns
#             )
#         ),
#     }
# )
