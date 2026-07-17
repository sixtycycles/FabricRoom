"""Management command: cleanup_orphan_images

Finds and deletes two kinds of orphaned InlineImage records:

1. **Pending orphans** – images uploaded during a new-post session that was
   never submitted (``post`` is NULL), older than ``--hours``.

2. **Content orphans** – images that *are* linked to a post but whose URL no
   longer appears anywhere in that post's body (e.g. the user removed the
   image from the editor but the record was not cleaned up server-side).
   These are only included when ``--include-content-orphans`` is passed,
   because checking every linked image against its post body is more
   expensive and should only run periodically.

The ``post_delete`` signal on InlineImage automatically removes the file from
disk for every record deleted here.

Usage:
    # Dry-run: see what would be removed without deleting anything
    python manage.py cleanup_orphan_images --dry-run

    # Delete pending orphans older than 24 h (default)
    python manage.py cleanup_orphan_images

    # Also delete images that were removed from their post's body
    python manage.py cleanup_orphan_images --include-content-orphans

    # Adjust the age threshold
    python manage.py cleanup_orphan_images --hours 2
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from blog.models import InlineImage


class Command(BaseCommand):
    help = (
        "Delete orphaned InlineImage records (no post, or URL absent from post body) "
        "and their files from disk."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours",
            type=int,
            default=24,
            help="Delete pending images (no post) older than this many hours (default: 24).",
        )
        parser.add_argument(
            "--include-content-orphans",
            action="store_true",
            help=(
                "Also delete images that are linked to a post but whose URL "
                "no longer appears in the post body (i.e. the editor delete "
                "button was used but the server record was not cleaned up)."
            ),
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be deleted without actually deleting anything.",
        )

    def handle(self, *args, **options):
        hours = options["hours"]
        dry_run = options["dry_run"]
        include_content_orphans = options["include_content_orphans"]

        to_delete = []

        # ── 1. Pending orphans (uploaded for a new post that was never saved) ──
        cutoff = timezone.now() - timedelta(hours=hours)
        pending_orphans = list(
            InlineImage.objects.filter(post__isnull=True, created_at__lt=cutoff)
        )
        if pending_orphans:
            self.stdout.write(
                f"Found {len(pending_orphans)} pending orphan(s) older than {hours} hour(s)."
            )
        to_delete.extend(pending_orphans)

        # ── 2. Content orphans (image linked to post but not in body) ──────────
        if include_content_orphans:
            linked_images = InlineImage.objects.filter(post__isnull=False).select_related("post")
            content_orphans = [
                img for img in linked_images
                if img.image and img.image.url not in img.post.body
            ]
            if content_orphans:
                self.stdout.write(
                    f"Found {len(content_orphans)} content orphan(s) "
                    "(linked to a post but URL absent from body)."
                )
            to_delete.extend(content_orphans)

        if not to_delete:
            self.stdout.write("No orphaned images to clean up.")
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"[dry-run] Would delete {len(to_delete)} image(s):")
            )
            for img in to_delete:
                self.stdout.write(
                    f"  • {img.image.name}  "
                    f"(post: {img.post_id or 'none'}, "
                    f"session: {img.session_key}, "
                    f"created: {img.created_at})"
                )
            return

        deleted = 0
        for img in to_delete:
            self.stdout.write(f"  Deleting {img.image.name} …")
            img.delete()  # triggers post_delete signal → file removed from disk
            deleted += 1

        self.stdout.write(
            self.style.SUCCESS(f"Cleaned up {deleted} orphaned inline image(s).")
        )
