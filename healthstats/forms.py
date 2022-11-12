from django import forms
from healthstats.models import AppleHealthUpload


class AppleHealthUploadForm(forms.ModelForm):
    class Meta:
        model = AppleHealthUpload
        fields = (
            "author",
            "health_data_xml",
        )
        labels = {"author": "Who owns this data?", "health_data_xml": "Choose a File (export.xml):"}
        exclude = ("is_processed",)


