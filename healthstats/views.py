import os
import logging
from django.shortcuts import render
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    TemplateView,
)
from django.views.generic.edit import DeleteView, ProcessFormView
from healthstats.models import (
    AppleHealthUpload,
    BloodPressure,
    HealthEvent,
    Symptom,
    HeartRate,
    StepData,
    OxygenData,
)
from healthstats.forms import AppleHealthUploadForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from plotly.offline import plot
import plotly.graph_objects as go
from datetime import datetime


def _render_plotly_figure(fig):
    return plot(
        fig,
        output_type="div",
        include_plotlyjs="cdn",
        config={
            "responsive": True,
            "displayModeBar": False,
            "scrollZoom": True,
        },
    )


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
    fields = ["temperature", "symptoms", "note"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class BPCreateView(LoginRequiredMixin, CreateView):
    model = BloodPressure
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "bp_new.html"
    fields = ["systolic_pressure", "diastolic_pressure", "position"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class BPListView(LoginRequiredMixin, ListView):
    model = BloodPressure
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "bp_list.html"
    context_object_name = "all_bps"

    def get_queryset(self):
        return BloodPressure.objects.all()


class BPDetailView(LoginRequiredMixin, DetailView):
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "bp_detail.html"
    context_object_name = "bp"

    def get_queryset(self):
        return BloodPressure.objects.filter(author=self.request.user)


class BPUpdateView(LoginRequiredMixin, UpdateView):
    model = BloodPressure
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "bp_update.html"
    fields = ["systolic_pressure", "diastolic_pressure"]


class BPDeleteView(LoginRequiredMixin, DeleteView):
    model = BloodPressure
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "bp_delete.html"
    success_url = reverse_lazy("bp_list")


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
    fields = [
        "temperature",
        "symptoms",
        "note",
    ]

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
    success_url = reverse_lazy("stat_list")

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


class AppleHealthDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = AppleHealthUpload
    login_url = "/accounts/login"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "apple_health_detail.html"
    context_object_name = "object"

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class AppleHealthUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = AppleHealthUpload
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "apple_health_update.html"
    fields = ["author", "health_data_xml"]

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class AppleHealthDeleteView(LoginRequiredMixin, DeleteView):
    model = AppleHealthUpload
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "apple_health_delete.html"
    success_url = reverse_lazy("apple-health-list")
    context_object_name = "obj"


class AppleHealthListView(LoginRequiredMixin, ListView):
    model = AppleHealthUpload
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "apple_health_list.html"
    context_object_name = "all_uploads"

    def get_queryset(self):
        return AppleHealthUpload.objects.filter(author=self.request.user)


def upload_file(request):
    if request.method == "POST":
        form = AppleHealthUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("upload/success")
    else:
        form = AppleHealthUploadForm()
    return render(request, "upload.html", {"form": form})


def upload_file_success(request):

    return render(request, "upload_success.html")


def stat_plot_view(request):
    return render(request, "stat_plot.html", context={})


def temp_stat_plot_view(request):
    health_events = (
        HealthEvent.objects.filter(author=request.user)
        .exclude(temperature=None)
        .order_by("when")
    )
    timestamps = [event.when for event in health_events]
    temperatures = [event.temperature for event in health_events]

    raw_temp_fig = go.Figure()
    raw_temp_fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=temperatures,
            mode="markers",
            name="Temperature",
            marker=dict(size=7, color="#2ca02c", opacity=0.75),
            hovertemplate="%{x}<br>%{y:.1f}°F<extra></extra>",
        )
    )
    raw_temp_fig.update_layout(
        template="plotly_white",
        title="Temperature",
        xaxis_title="Date",
        yaxis_title="°F",
        height=420,
        margin=dict(l=10, r=10, t=50, b=10),
        hovermode="x unified",
    )
    raw_temp_data = _render_plotly_figure(raw_temp_fig)

    if len(temperatures) >= 7:
        df = health_events.to_timeseries(index="when")
        seven_day_average = df.temperature.rolling(7).mean().dropna()
        seven_day_fig = go.Figure()
        seven_day_fig.add_trace(
            go.Scatter(
                x=seven_day_average.index,
                y=seven_day_average,
                mode="lines+markers",
                name="7-day rolling average",
                line=dict(color="#1f77b4", width=2),
                marker=dict(size=5, color="#1f77b4"),
                hovertemplate="%{x}<br>%{y:.1f}°F<extra></extra>",
            )
        )
        seven_day_fig.update_layout(
            template="plotly_white",
            title="7-day rolling average",
            xaxis_title="Date",
            yaxis_title="°F",
            height=420,
            margin=dict(l=10, r=10, t=50, b=10),
            hovermode="x unified",
        )
        seven_day_rolling_average = _render_plotly_figure(seven_day_fig)
    else:
        seven_day_rolling_average = "<p class='text-muted'>Not enough temperature data for a rolling average.</p>"

    return render(
        request,
        "stat_plot_temp.html",
        context={
            "seven_day_rolling_average": seven_day_rolling_average,
            "raw_temp_data": raw_temp_data,
        },
    )


def heart_stat_plot_view(request):
    heart_rates = HeartRate.objects.filter(author=request.user).order_by(
        "creation_date"
    )
    if heart_rates.exists():
        x_values = [sample.creation_date for sample in heart_rates]
        y_values = [sample.value for sample in heart_rates]

        heart_rate_fig = go.Figure()
        heart_rate_fig.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                mode="lines+markers",
                name="Heart Rate",
                line=dict(color="#e74c3c", width=2),
                marker=dict(size=6, color="#e74c3c", opacity=0.8),
                hovertemplate="%{x}<br>%{y:.0f} bpm<extra></extra>",
            )
        )
        heart_rate_fig.update_layout(
            template="plotly_white",
            title="Heart Rate",
            xaxis_title="Date",
            yaxis_title="BPM",
            height=420,
            margin=dict(l=10, r=10, t=50, b=10),
            hovermode="x unified",
        )
        heart_rate = _render_plotly_figure(heart_rate_fig)
    else:
        heart_rate = "<p class='text-muted'>No heart rate data available yet.</p>"

    return render(
        request,
        "stat_plot_heart.html",
        context={
            "heart_rate": heart_rate,
        },
    )


def steps_stat_plot_view(request):
    steps_data = StepData.objects.filter(author=request.user).order_by("creation_date")
    if steps_data.exists():
        x_values = [sample.creation_date for sample in steps_data]
        y_values = [sample.value for sample in steps_data]

        step_fig = go.Figure()
        step_fig.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                mode="lines+markers",
                name="Steps",
                line=dict(color="#4c72b0", width=2),
                marker=dict(size=6, color="#4c72b0", opacity=0.8),
                hovertemplate="%{x}<br>%{y:.0f} steps<extra></extra>",
            )
        )
        step_fig.update_layout(
            template="plotly_white",
            title="Steps",
            xaxis_title="Date",
            yaxis_title="Steps",
            height=420,
            margin=dict(l=10, r=10, t=50, b=10),
            hovermode="x unified",
        )
        step_data = _render_plotly_figure(step_fig)
    else:
        step_data = "<p class='text-muted'>No step data available yet.</p>"

    return render(
        request,
        "stat_plot_steps.html",
        context={
            "step_data": step_data,
        },
    )


def oxygen_stat_plot_view(request):
    oxygen_data = OxygenData.objects.filter(author=request.user).order_by(
        "creation_date"
    )
    if oxygen_data.exists():
        x_values = [sample.creation_date for sample in oxygen_data]
        y_values = [sample.value for sample in oxygen_data]

        oxygen_fig = go.Figure()
        oxygen_fig.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                mode="lines+markers",
                name="Oxygen Saturation",
                line=dict(color="#9c5b00", width=2),
                marker=dict(size=6, color="#9c5b00", opacity=0.8),
                hovertemplate="%{x}<br>%{y:.1f}%<extra></extra>",
            )
        )
        oxygen_fig.update_layout(
            template="plotly_white",
            title="Oxygen Saturation",
            xaxis_title="Date",
            yaxis_title="%",
            height=420,
            margin=dict(l=10, r=10, t=50, b=10),
            hovermode="x unified",
        )
        oxygen_data_plot = _render_plotly_figure(oxygen_fig)
    else:
        oxygen_data_plot = "<p class='text-muted'>No oxygen data available yet.</p>"

    return render(
        request,
        "stat_plot_oxygen.html",
        context={
            "oxygen_data": oxygen_data_plot,
        },
    )


def oxygen_temperature_stat_plot_view(request):
    oxygen_data = OxygenData.objects.filter(author=request.user).order_by(
        "creation_date"
    )
    temp_data = (
        HealthEvent.objects.filter(author=request.user)
        .exclude(temperature=None)
        .exclude(note="")
        .order_by("when")
    )

    oxygen_temperature_fig = go.Figure()

    if oxygen_data.exists():
        oxygen_x = [sample.creation_date for sample in oxygen_data]
        oxygen_y = [sample.value for sample in oxygen_data]
        oxygen_temperature_fig.add_trace(
            go.Scatter(
                x=oxygen_x,
                y=oxygen_y,
                mode="lines+markers",
                name="Oxygen",
                line=dict(color="#d62728", width=2),
                marker=dict(size=6, color="#d62728", opacity=0.8),
                hovertemplate="%{x}<br>%{y:.1f}%<extra></extra>",
            )
        )

    if temp_data.exists():
        temp_x = [sample.when for sample in temp_data]
        temp_y = [sample.temperature for sample in temp_data]
        oxygen_temperature_fig.add_trace(
            go.Scatter(
                x=temp_x,
                y=temp_y,
                mode="markers",
                name="Temperature",
                marker=dict(size=7, color="#2f2f2f", opacity=0.8),
                hovertemplate="%{x}<br>%{y:.1f}°F<extra></extra>",
            )
        )

    if oxygen_temperature_fig.data:
        oxygen_temperature_fig.update_layout(
            template="plotly_white",
            title="Oxygen + Temperature",
            xaxis_title="Date",
            yaxis_title="Value",
            height=420,
            margin=dict(l=10, r=10, t=50, b=10),
            hovermode="x unified",
        )
        oxygen_temperature_plot = _render_plotly_figure(oxygen_temperature_fig)
    else:
        oxygen_temperature_plot = (
            "<p class='text-muted'>No chart data available yet.</p>"
        )

    return render(
        request,
        "stat_plot_oxygen.html",
        context={
            "oxygen_data": oxygen_temperature_plot,
        },
    )
