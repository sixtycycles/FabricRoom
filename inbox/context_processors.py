from django.db.utils import OperationalError, ProgrammingError

from inbox.models import MessageState


def unread_inbox_count(request):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {"unread_inbox_count": 0}

    try:
        count = MessageState.objects.filter(
            user=request.user,
            is_deleted=False,
            is_archived=False,
            is_read=False,
            message__sent_at__isnull=False,
            message__recipient=request.user,
        ).count()
    except (OperationalError, ProgrammingError):
        count = 0

    return {"unread_inbox_count": count}
