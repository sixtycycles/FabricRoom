from django.contrib import admin

from inbox.models import Message, MessageState


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "recipient", "subject", "sent_at", "created_at")
    search_fields = ("subject", "body", "sender__username", "recipient__username")
    list_filter = ("sent_at", "created_at")


@admin.register(MessageState)
class MessageStateAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "message", "is_read", "is_archived", "is_deleted")
    list_filter = ("is_read", "is_archived", "is_deleted")
    search_fields = ("user__username", "message__subject")
