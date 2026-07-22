import traceback

from django.utils import timezone

from main.models import ManagementCommandRun


def record_management_command_run(
    *,
    command_name,
    status,
    started_at,
    summary="",
    details="",
):
    finished_at = timezone.now()
    duration_seconds = max((finished_at - started_at).total_seconds(), 0.0)
    return ManagementCommandRun.objects.create(
        command_name=command_name,
        status=status,
        summary=summary,
        details=details,
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=duration_seconds,
    )


def record_management_command_failure(*, command_name, started_at, error):
    return record_management_command_run(
        command_name=command_name,
        status=ManagementCommandRun.STATUS_FAILED,
        started_at=started_at,
        summary=str(error),
        details=traceback.format_exc(),
    )
