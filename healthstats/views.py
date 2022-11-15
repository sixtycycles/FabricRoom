import os
import csv
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
from plotly.graph_objs import Scatter
from .apple_health_data_parse import *
from datetime import datetime


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
    fields = ["author", "health_data_xml", "is_processed"]

    # def process_health_data(self):
    #     # call the script, output to csv for now.
    #     return HttpResponseRedirect(f"apple-health/update/{self.id}")

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


def process_apple_health_data(request, pk):
    file = AppleHealthUpload.objects.get(pk=pk)
    try:
        os.mkdir(f"/srv/code/media/processed/{request.user.first_name}")
    except OSError as error:
        print(error)
    data = HealthDataExtractor(
        f"/srv/code/media/{file.health_data_xml}",
        f"/srv/code/media/processed/{request.user.first_name}",
    )
    data.report_stats()
    data.extract()
    file.is_processed = True
    file.csv_data_dir = f"/srv/code/media/processed/{request.user.first_name}"
    file.save()
    return HttpResponseRedirect("/health/apple-health/process/success")


def import_processed_apple_health_data(request, pk):
    obj = AppleHealthUpload.objects.get(pk=pk)
    csv_dir = f"{obj.csv_data_dir}"
    heart_rate_path = f"{csv_dir}/HeartRate.csv"

    # HearRate.csv header fields:
    # sourceName(0), sourceVersion(1), device(2), type(3), unit(4), creationDate(5), startDate(6), endDate(7), value(8)
    with open(heart_rate_path) as f:
        reader = csv.reader(f)
        # dont spend hours troubleshooting the header data?
        next(reader)
        # actual data.
        for row in reader:
            c_date = datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S %z")
            created_date = datetime.strftime(c_date, "%Y-%m-%d %H:%M:%S.%f")
            s_date = datetime.strptime(row[6], "%Y-%m-%d %H:%M:%S %z")
            start_date = datetime.strftime(s_date, "%Y-%m-%d %H:%M:%S.%f")
            e_date = datetime.strptime(row[7], "%Y-%m-%d %H:%M:%S %z")
            end_date = datetime.strftime(e_date, "%Y-%m-%d %H:%M:%S.%f")

            _, created = HeartRate.objects.get_or_create(
                author=request.user,
                creation_date=created_date,
                start_date=start_date,
                end_date=end_date,
                value=row[8],
            )
        # tell the db its imported.
        obj.is_imported = True
        obj.save()

    return HttpResponseRedirect("/health/apple-health/process/success")


def process_file_success(request):

    return render(request, "process_success.html")


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
                marker=dict(
                    size=3,
                    color=[sample.value**3 for sample in heart_rates],
                    colorscale="gray",
                    line_width=0,
                ),
                # marker_color="blue",
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
    step_data = StepData.objects.filter(author=request.user)
    temp_data = (
        HealthEvent.objects.filter(author=request.user)
        .exclude(temperature=None)
        .exclude(note="")
    )

    dfo = oxygen_data.to_timeseries(index="start_date")
    dft = temp_data.to_timeseries(index="when")
    day_average = dfo.value.rolling(7).mean().shift(-3)
    day_average_t = dft.value.rolling(7).mean().shift(-3)

    oxygen_temperature_plot = plot(
        [
            Scatter(
                x=[sample.creation_date for sample in oxygen_data],
                y=day_average * 100,
                # y=[sample.value*100 for sample in oxygen_data],
                mode="markers",
                name="oxygen",
                opacity=0.8,
                marker_color="red",
            ),
            Scatter(
                x=[sample.when for sample in temp_data],
                y=day_average_t,
                # y=[sample.temperature for sample in temp_data],
                mode="markers",
                name="temp",
                opacity=0.8,
                marker_color="black",
                hovertext=[sample.note for sample in temp_data],
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
