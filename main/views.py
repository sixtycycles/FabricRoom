from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from main.forms import CustomUserChangeForm, CustomUserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView


class LandingPageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(LandingPageView, self).get_context_data(**kwargs)
        context["user"] = self.request.user
        # context['notes'] = Note.objects.all()
        # context['posts'] = Post.objects.filter(published=True)
        # context['tags'] = Tag.objects.all()
        return context


class AboutPageView(TemplateView):
    template_name = "about.html"


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class PrivateHome(LoginRequiredMixin, TemplateView):
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True

    template_name = "private_home.html"

    def get_context_data(self, **kwargs):
        context = super(PrivateHome, self).get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


# Custom http error code pages
def custom_error_403(request, exception):
    return render(request, "403.html", {})


def custom_error_404(request, exception):
    return render(request, "404.html", {})


def custom_error_500(request):
    return render(request, "500.html", {})
