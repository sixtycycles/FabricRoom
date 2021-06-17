from django import forms
from healthstats.models import AppleHealthUpload

# from django.utils import timezone

# class HealthEventForm(forms.Form):
#     event_type = forms.CharField(label='Your name', max_length=100)
#     when = forms.DateTimeField(autonow_add=True, default=timezone.now)


class AppleHealthUpload(forms.Form):
    file = forms.FileField()
