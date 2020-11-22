from django.shortcuts import render
from django.views.generic import TemplateView



class LandingPageView(TemplateView):
    template_name = 'base.html'
    