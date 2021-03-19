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
    temp_stat_plot_view,
    heart_stat_plot_view,
    steps_stat_plot_view,
    oxygen_stat_plot_view,
    oxygen_temperature_stat_plot_view,

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
    path("plots/temperature", temp_stat_plot_view, name="temp-plot"),
    path("plots/heart", heart_stat_plot_view, name="heart-plot"),
    path("plots/steps", steps_stat_plot_view, name="steps-plot"),
    path("plots/oxygen", oxygen_stat_plot_view, name="oxygen-plot"),
    path("plots/oxygen-temperature", oxygen_temperature_stat_plot_view, name="oxygen-temp-plot"),
    path("event/<int:pk>/", HealthEventDetailView.as_view(), name="stat_detail"),
    path("event/new/", HealthEventCreateView.as_view(), name="stat_new"),
    path("event/<int:pk>/delete", HealthEventDeleteView.as_view(), name="stat_delete"),
    path("event/<int:pk>/update", HealthEventUpdateView.as_view(), name="stat_update"),
    
]
