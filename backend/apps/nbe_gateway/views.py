import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import GatewayScenario, NbeSubmissionRecord, GatewayAuditLog
from .serializers import GatewayScenarioSerializer, NbeSubmissionRecordSerializer, GatewayAuditLogSerializer
from .gateway_service import NbeGatewayService

class GatewayHealthView(APIView):
    def get(self, request):
        scenario = GatewayScenario.get_current()
        is_healthy = scenario.mode not in ('SERVER_ERROR', 'TIMEOUT')
        status_text = 'DEGRADED' if scenario.mode in ('SERVER_ERROR', 'TIMEOUT', 'RANDOM_FLAKY') else 'ONLINE'

        return Response({
            'status': status_text,
            'healthy': is_healthy,
            'gateway': 'National Bank of Ethiopia (NBE) BSD Gateway',
            'endpoint': 'https://nbe.gov.et/api/v2/regulatory/gateway',
            'institutionCode': '0000013',
            'latencyMs': scenario.latency_ms,
            'tlsVersion': 'TLSv1.3 / mTLS',
            'directives': ['BSD/03/2020', 'SBR/2026'],
            'mode': scenario.mode,
            'timestamp': timezone.now().isoformat(),
        })

class GatewaySubmitView(APIView):
    def post(self, request):
        status_code, body = NbeGatewayService.process_payload(request.data, request.headers)
        return Response(body, status=status_code)

class GatewayScenarioView(APIView):
    def get(self, request):
        scenario = GatewayScenario.get_current()
        return Response(GatewayScenarioSerializer(scenario).data)

    def post(self, request):
        scenario = GatewayScenario.get_current()
        data = request.data
        if 'mode' in data:
            scenario.mode = data['mode']
        if 'latencyMs' in data:
            scenario.latency_ms = int(data['latencyMs'])
        if 'failureMessage' in data:
            scenario.failure_message = data['failureMessage']
        if 'flakyFailureRate' in data:
            scenario.flaky_failure_rate = float(data['flakyFailureRate'])
        scenario.save()
        return Response(GatewayScenarioSerializer(scenario).data)

class GatewaySubmissionsListView(APIView):
    def get(self, request):
        records = NbeSubmissionRecord.objects.all()[:100]
        return Response(NbeSubmissionRecordSerializer(records, many=True).data)

class GatewayLogsListView(APIView):
    def get(self, request):
        logs = GatewayAuditLog.objects.all()[:100]
        return Response(GatewayAuditLogSerializer(logs, many=True).data)

    def delete(self, request):
        GatewayAuditLog.objects.all().delete()
        return Response({'message': 'Logs cleared'})
