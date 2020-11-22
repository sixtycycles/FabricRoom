from django.urls import path
from main.views import LandingPageView
from django.views.generic import TemplateView


urlpatterns = [
    path('', LandingPageView.as_view()),
]

