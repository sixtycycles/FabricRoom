from django.conf import settings
from django.db import models
from django.urls import reverse


class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages_sent",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages_received",
        blank=True,
        null=True,
    )
    subject = models.CharField(max_length=200, blank=True)
    body = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="replies",
        blank=True,
        null=True,
    )
    root = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="thread_messages",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        subject = self.subject.strip() or "(no subject)"
        if self.sent_at is None:
            return f"Draft: {subject}"
        return f"{subject} ({self.sender} -> {self.recipient})"

    @property
    def is_draft(self):
        return self.sent_at is None

    def get_absolute_url(self):
        return reverse("inbox_thread", args=[self.id])


class MessageState(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="states",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="message_states",
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    is_archived = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-message__sent_at", "-message__created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["message", "user"],
                name="unique_message_state_per_user",
            )
        ]

    def __str__(self):
        return f"State<{self.user} on #{self.message_id}>"
