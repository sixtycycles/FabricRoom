from django.urls import path

from feeds.views import (
    FeedDashboardView,
    FeedFolderCreateView,
    FeedCreateView,
    FeedDeleteView,
    FeedFolderDeleteView,
)

urlpatterns = [
    path("", FeedDashboardView.as_view(), name="feeds_dashboard"),
    path("folder/new/", FeedFolderCreateView.as_view(), name="feeds_folder_create"),
    path("folder/<int:pk>/delete/", FeedFolderDeleteView.as_view(), name="feeds_folder_delete"),
    path("new/", FeedCreateView.as_view(), name="feeds_add"),
    path("<int:pk>/delete/", FeedDeleteView.as_view(), name="feeds_delete"),
]
