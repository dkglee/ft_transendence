from django.urls import path, include
from ChitChat import views as chat_views
from django.contrib.auth.views import LoginView, LogoutView

# urlpatterns = [
#     path("", chat_views.chatPage, name="chat-page"),

#     # authentication section
#     path("auth/login/", LoginView.as_view
#          (template_name="chat/loginPage.html"), name="login-user"),
#     path("auth/login/", LogoutView.as_view(), name="logout-user"),
# ]

urlpatterns = [
    path("", chat_views.chatPage, name="chat-page"),

    # authentication section
    path("auth/login/", LoginView.as_view
         (template_name="chat/loginPage.html", next_page="chat-page"), name="login-user"),
    path("auth/logout/", LogoutView.as_view(next_page="login-user"), name="logout-user"),
]
