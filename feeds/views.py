import feedparser
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from datetime import timedelta
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, TemplateView

from feeds.forms import FeedForm, FeedFolderForm
from feeds.models import Feed, FeedFolder, FeedItem


class FeedContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


@login_required
def open_article(request, pk):
    """Mark an article as read and redirect to its original URL."""
    feed_ids = list(Feed.objects.filter(user=request.user).values_list("id", flat=True))
    item = get_object_or_404(FeedItem, pk=pk, feed_id__in=feed_ids)
    item.mark_read()

    if item.link:
        return redirect(item.link)
    return redirect(reverse("feeds_dashboard"))

def _parse_published(value):
    """Best-effort parsing of an RSS/Atom date string into a datetime."""
    if not value:
        return None
    parsed = parse_datetime(value)
    if parsed is not None:
        return parsed
    try:
        from email.utils import parsedate_to_datetime

        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None


SYNC_FEED_INTERVAL = timedelta(minutes=30)


def sync_feed_items(feed):
    """Parse `feed` and upsert its entries into FeedItem.

    Existing items are preserved (with their is_read state intact); new
    items are inserted. `feed.last_fetched_at` is updated.
    """
    parsed = feedparser.parse(feed.feed_url)
    entries = parsed.get("entries", [])
    feed.last_fetched_at = timezone.now()
    feed.save(update_fields=["last_fetched_at"])

    for entry in entries:
        entry_id = (
            entry.get("id")
            or entry.get("guid")
            or entry.get("link")
            or entry.get("title", "")
        )
        defaults = {
            "title": entry.get("title", "")[:500],
            "link": entry.get("link", feed.site_url)[:1000],
            "summary": entry.get("summary", "") or entry.get("description", ""),
            "author": entry.get("author", "")[:255],
            "published": _parse_published(
                entry.get("published") or entry.get("updated")
            ),
            "fetched_at": timezone.now(),
        }
        FeedItem.objects.update_or_create(
            feed=feed,
            entry_id=entry_id[:1000],
            defaults=defaults,
        )


@method_decorator(vary_on_cookie, name="dispatch")
@method_decorator(cache_page(settings.CACHE_TTL), name="dispatch")
class FeedDashboardView(FeedContextMixin, LoginRequiredMixin, TemplateView):
    template_name = "feeds/dashboard.html"
    login_url = "/accounts/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        folders = FeedFolder.objects.filter(user=user)
        selected_folder_id = self.request.GET.get("folder")
        selected_feed_id = self.request.GET.get("feed")
        selected_folder = None
        selected_feed = None

        feeds_qs = Feed.objects.filter(user=user, is_active=True)
        if selected_folder_id:
            selected_folder = folders.filter(pk=selected_folder_id).first()
            if selected_folder is not None:
                feeds_qs = feeds_qs.filter(folder=selected_folder)

        if selected_feed_id:
            selected_feed = feeds_qs.filter(pk=selected_feed_id).first()
            if selected_feed is not None:
                feeds_qs = feeds_qs.filter(pk=selected_feed_id)

        feeds = list(feeds_qs)

        # Refresh feed content only when the feed has not been fetched recently.
        for feed in feeds:
            if (
                feed.last_fetched_at is None
                or feed.last_fetched_at + SYNC_FEED_INTERVAL < timezone.now()
            ):
                try:
                    sync_feed_items(feed)
                except Exception:
                    continue

        latest_items = FeedItem.objects.filter(feed__in=feeds, is_read=False).select_related(
            "feed"
        ).order_by("-published", "-fetched_at")

        unread_feed_ids = list({item.feed_id for item in latest_items})
        available_feeds = [feed for feed in feeds if feed.pk in unread_feed_ids]

        entries = []
        feed_item_counts = {}
        for item in latest_items:
            count = feed_item_counts.get(item.feed_id, 0)
            if count < 6:
                entries.append(item)
                feed_item_counts[item.feed_id] = count + 1

        context["folders"] = folders
        context["selected_folder"] = selected_folder
        context["selected_feed"] = selected_feed
        context["feeds"] = available_feeds
        context["folder_form"] = FeedFolderForm()
        context["feed_form"] = FeedForm(user=user)
        context["entries"] = entries
        return context


@method_decorator(vary_on_cookie, name="dispatch")
@method_decorator(cache_page(settings.CACHE_TTL), name="dispatch")
class ReadArticlesView(FeedContextMixin, LoginRequiredMixin, TemplateView):
    template_name = "feeds/read_articles.html"
    login_url = "/accounts/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        feed_ids = list(Feed.objects.filter(user=user).values_list("id", flat=True))
        read_items = (
            FeedItem.objects.filter(feed_id__in=feed_ids, is_read=True)
            .select_related("feed")
            .order_by("-read_at")
        )
        context["read_articles"] = read_items
        return context


@login_required
@require_POST
def toggle_read(request, pk):
    """Toggle the is_read flag on a FeedItem scoped to the current user."""
    feed_ids = list(Feed.objects.filter(user=request.user).values_list("id", flat=True))
    item = get_object_or_404(FeedItem, pk=pk, feed_id__in=feed_ids)
    if item.is_read:
        item.mark_unread()
    else:
        item.mark_read()

    next_url = request.POST.get("next") or reverse("feeds_dashboard")
    return redirect(next_url)


class FeedFolderCreateView(FeedContextMixin, LoginRequiredMixin, CreateView):
    model = FeedFolder
    form_class = FeedFolderForm
    success_url = reverse_lazy("feeds_dashboard")
    login_url = "/accounts/login/"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class FeedFolderDeleteView(FeedContextMixin, LoginRequiredMixin, DeleteView):
    model = FeedFolder
    success_url = reverse_lazy("feeds_dashboard")
    login_url = "/accounts/login/"

    def get_queryset(self):
        return FeedFolder.objects.filter(user=self.request.user)


class FeedCreateView(FeedContextMixin, LoginRequiredMixin, CreateView):
    model = Feed
    form_class = FeedForm
    success_url = reverse_lazy("feeds_dashboard")
    login_url = "/accounts/login/"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class FeedDeleteView(FeedContextMixin, LoginRequiredMixin, DeleteView):
    model = Feed
    success_url = reverse_lazy("feeds_dashboard")
    login_url = "/accounts/login/"

    def get_queryset(self):
        return Feed.objects.filter(user=self.request.user)
