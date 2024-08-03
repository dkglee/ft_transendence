from django.urls import path

from . import views

# app_name = "polls"
# urlpatterns = [
# 	# ex: /polls/
# 	path("", views.index, name="index"),
# 	# ex: /polls/5/
# 	path("specifics/<int:question_id>/", views.detail, name="detail"),
# 	# ex: /polls/5/results/
# 	path("<int:question_id>/results/", views.results, name="results"),
# 	# ex: /polls/5/vote/
# 	path("<int:question_id>/vote/", views.vote, name="vote"),
# ]

app_name = "polls"
urlpatterns = [
	path("", views.IndexView.as_view(), name="index"),
	path("<int:pk>/", views.DetailView.as_view(), name="detail"),
	path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
	path("<int:question_id>/vote/", views.vote, name="vote"),
]

# 이제 polls 앱의 view를 호출하기 위해 URLconf를 설정했다.
# 이 URLconf는 polls 앱의 view를 호출하기 위한 URL을 지정한다.
# 이제는 global URLconf에 이 URLconf를 포함시켜야 한다.
