# NBE INTAKE GATEWAY SIMULATOR MICROSERVICE
**Application**: Oromia Bank NBE Regulatory Reporting Platform  
**Target Central Bank**: National Bank of Ethiopia (Bank Supervision Directorate)  
**Implementation**: `src/services/nbeSimulator.ts` & `src/services/nbeAdapter.ts`  
**Endpoint**: `POST /api/nbe-simulator/submit`  

---

## 1. Purpose & Design Rationale
Live production submission to the National Bank of Ethiopia requires:
- Leased point-to-point IPsec VPN tunnel directly to NBE datacenters.
- Hardware-bound mutual TLS (mTLS) smart cards issued by NBE.
- Live production credentials and central bank signing keys.

To enable complete end-to-end development, verification, negative path testing, and retry resilience without external infrastructure dependencies, an intake simulator microservice is embedded directly in the platform.

## 2. Configurable Simulation Modes
The simulator supports 6 runtime behavior scenarios configurable via the UI or `POST /api/nbe-simulator/scenario`:

1. `ALWAYS_SUCCESS` (HTTP 200 / 201):
   - Validates envelope schema, checks mandatory fields, and issues an official cryptographic receipt (e.g. `NBE-REC-20260928-XXXX`).
2. `VALIDATION_ERROR` (HTTP 422):
   - Simulates central bank rejection for invalid figures, negative balances where disallowed, or missing dynamic schedules.
3. `AUTH_FAILURE` (HTTP 401):
   - Simulates expired mTLS tokens or invalid institution client credentials.
4. `TIMEOUT` (HTTP 504):
   - Injects artificial latency exceeding client timeout threshold to test adapter abort controllers and retry behavior.
5. `SERVER_ERROR` (HTTP 500):
   - Simulates NBE central bank database or gateway internal failures.
6. `RANDOM_FLAKY`:
   - Introduces random latency (50ms - 2000ms) and 30% intermittent failure rate to stress-test retry backoff.

## 3. Idempotency Protection
- All submissions require an `Idempotency-Key` header (`idemp_{submissionId}_v{version}`).
- Duplicate deliveries with the same key return the existing receipt without duplicate ledger processing (`200 OK` or `208 Already Reported`).
