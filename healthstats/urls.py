from django.urls import path
from healthstats.views import (
    SymptomListView,
    SymptomDetailView,
    SymptomCreateView,
    SymptomDeleteView,
    SymptomUpdateView,
    HealthEventCreateView,
    HealthEventDeleteView,
    HealthEventUpdateView,
    HealthEventListView,
    HealthEventDetailView,
    HealthEventHomeView,
    stat_plot_view,
)

urlpatterns = [
    path("", HealthEventHomeView.as_view(), name="health_event_home"),
    path("symptoms/", SymptomListView.as_view(), name="symptoms"),
    path("symptom/new/", SymptomCreateView.as_view(), name="symptom_new"),
    path("symptom/<slug:slug>/delete", SymptomDeleteView.as_view(), name="symptom_delete"),
    path("symptom/<slug:slug>/update", SymptomUpdateView.as_view(), name="symptom_update"),
    path("symptom/<slug:slug>/", SymptomDetailView.as_view(), name="symptom_detail"),
    path("events/", HealthEventListView.as_view(), name="stat_list"),
    path("plots/", stat_plot_view, name="stat_plot"),
    path("event/<int:pk>/", HealthEventDetailView.as_view(), name="stat_detail"),
    path("event/new/", HealthEventCreateView.as_view(), name="stat_new"),
    path("event/<int:pk>/delete", HealthEventDeleteView.as_view(), name="stat_delete"),
    path("event/<int:pk>/update", HealthEventUpdateView.as_view(), name="stat_update"),
]
