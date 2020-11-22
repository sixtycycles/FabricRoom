from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from main.models import Tag, Note, Profile


class LandingPageView(TemplateView):
    template_name = 'home.html'
   
    
    def get_context_data(self, **kwargs):
        context = super(LandingPageView, self).get_context_data(**kwargs)
        context['user'] =  self.request.user
        context['tags'] = Tag.objects.all()
        context['notes'] = Note.objects.all()
        return context

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