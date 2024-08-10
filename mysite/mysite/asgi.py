from channels.routing import ProtocolTypeRouter, URLRouter
from ChitChat import routing
from channels.auth import AuthMiddlewareStack
import os
from django.core.asgi import get_asgi_application
import ChitChat

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoChat.settings')

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                ChitChat.routing.websocket_urlpatterns
            )
        )
    }
)
