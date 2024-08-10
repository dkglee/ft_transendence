from django.urls import path, include
from transcendence import views as transcendence_views
from django.contrib.auth.views import LoginView, LogoutView

app_name = "pingpong"
urlpatterns = [
	path("", transcendence_views.transcendencePage, name="transcendence-page"),

	# authentication section
	path("auth/login/", LoginView.as_view(
		template_name="transcendence/loginPage.html", next_page="pingpong:transcendence-page"), name="login-user"),
	path("auth/logout/", LogoutView.as_view(next_page="pingpong:login-user"), name="logout-user"),
]
