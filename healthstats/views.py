from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    TemplateView,
)
from django.views.generic.edit import DeleteView
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


def _build_svg_chart(title, series, y_label="", unit=""):
    width, height = 640, 260
    padding_left, padding_right = 40, 20
    padding_top, padding_bottom = 24, 36
    chart_width = width - padding_left - padding_right
    chart_height = height - padding_top - padding_bottom

    if not series:
        return (
            f'<div class="card p-3 mt-3">'
            f'<h5 class="mb-3">{title}</h5>'
            f'<svg viewBox="0 0 {width} {height}" width="100%" height="260" role="img" aria-label="{title}">'
            f'<rect x="0" y="0" width="{width}" height="{height}" fill="white" rx="8" />'
            f'<line x1="{padding_left}" y1="{padding_top}" x2="{padding_left}" y2="{height - padding_bottom}" stroke="#111827" stroke-width="1" />'
            f'<line x1="{padding_left}" y1="{height - padding_bottom}" x2="{width - padding_right}" y2="{height - padding_bottom}" stroke="#111827" stroke-width="1" />'
            f'<text x="{width / 2}" y="{height / 2}" text-anchor="middle" font-size="14" fill="#6b7280">No data available yet</text>'
            f'</svg></div>'
        )

    values = [value for _, value in series]
    min_value = min(values)
    max_value = max(values)
    if max_value == min_value:
        max_value = min_value + 1

    def scale_x(index):
        if len(series) == 1:
            return padding_left + chart_width / 2
        return padding_left + (index / (len(series) - 1)) * chart_width

    def scale_y(value):
        ratio = (value - min_value) / (max_value - min_value)
        return padding_top + chart_height - (ratio * chart_height)

    points = []
    for index, (_, value) in enumerate(series):
        x = scale_x(index)
        y = scale_y(value)
        points.append(f"{x:.1f},{y:.1f}")

    grid_lines = []
    for step in range(4):
        ratio = step / 3
        y = padding_top + chart_height * ratio
        grid_lines.append(
            f'<line x1="{padding_left}" y1="{y:.1f}" x2="{width - padding_right}" y2="{y:.1f}" stroke="#e5e7eb" stroke-width="1" />'
        )

    circles = []
    for index, (_, value) in enumerate(series):
        x = scale_x(index)
        y = scale_y(value)
        circles.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="#2563eb" />'
        )

    y_axis_label = f"{y_label} {unit}".strip()
    return (
        f'<div class="card p-3 mt-3">'
        f'<h5 class="mb-3">{title}</h5>'
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="260" role="img" aria-label="{title}">'
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="white" rx="8" />'
        f'<line x1="{padding_left}" y1="{padding_top}" x2="{padding_left}" y2="{height - padding_bottom}" stroke="#111827" stroke-width="1" />'
        f'<line x1="{padding_left}" y1="{height - padding_bottom}" x2="{width - padding_right}" y2="{height - padding_bottom}" stroke="#111827" stroke-width="1" />'
        f'{"".join(grid_lines)}'
        f'<polyline points="{" ".join(points)}" fill="none" stroke="#2563eb" stroke-width="2.5" />'
        f'{"".join(circles)}'
        f'<text x="{padding_left - 10}" y="{padding_top - 8}" text-anchor="end" font-size="12" fill="#374151">{max_value:.1f}</text>'
        f'<text x="{padding_left - 10}" y="{height - padding_bottom + 14}" text-anchor="end" font-size="12" fill="#374151">{min_value:.1f}</text>'
        f'<text x="{width / 2}" y="{height - 6}" text-anchor="middle" font-size="12" fill="#374151">Date</text>'
        f'<text x="12" y="{height / 2}" text-anchor="middle" font-size="12" fill="#374151" transform="rotate(-90 12 {height / 2})">{y_axis_label}</text>'
        f'</svg></div>'
    )


class HealthEventHomeView(LoginRequiredMixin, TemplateView):
    model = HealthEvent
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "healthstats/stat_home.html"
    context_object_name = "all_health_events"


class HealthEventCreateView(LoginRequiredMixin, CreateView):
    model = HealthEvent
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "healthstats/stat_new.html"
    fields = ["temperature", "symptoms", "note"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class BPCreateView(LoginRequiredMixin, CreateView):
    model = BloodPressure
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "healthstats/bp_new.html"
    fields = ["systolic_pressure", "diastolic_pressure", "position"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


@method_decorator(vary_on_cookie, name="dispatch")
@method_decorator(cache_page(settings.CACHE_TTL), name="dispatch")
class BPListView(LoginRequiredMixin, ListView):
    model = BloodPressure
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "healthstats/bp_list.html"
    context_object_name = "all_bps"

    def get_queryset(self):
        return BloodPressure.objects.filter(author=self.request.user)


@method_decorator(vary_on_cookie, name="dispatch")
@method_decorator(cache_page(settings.CACHE_TTL), name="dispatch")
class BPDetailView(LoginRequiredMixin, DetailView):
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "healthstats/bp_detail.html"
    context_object_name = "bp"

    def get_queryset(self):
        return BloodPressure.objects.filter(author=self.request.user)


class BPUpdateView(LoginRequiredMixin, UpdateView):
    model = BloodPressure
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "healthstats/bp_update.html"
    fields = ["systolic_pressure", "diastolic_pressure"]

    def get_queryset(self):
        return BloodPressure.objects.filter(author=self.request.user)


class BPDeleteView(LoginRequiredMixin, DeleteView):
    model = BloodPressure
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "healthstats/bp_delete.html"
    success_url = reverse_lazy("bp_list")

    def get_queryset(self):
        return BloodPressure.objects.filter(author=self.request.user)


class SymptomCreateView(LoginRequiredMixin, CreateView):
    model = Symptom
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "healthstats/symptom_new.html"
    fields = ["slug"]


@method_decorator(vary_on_cookie, name="dispatch")
@method_decorator(cache_page(settings.CACHE_TTL), name="dispatch")
class HealthEventListView(LoginRequiredMixin, ListView):
    model = HealthEvent
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "healthstats/stat_list.html"
    context_object_name = "all_health_events"

    def get_queryset(self):
        return (
            HealthEvent.objects.filter(author=self.request.user)
            .prefetch_related("symptoms")
            .order_by("-when")
        )


@method_decorator(vary_on_cookie, name="dispatch")
@method_decorator(cache_page(settings.CACHE_TTL), name="dispatch")
class SymptomListView(LoginRequiredMixin, ListView):
    model = Symptom
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "healthstats/symptom_list.html"
    context_object_name = "all_symptoms"

    def get_queryset(self):
        return Symptom.objects.all()


@method_decorator(vary_on_cookie, name="dispatch")
@method_decorator(cache_page(settings.CACHE_TTL), name="dispatch")
class HealthEventDetailView(LoginRequiredMixin, DetailView):
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "healthstats/stat_detail.html"
    context_object_name = "stat"

    def get_queryset(self):
        return HealthEvent.objects.filter(author=self.request.user).prefetch_related(
            "symptoms"
        )


@method_decorator(vary_on_cookie, name="dispatch")
@method_decorator(cache_page(settings.CACHE_TTL), name="dispatch")
class SymptomDetailView(LoginRequiredMixin, DetailView):
    model = Symptom
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "healthstats/symptom_detail.html"
    context_object_name = "symptom"
    # related_events = symptom.symptom_set.all()
    # def get_queryset(self):
    #     return Symptom.objects.get(pk=self.request.id).prefetch_related("health_event")


class HealthEventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = HealthEvent
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "healthstats/stat_update.html"
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
    template_name = "healthstats/symptom_update.html"
    fields = ["slug"]


class HealthEventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = HealthEvent
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "healthstats/stat_delete.html"
    success_url = reverse_lazy("stat_list")

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class SymptomDeleteView(LoginRequiredMixin, DeleteView):
    model = Symptom
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "healthstats/symptom_delete.html"
    success_url = reverse_lazy("health_event_home")


@method_decorator(vary_on_cookie, name="dispatch")
@method_decorator(cache_page(settings.CACHE_TTL), name="dispatch")
class AppleHealthDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = AppleHealthUpload
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "healthstats/apple_health_detail.html"
    context_object_name = "object"

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def get_queryset(self):
        return AppleHealthUpload.objects.filter(author=self.request.user)


class AppleHealthUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = AppleHealthUpload
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "healthstats/apple_health_update.html"
    fields = ["author", "health_data_xml"]

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def get_queryset(self):
        return AppleHealthUpload.objects.filter(author=self.request.user)


class AppleHealthDeleteView(LoginRequiredMixin, DeleteView):
    model = AppleHealthUpload
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "healthstats/apple_health_delete.html"
    success_url = reverse_lazy("apple-health-list")
    context_object_name = "obj"

    def get_queryset(self):
        return AppleHealthUpload.objects.filter(author=self.request.user)


@method_decorator(vary_on_cookie, name="dispatch")
@method_decorator(cache_page(settings.CACHE_TTL), name="dispatch")
class AppleHealthListView(LoginRequiredMixin, ListView):
    model = AppleHealthUpload
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    raise_exception = True
    template_name = "healthstats/apple_health_list.html"
    context_object_name = "all_uploads"

    def get_queryset(self):
        return AppleHealthUpload.objects.filter(author=self.request.user)


@login_required
def upload_file(request):
    if request.method == "POST":
        form = AppleHealthUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return HttpResponseRedirect("upload/success")
    else:
        form = AppleHealthUploadForm()
    return render(request, "healthstats/upload.html", {"form": form})


@login_required
def upload_file_success(request):

    return render(request, "healthstats/upload_success.html")


@login_required
def stat_plot_view(request):
    return render(request, "healthstats/stat_plot.html", context={})


@login_required
@vary_on_cookie
@cache_page(settings.CACHE_TTL)
def temp_stat_plot_view(request):
    health_events = list(
        HealthEvent.objects.filter(author=request.user)
        .exclude(temperature=None)
        .order_by("when")
        .values_list("when", "temperature")
    )
    timestamps, temperatures = zip(*health_events) if health_events else ([], [])

    raw_temp_data = _build_svg_chart("Temperature", list(zip(timestamps, temperatures)), y_label="°F")

    if len(temperatures) >= 7:
        rolling_series = []
        for index in range(6, len(temperatures)):
            window = temperatures[index - 6 : index + 1]
            rolling_series.append((timestamps[index], sum(window) / len(window)))
        seven_day_rolling_average = _build_svg_chart(
            "7-day rolling average",
            rolling_series,
            y_label="°F",
        )
    else:
        seven_day_rolling_average = _build_svg_chart(
            "7-day rolling average",
            [],
            y_label="°F",
        )

    return render(
        request,
        "healthstats/stat_plot_temp.html",
        context={
            "seven_day_rolling_average": seven_day_rolling_average,
            "raw_temp_data": raw_temp_data,
        },
    )


@login_required
@vary_on_cookie
@cache_page(settings.CACHE_TTL)
def heart_stat_plot_view(request):
    heart_rates = list(
        HeartRate.objects.filter(author=request.user)
        .order_by("creation_date")
        .values_list("creation_date", "value")
    )
    if heart_rates:
        x_values, y_values = zip(*heart_rates)
        heart_rate = _build_svg_chart(
            "Heart Rate",
            list(zip(x_values, y_values)),
            y_label="BPM",
            unit="bpm",
        )
    else:
        heart_rate = _build_svg_chart("Heart Rate", [], y_label="BPM", unit="bpm")

    return render(
        request,
        "healthstats/stat_plot_heart.html",
        context={
            "heart_rate": heart_rate,
        },
    )


@login_required
@vary_on_cookie
@cache_page(settings.CACHE_TTL)
def steps_stat_plot_view(request):
    steps_data = list(
        StepData.objects.filter(author=request.user)
        .order_by("creation_date")
        .values_list("creation_date", "value")
    )
    if steps_data:
        x_values, y_values = zip(*steps_data)
        step_data = _build_svg_chart(
            "Steps",
            list(zip(x_values, y_values)),
            y_label="Steps",
        )
    else:
        step_data = _build_svg_chart("Steps", [], y_label="Steps")

    return render(
        request,
        "healthstats/stat_plot_steps.html",
        context={
            "step_data": step_data,
        },
    )


@login_required
@vary_on_cookie
@cache_page(settings.CACHE_TTL)
def oxygen_stat_plot_view(request):
    oxygen_data = list(
        OxygenData.objects.filter(author=request.user)
        .order_by("creation_date")
        .values_list("creation_date", "value")
    )
    if oxygen_data:
        x_values, y_values = zip(*oxygen_data)
        oxygen_data_plot = _build_svg_chart(
            "Oxygen Saturation",
            list(zip(x_values, y_values)),
            y_label="%",
        )
    else:
        oxygen_data_plot = _build_svg_chart("Oxygen Saturation", [], y_label="%")

    return render(
        request,
        "healthstats/stat_plot_oxygen.html",
        context={
            "oxygen_data": oxygen_data_plot,
        },
    )


@login_required
@vary_on_cookie
@cache_page(settings.CACHE_TTL)
def oxygen_temperature_stat_plot_view(request):
    oxygen_data = list(
        OxygenData.objects.filter(author=request.user)
        .order_by("creation_date")
        .values_list("creation_date", "value")
    )
    temp_data = list(
        HealthEvent.objects.filter(author=request.user)
        .exclude(temperature=None)
        .exclude(note="")
        .order_by("when")
        .values_list("when", "temperature")
    )

    combined_series = []
    if oxygen_data:
        oxygen_x, oxygen_y = zip(*oxygen_data)
        combined_series.extend(list(zip(oxygen_x, oxygen_y)))

    if temp_data:
        temp_x, temp_y = zip(*temp_data)
        combined_series.extend(list(zip(temp_x, temp_y)))

    if combined_series:
        oxygen_temperature_plot = _build_svg_chart(
            "Oxygen + Temperature",
            combined_series,
            y_label="Value",
        )
    else:
        oxygen_temperature_plot = _build_svg_chart("Oxygen + Temperature", [], y_label="Value")

    return render(
        request,
        "healthstats/stat_plot_oxygen.html",
        context={
            "oxygen_data": oxygen_temperature_plot,
        },
    )
