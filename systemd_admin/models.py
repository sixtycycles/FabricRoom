from django.db import models

class SystemdAccess(models.Model):
    class Meta:
        managed = False  # No database table created
        permissions = [
            ("can_view_systemd", "Can view host systemd status"),
            ("can_manage_systemd", "Can start/stop/restart host systemd services"),
        ]