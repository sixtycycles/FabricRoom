import argparse
import csv
import os
from pathlib import Path
from typing import TextIO, Union

from django.core.management.base import BaseCommand, CommandError

from blog.models import Quote


class Command(BaseCommand):
    help = "Import quotes from a CSV file into the Quote model"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "csv_path",
            nargs="?",
            help="Path to a CSV file. If omitted, the default attachment file is used.",
        )
        parser.add_argument(
            "--csv",
            dest="csv_flag",
            help="Path to a CSV file. Useful when you want to pass the file explicitly as an option.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview rows without saving them to the database.",
        )

    def handle(self, *args, **options) -> None:
        csv_source = options.get("csv_flag") or options.get("csv_path")
        dry_run = options.get("dry_run", False)

        handle = self._open_csv_source(csv_source)

        try:
            imported_count = self._import_from_handle(handle, dry_run=dry_run)
        finally:
            if hasattr(handle, "close"):
                handle.close()

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"Dry run complete. {imported_count} rows would be imported."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Imported {imported_count} quotes."))

    def _open_csv_source(self, csv_source: Union[str, os.PathLike, TextIO, None]) -> TextIO:
        if csv_source is None:
            default_path = Path("*.csv")
            if not default_path.exists():
                raise CommandError(
                    "No CSV path provided and default file was not found: *.csv"
                )
            return default_path.open(newline="", encoding="utf-8")

        if hasattr(csv_source, "read"):
            return csv_source

        path = Path(csv_source)
        if not path.exists():
            raise CommandError(f"CSV file not found: {path}")
        return path.open(newline="", encoding="utf-8")

    def _import_from_handle(self, handle: TextIO, *, dry_run: bool = False) -> int:
        reader = csv.DictReader(handle)
        imported = 0

        for row in reader:
            text = (row.get("Quote") or "").strip()
            author = (row.get("Author/Character") or "").strip()
            if not text:
                continue
            if dry_run:
                imported += 1
                continue
            Quote.objects.update_or_create(text=text, defaults={"author": author})
            imported += 1

        return imported
