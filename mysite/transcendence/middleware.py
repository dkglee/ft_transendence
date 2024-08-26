from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs
from jwt import decode as jwt_decode, DecodeError, ExpiredSignatureError
from django.conf import settings
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

@sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware:
    """
    Custom middleware to handle JWT authentication for Django Channels.
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        print("JWTAuthMiddleware")
        try:
            query_string = scope["query_string"].decode()
            query_params = parse_qs(query_string)
            token = query_params.get("token", None)
            print(f"Received token: {token}")

            if token:
                try:
                    # JWT 토큰 디코딩 및 검증
                    decoded_data = jwt_decode(token[0], settings.JWT_SECRET, algorithms=["HS256"])
                    print(f"Decoded data: {decoded_data}")
                    user_id = decoded_data.get("user_id")

                    # print(f"All Users: {User.objects.all()}")

                    scope["user"] = await get_user(user_id)
                    user = scope["user"]
                    user.username = decoded_data.get("username")
                    print(f"Authenticated user: {scope['user']}")
                except (DecodeError, ExpiredSignatureError) as e:
                    print(f"Token decoding error: {str(e)}")
                    # 토큰이 유효하지 않을 경우 익명 사용자 설정
                    scope["user"] = AnonymousUser()
            else:
                print("No token provided, setting user as AnonymousUser")
                scope["user"] = AnonymousUser()

            return await self.inner(scope, receive, send)

        except Exception as e:
            scope["user"] = AnonymousUser()
            return await self.inner(scope, receive, send)
