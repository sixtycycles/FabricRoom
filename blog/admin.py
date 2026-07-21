from django.contrib import admin
from django.utils.html import format_html
from .models import Post, Note, Tag, InlineImage, Quote, Gratitude


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["author", "title", "body", "created_date", "published"]
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


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ["author", "text", "created_at"]
    search_fields = ["author", "text"]
    list_filter = ["author"]


@admin.register(InlineImage)
class InlineImageAdmin(admin.ModelAdmin):
    list_display = [
        "image_preview",
        "post",
        "alt_text",
        "created_at",
    ]
    list_filter = ["created_at", "post"]
    readonly_fields = ["created_at", "image_preview"]
    fields = ["post", "image", "alt_text"]

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="auto" />', obj.image.url
            )
        return "No image"

    image_preview.short_description = "Preview"


@admin.register(Gratitude)
class GratitudeAdmin(admin.ModelAdmin):
    list_display = ["author", "gratitude_text_short", "created_date"]
    list_filter = ["created_date", "author"]
    search_fields = ["gratitude_text", "author__username"]
    filter_horizontal = ["target"]

    def gratitude_text_short(self, obj):
        return obj.gratitude_text[:50] + ("..." if len(obj.gratitude_text) > 50 else "")
    gratitude_text_short.short_description = "Gratitude Text"

