from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import DeleteView
from healthstats.models import HealthEvent, EventType
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy


class HealthEventListView(ListView):
    model = HealthEvent
    template_name = 'stat_list.html'
    context_object_name = 'all_health_events'

    def get_queryset(self):
        return HealthEvent.objects.all()


class HealthEventDetailView(DetailView):  # new model = HealthEvent
    model = HealthEvent
    template_name = 'stat_detail.html'
    context_object_name = 'post'


class HealthEventCreateView(LoginRequiredMixin, CreateView):
    model = HealthEvent
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    raise_exception = True
    template_name = 'stat_new.html'
    fields = ['event_type', 'value', 'notes']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class HealthEventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = HealthEvent
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    raise_exception = True
    template_name = 'stat_update.html'
    fields = ['when', 'event_type', 'value', 'notes']

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class HealthEventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = HealthEvent
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    raise_exception = True
    template_name = 'stat_delete.html'
    success_url = reverse_lazy('blog_list')

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user
