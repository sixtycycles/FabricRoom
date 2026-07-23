from django.urls import path
from main.views import (
    LandingPageView,
    AboutPageView,
    TriggerManagementCommandView,
    delete_quote,
    PrivacyPolicyView,
    UtilitiesView,
    ManagementCommandRunsView,
)
from django.views.generic import TemplateView

urlpatterns = [
    path("", LandingPageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("quotes/<int:pk>/delete/", delete_quote, name="delete_quote"),
    path("privacy-policy/", PrivacyPolicyView.as_view(), name="privacy_policy"),
    path("utilities/", UtilitiesView.as_view(), name="utilities"),
    path("utilities/commands/", ManagementCommandRunsView.as_view(), name="management_commands"),
    path(
        "admin/commands/<str:command_name>/run/",
        TriggerManagementCommandView.as_view(),
        name="run_management_command",
    ),
]
