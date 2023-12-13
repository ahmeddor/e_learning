# user_authentification/urls.py
from django.urls import path
from .views import signup, signin, user_logout

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("signin/", signin, name="signin"),
    path("logout/", user_logout, name="logout"),
    # Add other URL patterns if needed
]
