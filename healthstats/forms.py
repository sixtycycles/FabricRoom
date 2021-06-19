from django import forms
from healthstats.models import AppleHealthUpload


class AppleHealthUploadForm(forms.ModelForm):
    class Meta:
        model = AppleHealthUpload
        fields = (
            "author",
            "health_data_xml",
        )
        exclude = ("is_processed",)


