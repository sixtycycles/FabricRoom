from django.urls import path
from blog.views import (
    BlogListView,
    BlogDetailView,
    BlogCreateView,
    BlogUpdateView,
    BlogDeleteView,
    NoteListView,
    NoteDetailView,
    NoteCreateView,
    NoteUpdateView,
    NoteDeleteView,
)

urlpatterns = [
    path("", BlogListView.as_view(), name="blog"),
    path("post/<int:pk>/", BlogDetailView.as_view(), name="post_detail"),
    path("post/new/", BlogCreateView.as_view(), name="post_new"),
    path("post/<int:pk>/delete", BlogDeleteView.as_view(), name="post_delete"),
    path("post/<int:pk>/update", BlogUpdateView.as_view(), name="post_update"),
    path("note/new/", NoteCreateView.as_view(), name="note_new"),
    path("note/<int:pk>/", NoteDetailView.as_view(), name="note_detail"),
    path("note/<int:pk>/delete", NoteDeleteView.as_view(), name="note_delete"),
    path("note/<int:pk>/update", NoteUpdateView.as_view(), name="note_update"),
]
