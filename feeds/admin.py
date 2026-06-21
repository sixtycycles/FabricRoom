from django.contrib import admin

from feeds.models import Feed, FeedFolder


@admin.register(FeedFolder)
class FeedFolderAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at")
    search_fields = ("name", "description")


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "folder", "is_active", "created_at")
    list_filter = ("is_active", "folder")
    search_fields = ("title", "feed_url")
