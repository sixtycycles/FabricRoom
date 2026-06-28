from django.contrib import admin

from feeds.models import Feed, FeedFolder, FeedItem


@admin.register(FeedFolder)
class FeedFolderAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at")
    search_fields = ("name", "description")


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "folder", "is_active", "last_fetched_at", "created_at")
    list_filter = ("is_active", "folder")
    search_fields = ("title", "feed_url")


@admin.register(FeedItem)
class FeedItemAdmin(admin.ModelAdmin):
    list_display = ("title", "feed", "is_read", "read_at", "published", "fetched_at")
    list_filter = ("is_read", "feed")
    search_fields = ("title", "link", "entry_id")
    readonly_fields = ("fetched_at",)
    date_hierarchy = "published"
