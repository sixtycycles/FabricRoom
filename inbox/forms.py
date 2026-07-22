from django import forms
from django.contrib.auth import get_user_model

from inbox.models import Message


class MessageComposeForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(
        queryset=get_user_model().objects.none(),
        required=False,
    )

    class Meta:
        model = Message
        fields = ["recipient", "subject", "body"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 8}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["recipient"].queryset = get_user_model().objects.order_by("username")

    def validate_for_send(self):
        is_valid = True
        recipient = self.cleaned_data.get("recipient")
        body = (self.cleaned_data.get("body") or "").strip()

        if recipient is None:
            self.add_error("recipient", "Recipient is required to send a message.")
            is_valid = False
        if not body:
            self.add_error("body", "Message body is required to send.")
            is_valid = False
        return is_valid
