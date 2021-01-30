from django.shortcuts import render
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    TemplateView,
)
from django.views.generic.edit import DeleteView
from healthstats.models import HealthEvent, Symptom
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from plotly.offline import plot
from plotly.graph_objs import Scatter


class HealthEventHomeView(LoginRequiredMixin, TemplateView):
    model = HealthEvent
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "stat_home.html"
    context_object_name = "all_health_events"


class HealthEventCreateView(LoginRequiredMixin, CreateView):
    model = HealthEvent
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "stat_new.html"
    fields = ["temperature", "symptoms", "feels_rating", "note"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class SymptomCreateView(LoginRequiredMixin, CreateView):
    model = Symptom
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "symptom_new.html"
    fields = ["name"]


class HealthEventListView(LoginRequiredMixin, ListView):
    model = HealthEvent
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "stat_list.html"
    context_object_name = "all_health_events"

    def get_queryset(self):
        return HealthEvent.objects.filter(author=self.request.user)


class SymptomListView(LoginRequiredMixin, ListView):
    model = Symptom
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "symptom_list.html"
    context_object_name = "all_symptoms"

    def get_queryset(self):
        return Symptom.objects.all()


class HealthEventDetailView(LoginRequiredMixin, DetailView):
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "stat_detail.html"
    context_object_name = "stat"

    def get_queryset(self):
        return HealthEvent.objects.filter(author=self.request.user).prefetch_related(
            "symptoms"
        )


class SymptomDetailView(LoginRequiredMixin, DetailView):
    model = Symptom
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "symptom_detail.html"
    context_object_name = "symptom"


class HealthEventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = HealthEvent
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "stat_update.html"
    readonly_fields = ["when"]
    fields = ["event_type", "value", "notes"]

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class SymptomUpdateView(LoginRequiredMixin, UpdateView):
    model = Symptom
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "symptom_update.html"
    fields = ["name"]


class HealthEventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = HealthEvent
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "stat_delete.html"
    success_url = reverse_lazy("blog_list")

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class SymptomDeleteView(LoginRequiredMixin, DeleteView):
    model = Symptom
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "symptom_delete.html"
    success_url = reverse_lazy("health_event_home")


def stat_plot_view(request):
    health_events = HealthEvent.objects.filter(author=request.user)
    y_data = [each.temperature for each in health_events]
    x_data = [each.when for each in health_events]
    plot_div = plot(
        [
            Scatter(
                x=x_data,
                y=y_data,
                mode="markers",
                name="test",
                opacity=0.8,
                marker_color="green",
            )
        ],
        output_type="div",
    )
    return render(request, "stat_plot.html", context={"plot_div": plot_div})
