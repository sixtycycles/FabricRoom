from django.shortcuts import render
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    TemplateView,
)
from django.views.generic.edit import DeleteView
from healthstats.models import (
    HealthEvent,
    Symptom,
    HeartRate,
    StepData,
    OxygenData,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from plotly.offline import plot
from plotly.graph_objs import Scatter


class HealthEventHomeView(LoginRequiredMixin, TemplateView):
    model = HealthEvent
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "home.html"
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
    # related_events = symptom.symptom_set.all()
    # def get_queryset(self):
    #     return Symptom.objects.get(pk=self.request.id).prefetch_related("health_event")


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
    return render(request, "stat_plot.html", context={})


def temp_stat_plot_view(request):

    health_events = HealthEvent.objects.filter(author=request.user)
    onlytemps = HealthEvent.objects.filter(author=request.user).exclude(
        temperature=None
    )
    df = health_events.to_timeseries(index="when")
    seven_day_average = df.temperature.rolling(7).mean().shift(-3)
    raw_temp_data = plot(
        [
            Scatter(
                x=[event.when for event in onlytemps],
                y=[event.temperature for event in onlytemps],
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
                x=[event.when for event in onlytemps],
                y=seven_day_average,
                mode="lines+markers",
                name="7 day rolling average temperature",
                opacity=0.8,
                marker_color="blue",
            ),
        ],
        output_type="div",
    )
    return render(
        request,
        "stat_plot_temp.html",
        context={
            "seven_day_rolling_average": seven_day_rolling_average,
            "raw_temp_data": raw_temp_data,
        },
    )


def heart_stat_plot_view(request):
    heart_rates = HeartRate.objects.filter(author=request.user)
    heart_rate = plot(
        [
            Scatter(
                x=[sample.creation_date for sample in heart_rates],
                y=[sample.value for sample in heart_rates],
                mode="markers",
                name="Heart rate from apple watch",
                opacity=0.8,
                marker_color="blue",
            ),
        ],
        output_type="div",
    )
    return render(
        request,
        "stat_plot_heart.html",
        context={
            "heart_rate": heart_rate,
        },
    )


def steps_stat_plot_view(request):

    steps_data = StepData.objects.filter(author=request.user)
    # step_dict = {event.creation_date: event.value for event in step_data}
    step_data = plot(
        [
            Scatter(
                x=[sample.creation_date for sample in steps_data],
                y=[sample.value for sample in steps_data],
                mode="lines+markers",
                name="Steps from apple watch",
                opacity=0.8,
                marker_color="blue",
            ),
        ],
        output_type="div",
    )
    return render(
        request,
        "stat_plot_steps.html",
        context={
            "step_data": step_data,
        },
    )


def oxygen_stat_plot_view(request):
    oxygen_data = OxygenData.objects.filter(author=request.user)
    oxygen_data_plot = plot(
        [
            Scatter(
                x=[sample.creation_date for sample in oxygen_data],
                y=[sample.value for sample in oxygen_data],
                mode="lines+markers",
                name="Heart rate from apple watch",
                opacity=0.8,
                marker_color="brown",
            ),
        ],
        output_type="div",
    )
    return render(
        request,
        "stat_plot_oxygen.html",
        context={
            "oxygen_data": oxygen_data_plot,
        },
    )


def oxygen_temperature_stat_plot_view(request):
    oxygen_data = OxygenData.objects.filter(author=request.user)
    temp_data = HealthEvent.objects.filter(author=request.user).exclude(temperature=None)

    df = oxygen_data.to_timeseries(index="creation_date")
    day_average = df.value.rolling(7).mean().shift(-3)
    oxygen_temperature_plot = plot(
        [
            Scatter(
                x=[sample.creation_date for sample in oxygen_data],
                y=day_average,
                # y=[sample.value*100 for sample in oxygen_data],
                mode="markers",
                name="oxygen",
                opacity=0.8,
                marker_color="blue",
            ),
            Scatter(
                x=[sample.when for sample in temp_data],
                y=[sample.temperature for sample in temp_data],
                mode="markers",
                name="Heart rate from apple watch",
                opacity=0.8,
                marker_color="green",
                hovertext=[sample.note for sample in temp_data]
            ),
        ],
        output_type="div",
    )
    return render(
        request,
        "stat_plot_oxygen.html",
        context={
            "oxygen_data": oxygen_temperature_plot,
        },
    )