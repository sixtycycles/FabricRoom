from django.shortcuts import render
from .models import Snack
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    TemplateView,
)


class SnackCreateView(LoginRequiredMixin, CreateView):
    model = Snack
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "new_snack.html"
    fields = ["name", "quantity"]


class SnackListView(LoginRequiredMixin, ListView):
    model = Snack
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "snack_list.html"
    context_object_name = "all_snacks"

    def get_queryset(self):
        return Snack.objects.all().order_by("quantity")


class SnackOrderView(TemplateView):
    model = Snack
