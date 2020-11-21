from django.urls import path
from main.views import index_view

urlpatterns = [
    path('', index_view),
]

