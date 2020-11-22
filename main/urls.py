from django.urls import path
from main.views import LandingPageView, AboutPageView, PrivateHome
from django.views.generic import TemplateView


urlpatterns = [
    path('', LandingPageView.as_view(), name='home'),
    path('about/', AboutPageView.as_view(), name='about'),
    path('secret/',PrivateHome.as_view(), name='private_home')

]

