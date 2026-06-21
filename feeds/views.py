import feedparser
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, TemplateView

from feeds.forms import FeedForm, FeedFolderForm
from feeds.models import Feed, FeedFolder


class FeedDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "feeds/dashboard.html"
    login_url = "/accounts/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        folders = FeedFolder.objects.filter(user=user)
        selected_folder_id = self.request.GET.get("folder")
        selected_folder = None

        feeds = Feed.objects.filter(user=user, is_active=True)
        if selected_folder_id:
            selected_folder = folders.filter(pk=selected_folder_id).first()
            if selected_folder is not None:
                feeds = feeds.filter(folder=selected_folder)

        context["folders"] = folders
        context["selected_folder"] = selected_folder
        context["feeds"] = feeds
        context["folder_form"] = FeedFolderForm()
        context["feed_form"] = FeedForm(user=user)

        entries = []
        for feed in feeds:
            try:
                parsed = feedparser.parse(feed.feed_url)
                for entry in parsed.get("entries", [])[:6]:
                    entries.append(
                        {
                            "feed": feed,
                            "title": entry.get("title", "Untitled"),
                            "link": entry.get("link", feed.site_url),
                            "summary": entry.get("summary", ""),
                            "published": entry.get("published", ""),
                        }
                    )
            except Exception:
                continue

        context["entries"] = entries
        return context


class FeedFolderCreateView(LoginRequiredMixin, CreateView):
    model = FeedFolder
    form_class = FeedFolderForm
    success_url = reverse_lazy("feeds_dashboard")
    login_url = "/accounts/login/"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class FeedFolderDeleteView(LoginRequiredMixin, DeleteView):
    model = FeedFolder
    success_url = reverse_lazy("feeds_dashboard")
    login_url = "/accounts/login/"

    def get_queryset(self):
        return FeedFolder.objects.filter(user=self.request.user)


class FeedCreateView(LoginRequiredMixin, CreateView):
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


class FeedDeleteView(LoginRequiredMixin, DeleteView):
    model = Feed
    success_url = reverse_lazy("feeds_dashboard")
    login_url = "/accounts/login/"

    def get_queryset(self):
        return Feed.objects.filter(user=self.request.user)
