from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    actorId = serializers.CharField(source='actor_id')
    actorName = serializers.CharField(source='actor_name')
    actorRole = serializers.CharField(source='actor_role')
    entityType = serializers.CharField(source='entity_type')
    entityId = serializers.CharField(source='entity_id')
    correlationId = serializers.CharField(source='correlation_id', required=False, allow_blank=True)
    oldState = serializers.JSONField(source='old_state', required=False, allow_null=True)
    newState = serializers.JSONField(source='new_state', required=False, allow_null=True)
    syncStatus = serializers.CharField(source='sync_status', required=False)
    persistedAt = serializers.DateTimeField(source='persisted_at', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'timestamp',
            'actorId',
            'actorName',
            'actorRole',
            'action',
            'entityType',
            'entityId',
            'correlationId',
            'details',
            'oldState',
            'newState',
            'syncStatus',
            'persistedAt',
        ]
