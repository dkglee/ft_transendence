from django.urls import path, include
from transcendence import views as transcendence_views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
	path("", transcendence_views.transcendencePage, name="transcendence-page"),
]
