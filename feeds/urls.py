from django.urls import path

from feeds.views import (
    FeedDashboardView,
    ReadArticlesView,
    FeedFolderCreateView,
    FeedCreateView,
    FeedDeleteView,
    FeedFolderDeleteView,
    open_article,
    refresh_feeds,
    toggle_read,
)

urlpatterns = [
    path("", FeedDashboardView.as_view(), name="feeds_dashboard"),
    path("refresh/", refresh_feeds, name="feeds_refresh"),
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
    path("item/<int:pk>/open/", open_article, name="feeds_open_article"),
    path("new/", FeedCreateView.as_view(), name="feeds_add"),
    path("<int:pk>/delete/", FeedDeleteView.as_view(), name="feeds_delete"),
]
