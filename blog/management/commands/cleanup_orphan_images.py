"""Management command: cleanup_orphan_images

Finds and deletes two kinds of orphaned InlineImage records, both by default:

1. **Pending orphans** – images uploaded during a new-post session that was
   never submitted (``post`` is NULL).  A ``--grace-hours`` threshold (default
   1 h) prevents deleting images that were *just* uploaded and are still part
   of an in-progress new-post form.

2. **Content orphans** – images that *are* linked to a post but whose URL no
   longer appears anywhere in that post's body (e.g. the user removed the
   image from the editor but the record was not cleaned up server-side).

The ``post_delete`` signal on InlineImage automatically removes the file from
disk for every record deleted here.

Usage:
    # Dry-run: see what would be removed without deleting anything
    python manage.py cleanup_orphan_images --dry-run

    # Delete both kinds of orphan (default grace period = 1 h for pending)
    python manage.py cleanup_orphan_images

    # Use a longer grace period for pending images (e.g. during slow sessions)
    python manage.py cleanup_orphan_images --grace-hours 4

    # Skip the content-orphan check (faster; only removes post-less images)
    python manage.py cleanup_orphan_images --skip-content-check
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from blog.models import InlineImage
from main.command_run_logging import (
    record_management_command_failure,
    record_management_command_run,
)
from main.models import ManagementCommandRun


class Command(BaseCommand):
    help = (
        "Delete orphaned InlineImage records (no post, or URL absent from post body) "
        "and their files from disk."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--grace-hours",
            type=int,
            default=1,
            help=(
                "Grace period (hours) before a pending image (no post) is "
                "considered an orphan.  Prevents deleting images that were "
                "just uploaded as part of an in-progress new-post form. "
                "Default: 1."
            ),
        )
        parser.add_argument(
            "--skip-content-check",
            action="store_true",
            help=(
                "Skip the content-orphan check (images linked to a post but "
                "absent from its body).  Useful for quick runs."
            ),
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be deleted without actually deleting anything.",
        )

    def handle(self, *args, **options):
        started_at = timezone.now()
        grace_hours = options["grace_hours"]
        skip_content_check = options["skip_content_check"]
        dry_run = options["dry_run"]

        try:
            to_delete = []

            # ── 1. Pending orphans (no post, outside the grace window) ───────────
            cutoff = timezone.now() - timedelta(hours=grace_hours)
            pending_orphans = list(
                InlineImage.objects.filter(post__isnull=True, created_at__lt=cutoff)
            )
            pending_count = len(pending_orphans)
            self.stdout.write(
                f"Pending orphans (no post, older than {grace_hours}h): "
                f"{pending_count} found."
            )
            to_delete.extend(pending_orphans)

            # ── 2. Content orphans (linked to post, URL absent from body) ────────
            content_count = 0
            if not skip_content_check:
                linked_images = InlineImage.objects.filter(
                    post__isnull=False
                ).select_related("post")
                content_orphans = [
                    img for img in linked_images
                    if img.image and img.image.url not in img.post.body
                ]
                content_count = len(content_orphans)
                self.stdout.write(
                    f"Content orphans (linked to post, absent from body): "
                    f"{content_count} found."
                )
                to_delete.extend(content_orphans)

            if not to_delete:
                self.stdout.write(self.style.SUCCESS("Nothing to clean up."))
                record_management_command_run(
                    command_name="cleanup_orphan_images",
                    status=ManagementCommandRun.STATUS_SUCCESS,
                    started_at=started_at,
                    summary=(
                        "No orphaned inline images found "
                        f"(pending={pending_count}, content={content_count}, "
                        f"grace_hours={grace_hours}, skip_content_check={skip_content_check})."
                    ),
                )
                return

            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f"\n[dry-run] Would delete {len(to_delete)} image(s):"
                    )
                )
                for img in to_delete:
                    self.stdout.write(
                        f"  • {img.image.name}  "
                        f"(post: {img.post_id or 'none'}, "
                        f"session: {img.session_key or '-'}, "
                        f"created: {img.created_at})"
                    )
                record_management_command_run(
                    command_name="cleanup_orphan_images",
                    status=ManagementCommandRun.STATUS_SUCCESS,
                    started_at=started_at,
                    summary=(
                        f"Dry run: {len(to_delete)} orphaned inline images would be deleted "
                        f"(pending={pending_count}, content={content_count}, "
                        f"grace_hours={grace_hours}, skip_content_check={skip_content_check})."
                    ),
                )
                return

            deleted = 0
            for img in to_delete:
                self.stdout.write(f"  Deleting {img.image.name} …")
                img.delete()  # post_delete signal removes file from disk
                deleted += 1

            self.stdout.write(
                self.style.SUCCESS(f"\nCleaned up {deleted} orphaned inline image(s).")
            )
            record_management_command_run(
                command_name="cleanup_orphan_images",
                status=ManagementCommandRun.STATUS_SUCCESS,
                started_at=started_at,
                summary=(
                    f"Deleted {deleted} orphaned inline images "
                    f"(pending={pending_count}, content={content_count}, "
                    f"grace_hours={grace_hours}, skip_content_check={skip_content_check})."
                ),
            )
        except Exception as error:
            record_management_command_failure(
                command_name="cleanup_orphan_images",
                started_at=started_at,
                error=error,
            )
            raise
