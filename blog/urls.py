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
    UploadPostImageView,
)

urlpatterns = [
    path("", BlogListView.as_view(), name="blog"),
    path("post/<int:pk>/", BlogDetailView.as_view(), name="post_detail"),
    path("post/new/", BlogCreateView.as_view(), name="post_new"),
    path("post/<int:pk>/delete", BlogDeleteView.as_view(), name="post_delete"),
    path("post/<int:pk>/update", BlogUpdateView.as_view(), name="post_edit"),
    path("post/new/upload-image/", UploadPostImageView.as_view(), name="upload_post_image_new"),
    path("post/<int:pk>/upload-image/", UploadPostImageView.as_view(), name="upload_post_image"),
    path("note/", NoteListView.as_view(), name="note_list"),
    path("note/new/", NoteCreateView.as_view(), name="note_new"),
    path("note/<int:pk>/", NoteDetailView.as_view(), name="note_detail"),
    path("note/<int:pk>/delete", NoteDeleteView.as_view(), name="note_delete"),
    path("note/<int:pk>/update", NoteUpdateView.as_view(), name="note_update"),
]
