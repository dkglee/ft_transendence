# authentication.py
import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.conf import settings


User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            # 헤더가 없는 경우에 대한 처리
            if self.is_public_endpoint(request):
                return None  # 인증이 필요 없는 엔드포인트에서는 None 반환
            else:
                raise AuthenticationFailed('Authorization header is missing')

        token = auth_header.split()[1]

        try:
            # JWT를 검증하고 페이로드를 디코딩
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])

            # 페이로드에서 사용자 정보 추출
            user_id = payload['user_id']
            # jihwjeon: 저는 User 테이블을 가지고 있어서 디비로부터 로딩하지만 해당 내용이 없다면
            # payload['email'], payload['username'] 등을 직접 변수로 읽어가면 될 것 같습니다
            # 이후 view 단에서 request.user or request.email 등으로 읽을 수 있습니다.
            user = User.objects.get(id=user_id)

            return user, token

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired')

        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

    def authenticate_header(self, request):
        return 'Bearer'

    def is_public_endpoint(self, request):
        """
        해당 요청이 인증이 필요 없는 엔드포인트인지 확인합니다.
        """
        public_endpoints = ['/api/oauth', '/swagger']  # 예시: 인증이 필요 없는 엔드포인트 목록

        for endpoint in public_endpoints:
            if request.path.startswith(endpoint):
                return True

        return False
