from datetime import datetime
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django_pandas.managers import DataFrameManager


class Symptom(models.Model):
    slug = models.SlugField(
        verbose_name="Symptom name",
        max_length=200,
        unique=True,
        help_text="Enter the name in with hyphens instead of spaces, like 'my-symptom-name'",
    )
    description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        verbose_name = "Symptom"
        verbose_name_plural = "Symptoms"
        ordering = ["slug"]

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse("symptom_detail", args=[str(self.slug)])


class HealthEvent(models.Model):
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="health_events",
    )
    when = models.DateTimeField(auto_now_add=True)
    symptoms = models.ManyToManyField(
        Symptom,
        related_name="health_events",
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
    # feels_rating = models.IntegerField(
    #     blank=True,
    #     null=True,
    #     help_text="How bad do you feel? Enter a number between 0 and 10, where 10 is bad, 0 is good",
    # )
    objects = DataFrameManager()

    class Meta:
        verbose_name = "Health Event"
        verbose_name_plural = "Health Events"
        ordering = ["-when"]

    def __str__(self):
        return f"{self.author.first_name} - @{self.when}"

    def get_absolute_url(self):
        return reverse("stat_detail", args=[str(self.id)])

    def get_symptoms(self):
        return self.symptoms.all()


class BloodPressure(models.Model):

    POSITIONS = (
        ('sitting', 'Sitting'),
        ('laying down','Laying Down'),
        ('standing', 'Standing')
    )
    sample_date = models.DateTimeField(auto_now_add=True)
    systolic_pressure = models.PositiveIntegerField(default=0)
    diastolic_pressure = models.PositiveIntegerField(default=0)
    position = models.CharField(max_length=15, choices = POSITIONS, default = "sitting")
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="blood_pressures",
    )

    class Meta:
        verbose_name = "Blood Pressure"
        verbose_name_plural = "Blood Pressures"
        ordering = ["-sample_date"]

    def __str__(self) -> str:
        return f"{self.systolic_pressure} / {self.diastolic_pressure}"

    def get_absolute_url(self):
        return reverse("bp_detail", args=[str(self.id)])


class HeartRate(models.Model):

    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="heart_rates",
    )
    # unit = count/minute
    creation_date = models.DateTimeField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    value = models.FloatField()

    class Meta:
        verbose_name = "Heart Rate"
        verbose_name_plural = "Heart Rates"
        ordering = ["-creation_date"]

    def __str__(self):
        return f"{self.author.first_name} - @{self.creation_date}: {self.value}"

    def get_absolute_url(self):
        return reverse("heart_rate_detail", args=[str(self.id)])


class AppleHealthUpload(models.Model):
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="apple_health_uploads",
    )
    when = models.DateTimeField(auto_now=True)
    health_data_xml = models.FileField(
        upload_to="apple_health_xml/",
    )
    csv_data_dir = models.CharField(max_length=500)
    is_processed = models.BooleanField(default=False)
    is_imported = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Apple Health Upload"
        verbose_name_plural = "Apple Health Uploads"
        ordering = ["-when"]

    def __str__(self):
        return f"{self.author}-{self.health_data_xml}"

    def get_absolute_url(self):
        return f"/health/apple-health/{self.id}"


class StepData(models.Model):
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="step_data",
    )
    # unit = count
    creation_date = models.DateTimeField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    value = models.FloatField()

    class Meta:
        verbose_name = "Step Data"
        verbose_name_plural = "Step Data"
        ordering = ["-creation_date"]

    def __str__(self):
        return f"{self.author.first_name} - @{self.creation_date}: {self.value} steps"

    def get_absolute_url(self):
        return reverse("step_data_detail", args=[str(self.id)])


class OxygenData(models.Model):
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="oxygen_data",
    )
    # unit = %
    creation_date = models.DateTimeField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    value = models.FloatField()
    objects = DataFrameManager()

    class Meta:
        verbose_name = "Oxygen Data"
        verbose_name_plural = "Oxygen Data"
        ordering = ["-creation_date"]

    def __str__(self):
        return f"{self.author.first_name} - @{self.creation_date}: {self.value}%"

    def get_absolute_url(self):
        return reverse("oxygen_data_detail", args=[str(self.id)])
