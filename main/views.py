from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import PrivacyPolicy

from blog.models import Quote, Gratitude
from feeds.models import FeedItem


def _user_in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


class LandingPageView(TemplateView):
    template_name = "main/home.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("blog")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LandingPageView, self).get_context_data(**kwargs)
        user = self.request.user
        context["user"] = user

        if _user_in_group(user, "blog access"):
            context["random_quote"] = Quote.objects.order_by("?").first()
        elif _user_in_group(user, "gratitudes access"):
            context["random_gratitude"] = (
                Gratitude.objects.filter(target=user).order_by("?").first()
            )

        if _user_in_group(user, "feeds access"):
            context["recent_feed_items"] = (
                FeedItem.objects.filter(feed__user=user, is_read=False)
                .select_related("feed")
                .order_by("-published", "-fetched_at")[:5]
            )
        return context


class AboutPageView(TemplateView):
    template_name = "main/about.html"


class PrivateHome(LoginRequiredMixin, TemplateView):
    login_url = "/accounts/login/"
    logout_url = "/accounts/logout/"
    redirect_field_name = "redirect_to"
    raise_exception = True

    template_name = "main/private_home.html"

    def get_context_data(self, **kwargs):
        context = super(PrivateHome, self).get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


class PrivacyPolicyView(TemplateView):
    template_name = "privacy_policy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        privacy_policy = PrivacyPolicy.objects.first()
        context['privacy_policy'] = privacy_policy
        return context


# Custom http error code pages
def custom_error_403(request, exception):
    return render(request, "main/403.html", {})


def custom_error_404(request, exception):
    return render(request, "main/404.html", {})


def custom_error_500(request):
    return render(request, "main/500.html", {})


def delete_quote(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    if request.method == "POST":
        quote.delete()
        return redirect("home")
    return redirect("home")
