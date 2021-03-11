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
    fields = ["slug"]


class HealthEventListView(LoginRequiredMixin, ListView):
    model = HealthEvent
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "stat_list.html"
    context_object_name = "all_health_events"

    def get_queryset(self):
        return HealthEvent.objects.filter(author=self.request.user).order_by("-when")


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
    readonly_fields = ["author", "when"]
    fields = ["temperature", "symptoms", "note", "feels_rating"]

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class SymptomUpdateView(LoginRequiredMixin, UpdateView):
    model = Symptom
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "symptom_update.html"
    fields = ["slug"]


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
    onlytemps = HealthEvent.objects.filter(author=request.user).exclude(
        temperature=None
    )
    temperatures = [event.temperature for event in onlytemps]
    datetime_of_sample = [event.when for event in onlytemps]
    notes = [event.note for event in health_events]
    symptoms = [event.symptoms for event in health_events]
    df = health_events.to_timeseries(index="when")
    seven_day_average = df.temperature.rolling(7).mean().shift(-3)

    raw_temp_data = plot(
        [
            Scatter(
                x=datetime_of_sample,
                y=temperatures,
                mode="markers",
                name="raw daily temperatures",
                opacity=0.8,
                marker_color="green",
            ),
        ],
        output_type="div",
    )

    seven_day_rolling_average = plot(
        [
            Scatter(
                x=datetime_of_sample,
                y=seven_day_average,
                mode="markers",
                name="7 day rolling average temperature",
                opacity=0.8,
                marker_color="blue",
            ),
        ],
        output_type="div",
    )

    return render(
        request,
        "stat_plot.html",
        context={
            "seven_day_rolling_average": seven_day_rolling_average,
            "raw_temp_data": raw_temp_data,
            # "dates": x_data,
            # "test": newlist,
            # "notes": notes,
            # "symptoms": symptoms,
        },
    )


# def pandas_view(request):
#     health_events = HealthEvent.objects.filter(author=request.user)
#     df = health_events.to_timeseries(index='when')
#     df["7_day_average"] = df.temperature.rolling(7).mean().shift(-3)
#     return render(request, 'pandas.html', {'df': df.to_html()})