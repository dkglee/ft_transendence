from django.urls import path

from . import views

urlpatterns = [
	path("", views.index, name="index"),
]

# 이제 polls 앱의 view를 호출하기 위해 URLconf를 설정했다.
# 이 URLconf는 polls 앱의 view를 호출하기 위한 URL을 지정한다.
# 이제는 global URLconf에 이 URLconf를 포함시켜야 한다.
