import csv
from datetime import datetime
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from blog.models import Gratitude
from main.command_run_logging import (
    record_management_command_failure,
    record_management_command_run,
)
from main.models import ManagementCommandRun

User = get_user_model()


class Command(BaseCommand):
    help = "Ingest gratitude entries from a CSV file into the Gratitude model."

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            nargs="?",
            default="/Users/rod/Downloads/marisa_gratitude_entries.csv",
            help="Path to the CSV file to import. Defaults to /Users/rod/Downloads/marisa_gratitude_entries.csv",
        )
        parser.add_argument(
            "--author",
            default="roconnor",
            help="Username of the Gratitude author. Default is 'roconnor'.",
        )
        parser.add_argument(
            "--target",
            default="marisa",
            help="Username of the Gratitude target user. Default is 'marisa'.",
        )
        parser.add_argument(
            "--default-time",
            default="09:00",
            help="Default time (HH:MM) to assign to created dates. Default is '09:00'.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and preview rows without saving them to the database.",
        )

    def handle(self, *args, **options):
        started_at = timezone.now()
        csv_path = Path(options["csv_file"])
        author_username = options["author"]
        target_username = options["target"]
        default_time_str = options["default_time"]
        dry_run = options["dry_run"]

        try:
            if not csv_path.exists():
                raise CommandError(f"CSV file not found: {csv_path}")

            try:
                author = User.objects.get(username=author_username)
            except User.DoesNotExist:
                raise CommandError(f"Author user with username '{author_username}' not found.")

            target_user = None
            if target_username:
                try:
                    target_user = User.objects.get(username=target_username)
                except User.DoesNotExist:
                    raise CommandError(f"Target user with username '{target_username}' not found.")

            try:
                default_time = datetime.strptime(default_time_str, "%H:%M").time()
            except ValueError:
                raise CommandError(f"Invalid default-time format '{default_time_str}'. Expected HH:MM.")

            created_count = 0
            with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for row_idx, row in enumerate(reader, start=2):
                    date_str = (row.get("date_of_creation") or "").strip()
                    text = (row.get("quote_text") or "").strip()

                    if not text:
                        self.stdout.write(
                            self.style.WARNING(f"Row {row_idx}: Empty quote_text, skipping.")
                        )
                        continue
                    if not date_str:
                        self.stdout.write(
                            self.style.WARNING(f"Row {row_idx}: Empty date_of_creation, skipping.")
                        )
                        continue

                    # Parse date in M/D/YY or M/D/YYYY format
                    parsed_date = None
                    for fmt in ("%m/%d/%y", "%m/%d/%Y", "%Y-%m-%d"):
                        try:
                            parsed_date = datetime.strptime(date_str, fmt).date()
                            break
                        except ValueError:
                            continue

                    if not parsed_date:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Row {row_idx}: Could not parse date '{date_str}', skipping."
                            )
                        )
                        continue

                    naive_dt = datetime.combine(parsed_date, default_time)
                    aware_dt = timezone.make_aware(naive_dt, timezone.get_current_timezone())

                    if dry_run:
                        self.stdout.write(
                            f"[DRY RUN] Row {row_idx}: {aware_dt} | {text[:50]}..."
                        )
                        created_count += 1
                    else:
                        gratitude = Gratitude.objects.create(
                            author=author,
                            gratitude_text=text,
                            created_date=aware_dt,
                        )
                        if target_user:
                            gratitude.target.add(target_user)
                        created_count += 1

            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(f"Dry run complete. {created_count} entries verified.")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully ingested {created_count} gratitude entries.")
                )

            record_management_command_run(
                command_name="ingest_marisa_gratitudes",
                status=ManagementCommandRun.STATUS_SUCCESS,
                started_at=started_at,
                summary=(
                    f"{created_count} gratitude entries processed "
                    f"(dry_run={dry_run}, source={csv_path})."
                ),
            )
        except Exception as error:
            record_management_command_failure(
                command_name="ingest_marisa_gratitudes",
                started_at=started_at,
                error=error,
            )
            raise
