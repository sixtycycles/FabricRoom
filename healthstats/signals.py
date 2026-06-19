from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from healthstats.models import AppleHealthUpload
import os
import logging
import threading

from healthstats.apple_health_importer import AppleHealthXMLImporter

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=AppleHealthUpload)
def remove_apple_health_upload(sender, instance, **kwargs):

    if instance.health_data_xml:
        if os.path.isfile(instance.health_data_xml.path):
            os.remove(instance.health_data_xml.path)


@receiver(post_save, sender=AppleHealthUpload)
def process_apple_health_upload(sender, instance, created, **kwargs):
    """
    Signal handler that triggers automatic background processing when an
    AppleHealthUpload is created.
    """
    # Only process new uploads (not updates)
    if not created:
        return

    # Start processing in background thread (non-blocking)
    thread = threading.Thread(
        target=_process_health_data_background,
        args=(instance.id,),
        daemon=True
    )
    thread.start()
    logger.info(f"Started background processing thread for AppleHealthUpload {instance.id}")


def _process_health_data_background(upload_id):
    """
    Background thread function that processes Apple Health XML data.
    Runs in separate thread to avoid blocking HTTP request.
    """
    try:
        # Fetch fresh instance from DB (in case it changed)
        upload = AppleHealthUpload.objects.get(id=upload_id)

        # Update status to processing
        upload.processing_status = 'processing'
        upload.save(update_fields=['processing_status'])
        logger.info(f"Starting import process for AppleHealthUpload {upload_id}")

        # Get actual file path
        xml_file_path = upload.health_data_xml.path

        # Run the importer
        importer = AppleHealthXMLImporter(xml_file_path, upload.author)
        records_imported = importer.import_records()

        # Update status and record count on success
        upload.processing_status = 'complete'
        upload.records_imported = records_imported
        upload.processing_error = None
        upload.save(
            update_fields=['processing_status', 'records_imported', 'processing_error']
        )
        logger.info(
            f"Successfully imported {records_imported} records for AppleHealthUpload {upload_id}"
        )

    except Exception as e:
        # Log error and update status
        error_message = str(e)
        logger.error(f"Error processing AppleHealthUpload {upload_id}: {error_message}", exc_info=True)

        try:
            upload = AppleHealthUpload.objects.get(id=upload_id)
            upload.processing_status = 'error'
            upload.processing_error = error_message
            upload.save(
                update_fields=['processing_status', 'processing_error']
            )
        except AppleHealthUpload.DoesNotExist:
            logger.error(f"AppleHealthUpload {upload_id} not found when handling error")
