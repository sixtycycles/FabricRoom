from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from healthstats.models import (
    HealthEvent,
    Symptom,
    BloodPressure,
    HeartRate,
    StepData,
    OxygenData,
    AppleHealthUpload,
)
from datetime import datetime, timedelta


class SymptomModelTest(TestCase):
    """Test Symptom model"""

    def test_symptom_creation(self):
        """Test that Symptom is created successfully"""
        symptom = Symptom.objects.create(
            slug="fever", description="High body temperature"
        )
        self.assertEqual(symptom.slug, "fever")
        self.assertEqual(symptom.description, "High body temperature")

    def test_symptom_slug_is_unique(self):
        """Test that symptom slug must be unique"""
        Symptom.objects.create(slug="fever", description="High temperature")
        with self.assertRaises(Exception):
            Symptom.objects.create(slug="fever", description="Different description")

    def test_symptom_string_representation(self):
        """Test Symptom __str__ method"""
        symptom = Symptom.objects.create(slug="cough", description="Persistent cough")
        self.assertEqual(str(symptom), "cough")

    def test_symptom_get_absolute_url(self):
        """Test Symptom get_absolute_url method"""
        symptom = Symptom.objects.create(slug="headache", description="Head pain")
        expected_url = reverse("symptom_detail", args=[str(symptom.slug)])
        self.assertEqual(symptom.get_absolute_url(), expected_url)


class HealthEventModelTest(TestCase):
    """Test HealthEvent model"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.symptom = Symptom.objects.create(
            slug="fever", description="High temperature"
        )

    def test_health_event_creation(self):
        """Test that HealthEvent is created successfully"""
        event = HealthEvent.objects.create(
            author=self.user, temperature=99.5, note="Feeling better"
        )
        self.assertEqual(event.author, self.user)
        self.assertEqual(event.temperature, 99.5)
        self.assertEqual(event.note, "Feeling better")

    def test_health_event_temperature_optional(self):
        """Test that temperature is optional"""
        event = HealthEvent.objects.create(author=self.user, note="Just a note")
        self.assertIsNone(event.temperature)

    def test_health_event_note_optional(self):
        """Test that note is optional"""
        event = HealthEvent.objects.create(author=self.user, temperature=98.6)
        self.assertIsNone(event.note)

    def test_health_event_with_symptoms(self):
        """Test HealthEvent with symptoms"""
        event = HealthEvent.objects.create(author=self.user, temperature=100.0)
        event.symptoms.add(self.symptom)
        self.assertEqual(event.symptoms.count(), 1)
        self.assertIn(self.symptom, event.symptoms.all())

    def test_health_event_get_symptoms(self):
        """Test HealthEvent get_symptoms method"""
        event = HealthEvent.objects.create(author=self.user, temperature=99.0)
        event.symptoms.add(self.symptom)
        symptoms = event.get_symptoms()
        self.assertIn(self.symptom, symptoms)

    def test_health_event_string_representation(self):
        """Test HealthEvent __str__ method"""
        event = HealthEvent.objects.create(author=self.user, temperature=98.6)
        # The __str__ includes author first_name, so check for format
        result = str(event)
        self.assertIsNotNone(result)
        self.assertIn("@", result)  # Check for timestamp format

    def test_health_event_get_absolute_url(self):
        """Test HealthEvent get_absolute_url method"""
        event = HealthEvent.objects.create(author=self.user, temperature=98.6)
        expected_url = reverse("stat_detail", args=[str(event.id)])
        self.assertEqual(event.get_absolute_url(), expected_url)

    def test_health_event_detail_view_is_cached(self):
        event = HealthEvent.objects.create(author=self.user, temperature=98.6)
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("stat_detail", args=[str(event.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("max-age", response.get("Cache-Control", ""))

    def test_health_event_foreign_key_cascade_delete(self):
        """Test that deleting user deletes their events"""
        event = HealthEvent.objects.create(author=self.user, temperature=98.6)
        event_id = event.id
        self.user.delete()
        self.assertFalse(HealthEvent.objects.filter(id=event_id).exists())


class BloodPressureModelTest(TestCase):
    """Test BloodPressure model"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_blood_pressure_creation(self):
        """Test that BloodPressure is created successfully"""
        bp = BloodPressure.objects.create(
            author=self.user,
            systolic_pressure=120,
            diastolic_pressure=80,
            position="sitting",
        )
        self.assertEqual(bp.systolic_pressure, 120)
        self.assertEqual(bp.diastolic_pressure, 80)
        self.assertEqual(bp.position, "sitting")

    def test_blood_pressure_position_choices(self):
        """Test that position can be sitting, laying, or standing"""
        for position in ["sitting", "laying down", "standing"]:
            bp = BloodPressure.objects.create(
                author=self.user,
                systolic_pressure=120,
                diastolic_pressure=80,
                position=position,
            )
            self.assertEqual(bp.position, position)

    def test_blood_pressure_default_position_is_sitting(self):
        """Test that default position is sitting"""
        bp = BloodPressure.objects.create(
            author=self.user, systolic_pressure=120, diastolic_pressure=80
        )
        self.assertEqual(bp.position, "sitting")

    def test_blood_pressure_string_representation(self):
        """Test BloodPressure __str__ method"""
        bp = BloodPressure.objects.create(
            author=self.user, systolic_pressure=120, diastolic_pressure=80
        )
        self.assertEqual(str(bp), "120 / 80")

    def test_blood_pressure_get_absolute_url(self):
        """Test BloodPressure get_absolute_url method"""
        bp = BloodPressure.objects.create(
            author=self.user, systolic_pressure=120, diastolic_pressure=80
        )
        expected_url = reverse("bp_detail", args=[str(bp.id)])
        self.assertEqual(bp.get_absolute_url(), expected_url)


class HeartRateModelTest(TestCase):
    """Test HeartRate model"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.now = datetime.now()

    def test_heart_rate_creation(self):
        """Test that HeartRate is created successfully"""
        hr = HeartRate.objects.create(
            author=self.user,
            creation_date=self.now,
            start_date=self.now,
            end_date=self.now + timedelta(minutes=1),
            value=72.5,
        )
        self.assertEqual(hr.author, self.user)
        self.assertEqual(hr.value, 72.5)

    def test_heart_rate_string_representation(self):
        """Test HeartRate __str__ method"""
        hr = HeartRate.objects.create(
            author=self.user,
            creation_date=self.now,
            start_date=self.now,
            end_date=self.now + timedelta(minutes=1),
            value=75.0,
        )
        result = str(hr)
        self.assertIsNotNone(result)
        self.assertIn("75", result)  # Value should be in string


class OxygenDataModelTest(TestCase):
    """Test OxygenData model"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.now = datetime.now()

    def test_oxygen_data_creation(self):
        """Test that OxygenData is created successfully"""
        oxygen = OxygenData.objects.create(
            author=self.user,
            creation_date=self.now,
            start_date=self.now,
            end_date=self.now + timedelta(minutes=1),
            value=98.5,
        )
        self.assertEqual(oxygen.author, self.user)
        self.assertEqual(oxygen.value, 98.5)

    def test_oxygen_data_with_different_values(self):
        """Test oxygen values are stored correctly"""
        for value in [95.0, 98.0, 99.5, 100.0]:
            oxygen = OxygenData.objects.create(
                author=self.user,
                creation_date=self.now,
                start_date=self.now,
                end_date=self.now + timedelta(minutes=1),
                value=value,
            )
            self.assertEqual(oxygen.value, value)


class PlotViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="plotuser", email="plot@example.com", password="plotpass123"
        )
        self.client.login(username="plotuser", password="plotpass123")

    def test_temperature_plot_view_renders_chart(self):
        response = self.client.get(reverse("temp-plot"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Temperature")
        self.assertContains(response, "<svg")
        self.assertNotContains(response, "plotly")

    def test_heart_plot_view_renders_chart(self):
        response = self.client.get(reverse("heart-plot"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Heart Rate")


# class AppleHealthUploadModelTest(TestCase):
    # """Test AppleHealthUpload model"""

    # def setUp(self):
    #     self.user = get_user_model().objects.create_user(
    #         username="testuser", email="test@example.com", password="testpass123"
    #     )

    # def test_apple_health_upload_creation(self):
    #     """Test that AppleHealthUpload is created successfully"""
    #     upload = AppleHealthUpload.objects.create(
    #         author=self.user, health_data_xml="export.xml", csv_data_dir="/Users/rod/Documents/Rod/Misc Stuff/apple_health_export/"
    #     )
    #     self.assertEqual(upload.author, self.user)
    #     self.assertFalse(upload.is_processed)
    #     self.assertFalse(upload.is_imported)

    # def test_apple_health_upload_processed_flag(self):
    #     """Test that processed flag can be set"""
    #     upload = AppleHealthUpload.objects.create(
    #         author=self.user,
    #         health_data_xml="export.xml",
    #         csv_data_dir="/path",
    #         is_processed=True,
    #     )
    #     self.assertTrue(upload.is_processed)

    # def test_apple_health_upload_imported_flag(self):
    #     """Test that imported flag can be set"""
    #     upload = AppleHealthUpload.objects.create(
    #         author=self.user,
    #         health_data_xml="export.xml",
    #         csv_data_dir="/path",
    #         is_imported=True,
    #     )
    #     self.assertTrue(upload.is_imported)

    # def test_apple_health_upload_string_representation(self):
    #     """Test AppleHealthUpload __str__ method"""
    #     upload = AppleHealthUpload.objects.create(
    #         author=self.user, health_data_xml="export.xml", csv_data_dir="/path"
    #     )
    #     self.assertIn("testuser", str(upload))

    # def test_apple_health_upload_get_absolute_url(self):
    #     """Test AppleHealthUpload get_absolute_url method"""
    #     upload = AppleHealthUpload.objects.create(
    #         author=self.user, health_data_xml="export.xml", csv_data_dir="/path"
    #     )
    #     expected_url = f"/health/apple-health/{upload.id}"
    #     self.assertEqual(upload.get_absolute_url(), expected_url)
