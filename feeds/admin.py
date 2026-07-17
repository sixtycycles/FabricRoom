from django.contrib import admin
from django.utils import timezone

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


@admin.action(description="Mark selected feed items as read")
def mark_feed_items_read(modeladmin, request, queryset):
    updated = queryset.filter(is_read=False).update(is_read=True, read_at=timezone.now())
    modeladmin.message_user(request, f"{updated} feed item(s) marked as read.")


@admin.action(description="Mark selected feed items as unread")
def mark_feed_items_unread(modeladmin, request, queryset):
    updated = queryset.filter(is_read=True).update(is_read=False, read_at=None)
    modeladmin.message_user(request, f"{updated} feed item(s) marked as unread.")


@admin.register(FeedItem)
class FeedItemAdmin(admin.ModelAdmin):
    list_display = ("title", "feed", "is_read", "read_at", "published", "fetched_at")
    list_filter = ("is_read", "feed")
    search_fields = ("title", "link", "entry_id")
    readonly_fields = ("fetched_at",)
    date_hierarchy = "published"
    actions = [mark_feed_items_read, mark_feed_items_unread]
