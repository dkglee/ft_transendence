from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import GameSession
from django.shortcuts import render

# Create your views here.
@api_view(['GET'])
def check_session(request):
	# 게임 세션 검색
	session_available = check_for_available_session()
	if session_available:
		# 세션이 있을 경우
		response_data = {
			"session_id": session_available['session_id'],
			"websocket_url": session_available['websocket_url'],
			"websocket_port": session_available['websocket_port']
		}
	else:
		# 세션이 없을 경우
		response_data = {
			"session_id": None,
			"websocket_url": None,
			"websocket_port": None
		}
	return Response(response_data)

def check_for_available_session():
	# 현재 활성화된 게임 세션을 찾는다
	available_session = GameSession.objects.filter(is_active=False).first()
	if available_session:
		# 세션이 있을 경우
		return {
			"session_id": available_session.session_id,
			"websocket_url": available_session.websocket_url,
			"websocket_port": available_session.websocket_port
		}
	else:
		# 세션이 없을 경우
		return None

def match(request):
	return render(request, 'transcendence/match.html')

def pingpong(request):
	return render(request, 'transcendence/pingpong.html')
