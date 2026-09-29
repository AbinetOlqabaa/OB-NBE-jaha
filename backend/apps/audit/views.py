from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import AuditLog
from .serializers import AuditLogSerializer
from .audit_logger import AuditLogger

class AuditLogListView(APIView):
    def get(self, request):
        limit = int(request.query_params.get('limit', 100))
        logs = AuditLog.objects.all()[:limit]
        serializer = AuditLogSerializer(logs, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        action = data.get('action')
        if not action:
            return Response({'error': 'Action is required for audit trail entry'}, status=status.HTTP_400_BAD_REQUEST)

        entry = AuditLogger.log(
            action=action,
            actor_id=data.get('actorId', 'sys_user'),
            actor_name=data.get('actorName', 'System User'),
            actor_role=data.get('actorRole', 'MAKER'),
            entity_type=data.get('entityType', 'REGULATORY'),
            entity_id=data.get('entityId', 'OB_SYSTEM'),
            correlation_id=data.get('correlationId', ''),
            details=data.get('details', f'Recorded action {action}'),
            old_state=data.get('oldState'),
            new_state=data.get('newState')
        )
        return Response(AuditLogSerializer(entry).data, status=status.HTTP_201_CREATED)

class BiometricAuditLogView(APIView):
    def post(self, request):
        data = request.data
        action = data.get('action', 'BIOMETRIC_EVENT')
        entry = AuditLogger.log(
            action=action,
            actor_id=data.get('actorId', 'bio_sensor'),
            actor_name=data.get('actorName', 'Biometric Sensor'),
            actor_role=data.get('actorRole', 'AUTH'),
            entity_type='BIOMETRICS',
            entity_id=data.get('entityId', 'BIO_AUTH'),
            correlation_id=data.get('correlationId', ''),
            details=data.get('details', 'Biometric hardware sensor event')
        )
        return Response(AuditLogSerializer(entry).data, status=status.HTTP_201_CREATED)

class AuditBatchSyncView(APIView):
    def post(self, request):
        logs = request.data.get('logs', [])
        if not isinstance(logs, list):
            return Response({'error': 'Expected logs array'}, status=status.HTTP_400_BAD_REQUEST)

        appended_count = 0
        for item in logs:
            if not isinstance(item, dict) or not item.get('id'):
                continue
            log_id = item.get('id')
            if not AuditLog.objects.filter(id=log_id).exists():
                AuditLog.objects.create(
                    id=log_id,
                    actor_id=item.get('actorId', 'field_user'),
                    actor_name=item.get('actorName', 'Field Examiner'),
                    actor_role=item.get('actorRole', 'MAKER'),
                    action=item.get('action', 'OFFLINE_EVENT'),
                    entity_type=item.get('entityType', 'REGULATORY'),
                    entity_id=item.get('entityId', 'FIELD_DEVICE'),
                    correlation_id=item.get('correlationId', ''),
                    details=item.get('details', 'Synced offline audit log'),
                    sync_status='SYNCED',
                    persisted_at=timezone.now()
                )
                appended_count += 1

        return Response({
            'success': True,
            'count': appended_count,
            'totalLogs': AuditLog.objects.count()
        })
