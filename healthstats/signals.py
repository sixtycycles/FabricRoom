from django.db.models.signals import post_delete
from django.dispatch import receiver
from healthstats.models import AppleHealthUpload
import os


@receiver(post_delete, sender=AppleHealthUpload)
def remove_apple_health_upload(sender, instance, **kwargs):

    if instance.health_data_xml:
        if os.path.isfile(instance.health_data_xml.path):
            os.remove(instance.health_data_xml.path)
