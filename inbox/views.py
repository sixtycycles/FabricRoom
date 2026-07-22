from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, View

from inbox.forms import MessageComposeForm
from inbox.models import Message, MessageState


def _message_for_user_or_404(user, message_id):
    return get_object_or_404(
        Message.objects.filter(states__user=user, states__is_deleted=False).distinct(),
        pk=message_id,
    )


def _sender_state_defaults(now):
    return {
        "is_read": True,
        "read_at": now,
        "is_archived": False,
        "is_deleted": False,
    }


def _recipient_state_defaults(now, is_self_message):
    if is_self_message:
        return {
            "is_read": True,
            "read_at": now,
            "is_archived": False,
            "is_deleted": False,
        }
    return {
        "is_read": False,
        "read_at": None,
        "is_archived": False,
        "is_deleted": False,
    }


def _reply_recipient_for_message(message, replying_user):
    if message.sender_id == replying_user.id:
        return message.recipient
    return message.sender


def _persist_message(request, form, action, parent=None, draft=None, recipient_override=None):
    now = timezone.now()
    message = draft or form.save(commit=False)
    message.sender = request.user
    message.recipient = recipient_override or form.cleaned_data.get("recipient")
    message.subject = form.cleaned_data.get("subject", "")
    message.body = form.cleaned_data.get("body", "")

    if parent is not None:
        message.parent = parent
        message.root = parent.root or parent

    if action == "send":
        message.sent_at = now
    else:
        message.sent_at = None

    message.save()

    if message.sent_at is not None and message.root_id is None:
        message.root = message
        message.save(update_fields=["root"])

    MessageState.objects.update_or_create(
        message=message,
        user=request.user,
        defaults=_sender_state_defaults(now),
    )

    if message.sent_at is not None and message.recipient is not None:
        MessageState.objects.update_or_create(
            message=message,
            user=message.recipient,
            defaults=_recipient_state_defaults(now, message.recipient_id == request.user.id),
        )

    return message


class InboxListView(LoginRequiredMixin, TemplateView):
    template_name = "inbox/inbox_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mailbox"] = "inbox"
        context["title"] = "Inbox"
        context["states"] = (
            MessageState.objects.filter(
                user=self.request.user,
                is_deleted=False,
                is_archived=False,
                message__sent_at__isnull=False,
                message__recipient=self.request.user,
            )
            .select_related("message", "message__sender", "message__recipient")
            .order_by("-message__sent_at", "-message__created_at")
        )
        return context


class DraftListView(LoginRequiredMixin, TemplateView):
    template_name = "inbox/inbox_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mailbox"] = "drafts"
        context["title"] = "Drafts"
        context["states"] = (
            MessageState.objects.filter(
                user=self.request.user,
                is_deleted=False,
                message__sent_at__isnull=True,
                message__sender=self.request.user,
            )
            .select_related("message", "message__sender", "message__recipient")
            .order_by("-message__updated_at", "-message__created_at")
        )
        return context


class ArchiveListView(LoginRequiredMixin, TemplateView):
    template_name = "inbox/inbox_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mailbox"] = "archive"
        context["title"] = "Archive"
        context["states"] = (
            MessageState.objects.filter(
                user=self.request.user,
                is_deleted=False,
                is_archived=True,
                message__sent_at__isnull=False,
            )
            .select_related("message", "message__sender", "message__recipient")
            .order_by("-message__sent_at", "-message__created_at")
        )
        return context


class SentListView(LoginRequiredMixin, TemplateView):
    template_name = "inbox/inbox_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mailbox"] = "sent"
        context["title"] = "Sent"
        context["states"] = (
            MessageState.objects.filter(
                user=self.request.user,
                is_deleted=False,
                is_archived=False,
                message__sent_at__isnull=False,
                message__sender=self.request.user,
            )
            .select_related("message", "message__sender", "message__recipient")
            .order_by("-message__sent_at", "-message__created_at")
        )
        return context


class ComposeMessageView(LoginRequiredMixin, View):
    template_name = "inbox/compose.html"

    def get(self, request):
        form = MessageComposeForm(user=request.user)
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "page_title": "Compose Message",
            },
        )

    def post(self, request):
        form = MessageComposeForm(request.POST, user=request.user)
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "page_title": "Compose Message",
                },
            )

        action = "send" if "send" in request.POST else "draft"
        if action == "send" and not form.validate_for_send():
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "page_title": "Compose Message",
                },
            )

        message = _persist_message(request, form, action=action)
        if action == "send":
            messages.success(request, "Message sent.")
            return redirect("inbox_thread", message_id=message.id)
        messages.success(request, "Draft saved.")
        return redirect("inbox_drafts")


class DraftEditView(LoginRequiredMixin, View):
    template_name = "inbox/compose.html"

    def _draft_or_404(self, request, message_id):
        draft = get_object_or_404(
            Message,
            pk=message_id,
            sender=request.user,
            sent_at__isnull=True,
        )
        if not MessageState.objects.filter(
            message=draft, user=request.user, is_deleted=False
        ).exists():
            return None
        return draft

    def get(self, request, message_id):
        draft = self._draft_or_404(request, message_id)
        if draft is None:
            return HttpResponseForbidden("Draft not available.")

        form = MessageComposeForm(instance=draft, user=request.user)
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "page_title": "Edit Draft",
                "draft": draft,
            },
        )

    def post(self, request, message_id):
        draft = self._draft_or_404(request, message_id)
        if draft is None:
            return HttpResponseForbidden("Draft not available.")

        form = MessageComposeForm(request.POST, instance=draft, user=request.user)
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "page_title": "Edit Draft",
                    "draft": draft,
                },
            )

        action = "send" if "send" in request.POST else "draft"
        if action == "send" and not form.validate_for_send():
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "page_title": "Edit Draft",
                    "draft": draft,
                },
            )

        message = _persist_message(request, form, action=action, draft=draft)
        if action == "send":
            messages.success(request, "Draft sent.")
            return redirect("inbox_thread", message_id=message.id)
        messages.success(request, "Draft updated.")
        return redirect("inbox_drafts")


class ReplyMessageView(LoginRequiredMixin, View):
    template_name = "inbox/compose.html"

    def get(self, request, message_id):
        target = _message_for_user_or_404(request.user, message_id)
        recipient = _reply_recipient_for_message(target, request.user)
        initial_subject = target.subject or ""
        if initial_subject and not initial_subject.lower().startswith("re:"):
            initial_subject = f"Re: {initial_subject}"
        form = MessageComposeForm(
            user=request.user,
            initial={
                "recipient": recipient,
                "subject": initial_subject,
            },
        )
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "page_title": "Reply",
                "reply_to": target,
            },
        )

    def post(self, request, message_id):
        target = _message_for_user_or_404(request.user, message_id)
        recipient = _reply_recipient_for_message(target, request.user)
        form = MessageComposeForm(request.POST, user=request.user)
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "page_title": "Reply",
                    "reply_to": target,
                },
            )

        action = "send" if "send" in request.POST else "draft"
        if action == "send" and not form.validate_for_send():
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "page_title": "Reply",
                    "reply_to": target,
                },
            )

        if action == "send" and recipient is None:
            form.add_error(None, "This message cannot be replied to because it has no recipient.")
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "page_title": "Reply",
                    "reply_to": target,
                },
            )

        message = _persist_message(
            request,
            form,
            action=action,
            parent=target,
            recipient_override=recipient,
        )
        if action == "send":
            messages.success(request, "Reply sent.")
            return redirect("inbox_thread", message_id=message.id)
        messages.success(request, "Reply draft saved.")
        return redirect("inbox_drafts")


class ThreadDetailView(LoginRequiredMixin, TemplateView):
    template_name = "inbox/thread_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        message = _message_for_user_or_404(self.request.user, kwargs["message_id"])
        root = message.root or message
        thread_messages = list(
            Message.objects.filter(Q(id=root.id) | Q(root=root), sent_at__isnull=False)
            .filter(Q(sender=self.request.user) | Q(recipient=self.request.user))
            .select_related("sender", "recipient", "parent", "root")
            .order_by("sent_at", "created_at")
        )

        states = {
            state.message_id: state
            for state in MessageState.objects.filter(
                user=self.request.user,
                message_id__in=[m.id for m in thread_messages],
                is_deleted=False,
            )
        }
        for thread_message in thread_messages:
            if thread_message.recipient_id == self.request.user.id:
                state = states.get(thread_message.id)
                if state is not None and not state.is_read:
                    state.is_read = True
                    state.read_at = timezone.now()
                    state.save(update_fields=["is_read", "read_at"])
                    states[thread_message.id] = state

        context["current_message"] = message
        context["thread_root"] = root
        context["thread_entries"] = [
            {
                "message": thread_message,
                "state": states.get(thread_message.id),
            }
            for thread_message in thread_messages
        ]
        return context


@require_POST
def mark_read(request, message_id):
    message = _message_for_user_or_404(request.user, message_id)
    state = get_object_or_404(MessageState, message=message, user=request.user, is_deleted=False)
    if not state.is_read:
        state.is_read = True
        state.read_at = timezone.now()
        state.save(update_fields=["is_read", "read_at"])
    return redirect(request.POST.get("next") or "inbox_list")


@require_POST
def toggle_archive(request, message_id):
    message = _message_for_user_or_404(request.user, message_id)
    state = get_object_or_404(MessageState, message=message, user=request.user, is_deleted=False)
    state.is_archived = not state.is_archived
    state.save(update_fields=["is_archived"])
    return redirect(request.POST.get("next") or "inbox_list")


@require_POST
def delete_message(request, message_id):
    message = _message_for_user_or_404(request.user, message_id)
    state = get_object_or_404(MessageState, message=message, user=request.user, is_deleted=False)
    state.is_deleted = True
    state.save(update_fields=["is_deleted"])
    return redirect(request.POST.get("next") or "inbox_list")
