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
    DeletePostImageView,
    InlineImagePanelView,
    UpdatePostImageAltTextView,
    PostQRCodeView,
)

urlpatterns = [
    path("", BlogListView.as_view(), name="blog"),
    path("post/<int:pk>/", BlogDetailView.as_view(), name="post_detail"),
    path("post/<int:pk>/qr/", PostQRCodeView.as_view(), name="post_qr_code"),
    path("post/new/", BlogCreateView.as_view(), name="post_new"),
    path("post/<int:pk>/delete/", BlogDeleteView.as_view(), name="post_delete"),
    path("post/<int:pk>/update/", BlogUpdateView.as_view(), name="post_edit"),
    path(
        "post/new/upload-image/",
        UploadPostImageView.as_view(),
        name="upload_post_image_new",
    ),
    path(
        "post/<int:pk>/upload-image/",
        UploadPostImageView.as_view(),
        name="upload_post_image",
    ),
    path(
        "post/new/inline-images/",
        InlineImagePanelView.as_view(),
        name="post_inline_images_new",
    ),
    path(
        "post/<int:pk>/inline-images/",
        InlineImagePanelView.as_view(),
        name="post_inline_images",
    ),
    path(
        "post/image/<int:image_id>/alt-text/",
        UpdatePostImageAltTextView.as_view(),
        name="update_post_image_alt_text",
    ),
    path(
        "post/image/<int:image_id>/delete/",
        DeletePostImageView.as_view(),
        name="delete_post_image",
    ),
    path("note/", NoteListView.as_view(), name="note_list"),
    path("note/new/", NoteCreateView.as_view(), name="note_new"),
    path("note/<int:pk>/", NoteDetailView.as_view(), name="note_detail"),
    path("note/<int:pk>/delete/", NoteDeleteView.as_view(), name="note_delete"),
    path("note/<int:pk>/update/", NoteUpdateView.as_view(), name="note_update"),
]
