from django.urls import path
from main.views import LandingPageView, AboutPageView, delete_quote
from django.views.generic import TemplateView

urlpatterns = [
    path("", LandingPageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("quotes/<int:pk>/delete/", delete_quote, name="delete_quote"),
]
