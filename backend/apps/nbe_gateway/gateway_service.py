import uuid
import random
import time
from django.utils import timezone
from .models import GatewayScenario, NbeSubmissionRecord, GatewayAuditLog

class NbeGatewayService:
    @classmethod
    def process_payload(cls, payload: dict, headers: dict) -> tuple[int, dict]:
        scenario = GatewayScenario.get_current()

        idempotency_key = headers.get('Idempotency-Key') or headers.get('idempotency-key') or ''
        correlation_id = headers.get('X-Correlation-ID') or headers.get('x-correlation-id') or f"corr_nbe_{int(time.time()*1000)}"

        # Idempotency deduplication check
        if idempotency_key:
            existing = NbeSubmissionRecord.objects.filter(idempotency_key=idempotency_key).first()
            if existing:
                cls._log_gateway('INBOUND', 200, correlation_id, idempotency_key, f"[Idempotent Replay] Returned cached receipt {existing.submission_id}")
                return 200, existing.response_payload

        # Evaluate scenario mode
        mode = scenario.mode
        if mode == 'RANDOM_FLAKY':
            if random.random() < scenario.flaky_failure_rate:
                mode = 'SERVER_ERROR'
            else:
                mode = 'SUCCESS'

        report_key = payload.get('ReturnKey') or payload.get('reportKey') or 'UNKNOWN_RETURN'
        inst_code = payload.get('InstCode') or '0000013'

        if mode == 'AUTH_FAILURE':
            err_body = {
                'success': False,
                'statusCode': 401,
                'error': 'NBE BSD Portal: Mutual TLS / Certificate signature invalid or expired.',
                'correlationId': correlation_id
            }
            cls._log_gateway('INBOUND', 401, correlation_id, idempotency_key, "mTLS Authentication Failure at NBE BSD Gateway")
            return 401, err_body

        if mode == 'TIMEOUT':
            err_body = {
                'success': False,
                'statusCode': 504,
                'error': 'Gateway Timeout: NBE regulatory intake cluster took longer than 30000ms to acknowledge receipt.',
                'correlationId': correlation_id
            }
            cls._log_gateway('INBOUND', 504, correlation_id, idempotency_key, "Gateway timeout waiting for NBE ledger")
            return 504, err_body

        if mode == 'SERVER_ERROR':
            err_body = {
                'success': False,
                'statusCode': 500,
                'error': 'NBE BSD Core Gateway 500: Database lock deadlock on statutory return intake pipeline.',
                'correlationId': correlation_id
            }
            cls._log_gateway('INBOUND', 500, correlation_id, idempotency_key, "Internal Server Error in NBE intake pipeline")
            return 500, err_body

        if mode == 'VALIDATION_ERROR':
            err_body = {
                'success': False,
                'statusCode': 422,
                'error': 'NBE Validation Failure: Cross-return consistency check failed between BSD_LOAN and M_LCPLC001.',
                'correlationId': correlation_id
            }
            cls._log_gateway('INBOUND', 422, correlation_id, idempotency_key, "NBE Schema / Cross-return Validation Error (422)")
            return 422, err_body

        # SUCCESS path:
        receipt_id = f"NBE-BSD-{int(time.time())}-{random.randint(1000, 9999)}"
        response_body = {
            'success': True,
            'statusCode': 200,
            'submissionId': receipt_id,
            'correlationId': correlation_id,
            'message': f"Statutory return {report_key} officially received and verified by National Bank of Ethiopia BSD Gateway.",
            'timestamp': timezone.now().isoformat(),
            'institutionCode': inst_code,
            'directivesVerified': ['BSD/03/2020', 'SBR/2026'],
        }

        NbeSubmissionRecord.objects.create(
            submission_id=receipt_id,
            report_key=report_key,
            institution_code=inst_code,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
            status='ACCEPTED',
            payload=payload,
            response_payload=response_body
        )

        cls._log_gateway('INBOUND', 200, correlation_id, idempotency_key, f"Verified and accepted statutory return {report_key}. Receipt: {receipt_id}")
        return 200, response_body

    @classmethod
    def transmit_submission(cls, submission, user) -> dict:
        """
        Direct transmission from WorkflowEngine to Gateway.
        """
        headers = {
            'Idempotency-Key': f"idemp_{submission.id}_v{submission.version}",
            'X-Correlation-ID': f"corr_{submission.id}_{int(time.time()*1000)}"
        }
        payload = {
            'ReturnKey': submission.report_key,
            'InstCode': '0000013',
            'FinYear': submission.period_year,
            'PeriodQuarter': submission.period_quarter,
            'PeriodMonth': submission.period_month,
            'Values': submission.values,
            'DynamicRows': submission.dynamic_rows,
            'Maker': {'id': user.id, 'name': user.name, 'email': user.email},
            'Checker': {'id': submission.checker_id, 'name': submission.checker_name},
        }
        status_code, body = cls.process_payload(payload, headers)
        return body

    @classmethod
    def _log_gateway(cls, direction, status_code, correlation_id, idempotency_key, message):
        GatewayAuditLog.objects.create(
            direction=direction,
            endpoint='/api/v2/regulatory/gateway',
            status_code=status_code,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
            message=message
        )
