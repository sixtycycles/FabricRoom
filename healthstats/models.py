from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model


class Symptom(models.Model):
    name = models.SlugField(verbose_name="Symptom name", max_length=200, unique=True)
    description = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("symptom_detail", args=[str(self.name)])

    # override save to save slug only on creation so urls dont change .


class HealthEvent(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    when = models.DateTimeField(auto_now_add=True)
    symptoms = models.ManyToManyField(
        Symptom,
        related_name="symptoms",
        blank=True,
        help_text="hold command or ctrl key to select more than one symptom",
    )
    temperature = models.FloatField(
        verbose_name="what is your temperature right now",
        blank=True,
        null=True,
        help_text="temperature in Farenheit please, 1 or more decimal places",
    )
    note = models.TextField(
        verbose_name="Are there any notes related to this event?", blank=True, null=True
    )
    feels_rating = models.IntegerField(
        blank=True,
        null=True,
        help_text="Overall feelings impression. enter a number between 0 and 10, 0 is bad, 10 is good",
    )

    def __str__(self):
        return f"{self.author.first_name} - @{self.when}"

    def get_absolute_url(self):
        return reverse("stat_detail", args=[str(self.id)])

    def get_symptoms(self):
        return self.symptoms
