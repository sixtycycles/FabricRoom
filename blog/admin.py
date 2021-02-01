from django.contrib import admin
from .models import Post, Note, Tag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "author",
        "title",
        "body",
    ]
    list_filter = ["author"]


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
