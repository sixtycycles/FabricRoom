from django.urls import path
from main.views import LandingPageView, AboutPageView, SignUpView
from django.views.generic import TemplateView


urlpatterns = [
    path("", LandingPageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("signup/", SignUpView.as_view(), name="signup"),
]
