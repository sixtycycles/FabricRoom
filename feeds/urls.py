from django.urls import path

from feeds.views import (
    FeedDashboardView,
    ReadArticlesView,
    FeedFolderCreateView,
    FeedCreateView,
    FeedDeleteView,
    FeedFolderDeleteView,
    toggle_read,
)

urlpatterns = [
    path("", FeedDashboardView.as_view(), name="feeds_dashboard"),
    path("read/", ReadArticlesView.as_view(), name="feeds_read"),
    path(
        "item/<int:pk>/toggle-read/",
        toggle_read,
        name="feeds_toggle_read",
    ),
    path("folder/new/", FeedFolderCreateView.as_view(), name="feeds_folder_create"),
    path(
        "folder/<int:pk>/delete/",
        FeedFolderDeleteView.as_view(),
        name="feeds_folder_delete",
    ),
    path("new/", FeedCreateView.as_view(), name="feeds_add"),
    path("<int:pk>/delete/", FeedDeleteView.as_view(), name="feeds_delete"),
]
