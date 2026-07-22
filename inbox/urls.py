from django.urls import path

from inbox.views import (
    ArchiveListView,
    ComposeMessageView,
    DraftEditView,
    DraftListView,
    InboxListView,
    ReplyMessageView,
    SentListView,
    ThreadDetailView,
    delete_message,
    mark_read,
    toggle_archive,
)

urlpatterns = [
    path("", InboxListView.as_view(), name="inbox_list"),
    path("sent/", SentListView.as_view(), name="inbox_sent"),
    path("drafts/", DraftListView.as_view(), name="inbox_drafts"),
    path("archive/", ArchiveListView.as_view(), name="inbox_archive"),
    path("compose/", ComposeMessageView.as_view(), name="inbox_compose"),
    path("drafts/<int:message_id>/edit/", DraftEditView.as_view(), name="inbox_draft_edit"),
    path("message/<int:message_id>/", ThreadDetailView.as_view(), name="inbox_thread"),
    path("message/<int:message_id>/reply/", ReplyMessageView.as_view(), name="inbox_reply"),
    path("message/<int:message_id>/mark-read/", mark_read, name="inbox_mark_read"),
    path("message/<int:message_id>/archive/", toggle_archive, name="inbox_toggle_archive"),
    path("message/<int:message_id>/delete/", delete_message, name="inbox_delete"),
]
