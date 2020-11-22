from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class LandingPageView(TemplateView):
    template_name = 'home.html'
    

class AboutPageView(TemplateView):
    template_name = 'about.html'


class PrivateHome(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    raise_exception = True

    template_name = 'private_home.html'

    def get_context_data(self, **kwargs):
        context = super(PrivateHome, self).get_context_data(**kwargs)
        context['user'] =  self.request.user
        return context