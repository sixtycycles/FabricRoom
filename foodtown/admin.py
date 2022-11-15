from foodtown.models import Snack
from django.contrib import admin
from .models import Snack

# Register your models here.
@admin.register(Snack)
class SnackAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "quantity",
    )
    list_filter = ("quantity",)
