from django import forms

from feeds.models import Feed, FeedFolder


class FeedFolderForm(forms.ModelForm):
    class Meta:
        model = FeedFolder
        fields = ["name", "description"]


class FeedForm(forms.ModelForm):
    class Meta:
        model = Feed
        fields = ["folder", "title", "feed_url", "site_url"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["folder"].queryset = FeedFolder.objects.filter(user=user)
