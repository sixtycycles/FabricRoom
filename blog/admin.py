from django.contrib import admin
from .models import Post, Note, Tag, InlineImage


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "author",
        "title",
        "body",
        "created_date",
        "published"
    ]
    list_filter = ["author"]
    readonly_fields = []
    fields = ["author", "title", "body", "created_date", "published"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = [
        "tag_slug",
    ]


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = [
        "author",
        "title",
        "link",
    ]
    list_filter = ["author"]


@admin.register(InlineImage)
class InlineImageAdmin(admin.ModelAdmin):
    list_display = [
        "post",
        "created_at",
    ]
    list_filter = ["created_at", "post"]
    readonly_fields = ["created_at"]
