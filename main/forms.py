from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ("email", "first_name", "last_name")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = UserChangeForm.Meta.fields
