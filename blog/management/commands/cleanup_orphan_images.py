"""Management command: cleanup_orphan_images

Deletes InlineImage records that have no associated Post (i.e. were uploaded
during a new-post session that was never submitted) and are older than a
configurable age threshold.  The post_delete signal on InlineImage
automatically removes the file from disk for each deleted record.

Usage:
    python manage.py cleanup_orphan_images            # default: older than 24 h
    python manage.py cleanup_orphan_images --hours 2  # older than 2 h
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from blog.models import InlineImage


class Command(BaseCommand):
    help = "Delete orphaned InlineImage records (no post, older than --hours) and their files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours",
            type=int,
            default=24,
            help="Delete images older than this many hours (default: 24).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be deleted without actually deleting anything.",
        )

    def handle(self, *args, **options):
        hours = options["hours"]
        dry_run = options["dry_run"]
        cutoff = timezone.now() - timedelta(hours=hours)

        orphans = InlineImage.objects.filter(post__isnull=True, created_at__lt=cutoff)
        count = orphans.count()

        if count == 0:
            self.stdout.write("No orphaned images to clean up.")
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"[dry-run] Would delete {count} orphaned image(s) older than {hours} hour(s):"
                )
            )
            for img in orphans:
                self.stdout.write(f"  • {img.image.name}  (session: {img.session_key}, created: {img.created_at})")
            return

        # Deleting each record individually so the post_delete signal fires
        # for each one, triggering file removal from disk.
        deleted = 0
        for img in orphans:
            self.stdout.write(f"  Deleting {img.image.name} …")
            img.delete()
            deleted += 1

        self.stdout.write(
            self.style.SUCCESS(f"Cleaned up {deleted} orphaned inline image(s).")
        )
