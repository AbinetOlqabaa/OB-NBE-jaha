from django.db import models
from django.utils import timezone
import uuid

class AuditLog(models.Model):
    """
    Immutable compliance audit trail required by NBE Directive BSD/03/2020.
    Captures all security, authentication, workflow transitions, and regulatory submissions.
    """
    id = models.CharField(max_length=64, primary_key=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    actor_id = models.CharField(max_length=64)
    actor_name = models.CharField(max_length=255)
    actor_role = models.CharField(max_length=32)
    action = models.CharField(max_length=64, db_index=True)
    entity_type = models.CharField(max_length=64)
    entity_id = models.CharField(max_length=64)
    correlation_id = models.CharField(max_length=128, blank=True)
    details = models.TextField()
    old_state = models.JSONField(null=True, blank=True)
    new_state = models.JSONField(null=True, blank=True)
    sync_status = models.CharField(max_length=32, default='SYNCED')
    persisted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Compliance Audit Log'
        verbose_name_plural = 'Compliance Audit Logs'

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.action} by {self.actor_name} ({self.actor_role})"
