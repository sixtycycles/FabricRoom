from django.urls import path
from healthstats.views import HealthEventCreateView, HealthEventDeleteView, HealthEventUpdateView, HealthEventListView, HealthEventDetailView
urlpatterns = [
    path('', HealthEventListView.as_view(), name='HealthEvent_list'),
    path('event/<int:pk>/', HealthEventDetailView.as_view(), name='post_detail'),
    path('event/new/', HealthEventCreateView.as_view(), name='post_new'),
    path('event/<int:pk>/delete', HealthEventDeleteView.as_view(), name='post_delete'),
    path('event/<int:pk>/update', HealthEventUpdateView.as_view(), name='post_update'),
]
