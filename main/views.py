import subprocess

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.generic import TemplateView
from django.views import View
from .models import PrivacyPolicy, ManagementCommandRun

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

        if user.is_superuser:
            context["management_command_runs"] = ManagementCommandRun.objects.all()[:10]

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


class UtilitiesView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "main/utilities.html"

    def test_func(self):
        return self.request.user.is_superuser


class TriggerManagementCommandView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "/accounts/login/"
    raise_exception = True

    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request, *args, **kwargs):
        command_name = kwargs.get("command_name")
        allowed_commands = settings.MANAGEMENT_COMMAND_SYSTEMD_SERVICES

        if command_name not in allowed_commands:
            return HttpResponseForbidden("Unknown or disallowed management command.")

        service_name = allowed_commands[command_name]
        sudo_path = settings.MANAGEMENT_COMMAND_SUDO_PATH
        systemctl_path = settings.MANAGEMENT_COMMAND_SYSTEMCTL_PATH
        command = [sudo_path, "-n", systemctl_path, "start", service_name]

        started_at = timezone.now()
        try:
            proc = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
        except subprocess.TimeoutExpired:
            finished_at = timezone.now()
            ManagementCommandRun.objects.create(
                command_name=command_name,
                status=ManagementCommandRun.STATUS_FAILED,
                summary=f"Failed to trigger {service_name}: timed out while running systemctl.",
                details=f"Executed: {' '.join(command)}\nTimed out after 15 seconds.",
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=max((finished_at - started_at).total_seconds(), 0.0),
            )
            return redirect("home")

        if proc.returncode != 0:
            stderr = (proc.stderr or "").strip()
            stdout = (proc.stdout or "").strip()
            summary = stderr or stdout or "systemctl start failed."
            finished_at = timezone.now()
            ManagementCommandRun.objects.create(
                command_name=command_name,
                status=ManagementCommandRun.STATUS_FAILED,
                summary=f"Failed to trigger {service_name}: {summary}",
                details=(
                    f"Executed: {' '.join(command)}\n"
                    f"Exit code: {proc.returncode}\n"
                    f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
                ),
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=max((finished_at - started_at).total_seconds(), 0.0),
            )
            return redirect("home")

        finished_at = timezone.now()
        ManagementCommandRun.objects.create(
            command_name=command_name,
            status=ManagementCommandRun.STATUS_SUCCESS,
            summary=f"Triggered systemd service {service_name}.",
            details=f"Executed: {' '.join(command)}",
            started_at=started_at,
            finished_at=finished_at,
            duration_seconds=max((finished_at - started_at).total_seconds(), 0.0),
        )

        return redirect("home")


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
