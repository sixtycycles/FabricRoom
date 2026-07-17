import os

from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import InlineImage


@receiver(post_delete, sender=InlineImage)
def delete_inline_image_file(sender, instance, **kwargs):
    """Delete the image file from disk when an InlineImage record is deleted.

    This fires for both explicit deletes and cascade deletes triggered when the
    related Post is deleted, ensuring no orphaned files are left on disk.
    """
    if instance.image:
        image_path = instance.image.path
        if os.path.isfile(image_path):
            os.remove(image_path)
