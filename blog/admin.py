from django.contrib import admin
from .models import Post, Note, Tag
from django_summernote.admin import SummernoteModelAdmin


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    summernote_fields = ("body",)
    list_display = [
        "author",
        "title",
        "body",
        "created_date",
        "published"
    ]
    list_filter = ["author"]
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
