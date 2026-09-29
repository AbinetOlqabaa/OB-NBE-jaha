import os
import json
import time
import uuid
import requests
from django.utils import timezone
from .models import GatewayScenario, NbeSubmissionRecord, GatewayAuditLog

class NbeGatewayService:
    """
    Authoritative NBE Gateway & Central Bank Adapter.
    
    Architecture:
    - Acts as the secure client adapter between Oromia Bank Core Backend and the NBE Intake Gateway.
    - During testing & local development, targets the independent NBE Simulator microservice (port 8001).
    - In production, targets the National Bank of Ethiopia IPsec VPN mTLS endpoint (e.g., https://nbe.gov.et/api/v2/regulatory/gateway).
    - Preserves canonical NBE payload formats, correlation tracking, idempotency deduplication, and retry backoff.
    - The OB frontend NEVER interacts directly with the simulator or central bank; all communication flows through this adapter.
    """

    SIMULATOR_BASE_URL = os.environ.get('NBE_SIMULATOR_URL', 'http://127.0.0.1:8001/api/v1/nbe-simulator')
    MAX_RETRIES = 3
    TIMEOUT_SECONDS = 15

    @classmethod
    def get_simulator_url(cls, path: str = 'submit') -> str:
        base = cls.SIMULATOR_BASE_URL.rstrip('/')
        clean_path = path.lstrip('/')
        return f"{base}/{clean_path}"

    @classmethod
    def transmit_submission(cls, submission, user) -> dict:
        """
        Transmits a validated & checker-approved regulatory submission to the NBE Gateway.
        Converts submission entity into standard NBE envelope format.
        """
        correlation_id = f"corr_{submission.id}_{int(time.time()*1000)}"
        idempotency_key = f"idemp_{submission.id}_v{submission.version}"

        # Construct canonical NBE payload
        return_items = [
            {'Code': str(k), 'Value': v}
            for k, v in (submission.values or {}).items()
        ]

        dynamic_areas = []
        for area_id, rows in (submission.dynamic_rows or {}).items():
            if isinstance(rows, list):
                row_values = [r.get('values', r) if isinstance(r, dict) else r for r in rows]
                try:
                    area_num = int(area_id)
                except ValueError:
                    area_num = 1
                dynamic_areas.append({'Area': area_num, 'Rows': row_values})

        payload = {
            'ReturnKey': submission.report_key,
            'InstCode': '0000013',
            'FinYear': submission.period_year,
            'StartDate': str(submission.period_start or f"{submission.period_year}-01-01"),
            'EndDate': str(submission.period_end or f"{submission.period_year}-12-31"),
            'ReturnItemsList': return_items,
            'DynamicItemsList': dynamic_areas,
            'Maker': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
            },
            'Checker': {
                'id': submission.checker_id,
                'name': submission.checker_name,
            },
        }

        headers = {
            'Content-Type': 'application/json',
            'Idempotency-Key': idempotency_key,
            'X-Correlation-ID': correlation_id,
            'X-Institution-Code': '0000013',
            'Authorization': 'Bearer NBE_MTLS_CERT_SIMULATED_2026',
        }

        status_code, response_body = cls.dispatch_http(
            endpoint=cls.get_simulator_url('submit'),
            payload=payload,
            headers=headers,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
            report_key=submission.report_key
        )

        return response_body

    @classmethod
    def dispatch_http(
        cls,
        endpoint: str,
        payload: dict,
        headers: dict,
        correlation_id: str,
        idempotency_key: str,
        report_key: str
    ) -> tuple[int, dict]:
        """
        Executes outbound HTTP POST with retry backoff for 500/504 errors.
        """
        url = endpoint
        for attempt in range(1, cls.MAX_RETRIES + 1):
            try:
                resp = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=cls.TIMEOUT_SECONDS
                )
                status_code = resp.status_code
                try:
                    resp_json = resp.json()
                except Exception:
                    resp_json = {'raw': resp.text, 'statusCode': status_code}

                cls._log_gateway(
                    direction='OUTBOUND',
                    status_code=status_code,
                    correlation_id=correlation_id,
                    idempotency_key=idempotency_key,
                    message=f"[Attempt {attempt}] NBE Gateway returned HTTP {status_code} for return {report_key}"
                )

                # Retry on 500 or 504
                if status_code in (500, 504) and attempt < cls.MAX_RETRIES:
                    time.sleep(0.15 * attempt)
                    continue

                return status_code, resp_json

            except requests.exceptions.RequestException as exc:
                cls._log_gateway(
                    direction='OUTBOUND',
                    status_code=503,
                    correlation_id=correlation_id,
                    idempotency_key=idempotency_key,
                    message=f"[Attempt {attempt}] Connection failure to NBE Gateway at {url}: {str(exc)}"
                )
                if attempt < cls.MAX_RETRIES:
                    time.sleep(0.2 * attempt)
                    continue

                fallback_body = {
                    'success': False,
                    'statusCode': 503,
                    'error': 'Service Unavailable',
                    'message': f"Failed to connect to NBE Central Bank Gateway at {url}: {str(exc)}",
                    'correlationId': correlation_id,
                }
                return 503, fallback_body

        return 500, {'success': False, 'statusCode': 500, 'error': 'Max retries exhausted'}

    @classmethod
    def proxy_to_simulator(cls, method: str, path: str, data: dict = None, headers: dict = None) -> tuple[int, dict]:
        """
        Reverse-proxy helper so OB Backend can relay simulator telemetry/scenario to the frontend.
        """
        url = cls.get_simulator_url(path)
        req_headers = {'Content-Type': 'application/json'}
        if headers:
            for k in ['Idempotency-Key', 'idempotency-key', 'X-Correlation-ID', 'x-correlation-id', 'X-Simulator-Force-Scenario']:
                if k in headers:
                    req_headers[k] = headers[k]

        try:
            if method.upper() == 'GET':
                resp = requests.get(url, headers=req_headers, timeout=cls.TIMEOUT_SECONDS)
            elif method.upper() == 'POST':
                resp = requests.post(url, json=data, headers=req_headers, timeout=cls.TIMEOUT_SECONDS)
            elif method.upper() == 'DELETE':
                resp = requests.delete(url, headers=req_headers, timeout=cls.TIMEOUT_SECONDS)
            else:
                return 405, {'error': f"Method {method} not supported"}

            try:
                return resp.status_code, resp.json()
            except Exception:
                return resp.status_code, {'raw': resp.text}
        except requests.exceptions.RequestException as exc:
            return 503, {
                'error': 'Simulator Offline',
                'message': f"Unable to reach NBE Simulator microservice at {url}: {str(exc)}"
            }

    @classmethod
    def _log_gateway(cls, direction, status_code, correlation_id, idempotency_key, message):
        try:
            GatewayAuditLog.objects.create(
                direction=direction,
                endpoint='/api/v2/regulatory/gateway',
                status_code=status_code,
                correlation_id=correlation_id,
                idempotency_key=idempotency_key,
                message=message
            )
        except Exception:
            pass
