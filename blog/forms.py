from django import forms

from blog.models import Gratitude, Post


class BlogCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "body"]


class GratitudeForm(forms.ModelForm):
    class Meta:
        model = Gratitude
        fields = ["gratitude_text", "target"]
        widgets = {
            "gratitude_text": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "target": forms.SelectMultiple(attrs={"class": "form-control"}),
        }
