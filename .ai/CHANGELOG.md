# CHANGELOG

All notable changes and engineering enhancements for the Oromia Bank NBE Regulatory Reporting Platform are recorded in this file.

---

## [1.3.0-auditor-assessment] - 2026-09-28

### Added
- **Full Recovery Assessment for Auditor Role Implementation** (`.ai/19_AUDITOR_ROLE_AND_AUDIT_WORKFLOW.md`):
  - Completed thorough inspection across the entire project and all `.ai` documentation.
  - Formulated precise answers for all 10 recovery inquiries in `.ai/CURRENT_IMPLEMENTATION_STATUS.md`.
  - Clarified technical stack reality: both Express (`server.ts` port 3000), Django Core (`/backend` SQLite `db.sqlite3`), and Django NBE Simulator (`/nbe_simulator_service` SQLite `simulator_db.sqlite3` port 8001) are active and functional.
  - Cataloged gap analysis for first-class Auditor role: registration request, approval workflow, auditor dashboard, work queue, report audit view, revision history, evidence management, findings system (severity/status), audit notes, remediation tracking, formal audit reports, and Django boundary enforcement.

---

## [1.2.0-nbe-simulator] - 2026-09-28

### Added
- **Independent NBE Simulator Django Microservice** (`/nbe_simulator_service`):
  - Standalone Django project with own `manage.py`, settings, SQLite store (`simulator_db.sqlite3`), and dedicated port `8001`.
  - Models: `SimulatorScenario`, `SimulatorSubmission`, `SimulatorRequestLog`.
  - Full schema and envelope validation for all 24 NBE report definitions and institutional code `0000013`.
  - 6 runtime simulation modes: `ALWAYS_SUCCESS` (200/201 + cryptographic receipt `NBE-REC-YYYYMMDD-XXXX`), `VALIDATION_ERROR` (422), `AUTH_FAILURE` (401), `TIMEOUT` (504), `SERVER_ERROR` (500), `RANDOM_FLAKY`.
  - Deterministic test triggers: `X-Simulator-Force-Scenario` headers and query parameter overrides.
  - Idempotency deduplication: `Idempotency-Key` header prevents duplicate processing and returns existing receipts (`SUCCESS_IDEMPOTENT_DUPLICATE`).
  - Unit test suite (`nbe_simulator_service/apps/simulator/tests.py`): 11 tests covering all scenarios and 24 return definitions.
- **NBE Gateway & Adapter Integration**:
  - `backend/apps/nbe_gateway/gateway_service.py` and `src/services/nbeAdapter.ts`: Outbound HTTP client communicating with port 8001 with exponential retry backoff.
  - `server.ts`: Reverse-proxy endpoints for `/api/nbe-simulator/*` and auto-supervision of the Django simulator process.
  - Complete integration documentation in `.ai/NBE_SIMULATOR_AND_TEMPORARY_INTEGRATION.md`.

---

## [1.1.0-ui-ux] - 2026-09-28

### Added
- **Dedicated Automated Responsive UI & Layout Test Suite** (`src/tests/responsive-ui-and-layout.test.ts`):
  - 9 viewport classification matrix (Small Mobile 320px to Large Desktop 1920px).
  - 16-component React export and inventory verification.
  - Minimum 44px mobile touch target enforcement (`min-h-[44px]`, `min-w-[44px]`).
  - Horizontal page overflow prevention testing (`overflow-x-auto`, `truncate`, `line-clamp`).
  - Zero-pill compliance audit on static metadata.
  - Multi-breakpoint navigation adaptation verification.
  - Dynamic area table dual card/table view mode verification.
  - Non-color status indicator audit (dual icon + text pairing for WCAG AA).
- **Integrated into Root Test Runner** (`src/tests/run-all-tests.ts`):
  - Now executes 8 complete test suites sequentially with 100% green verification.

### Changed
- **Zero-Pill Discipline Refinements (Frontend Design Constitution)**:
  - `src/components/DynamicReportForm.tsx`: Replaced static pill capsules (`rounded-full`) in validation summary strips with clean unboxed metadata and subtle rounded tags (`rounded-md`).
  - `src/App.tsx`: Replaced `rounded-full` badge in toast hardware verification notifications with clean `rounded-md` metadata tags.
  - `src/components/AdminDashboard.tsx`: Cleaned tab count indicators from `rounded-full` to clean `rounded-md` indicators.
  - `src/components/OfflineStorageModal.tsx`: Replaced `rounded-full` sync status tags with clean unboxed/rounded-md tags.
  - `src/components/UserSettingsModal.tsx`: Replaced `rounded-full` authentication history count tag with clean `rounded-md` tag.
  - `src/components/NbeHealthIndicator.tsx`: Updated status telemetry badge from `rounded-full` to `rounded-md`.
  - `src/components/KeyboardShortcutsModal.tsx`: Updated badge tag from `rounded-full` to `rounded-md`.
  - `src/components/OfflineStatusIndicator.tsx`: Updated sync counter from `rounded-full` to `rounded-md`.

### Verified
- `compile_applet`: Succeeded cleanly.
- `lint_applet` (`npm run lint` / `tsc --noEmit`): Exited with 0 errors.
- `npx tsx src/tests/run-all-tests.ts`: All 8 automated test suites passed 100% green.

---

## [1.0.0-audit] - 2026-09-28
### Added
- Initial recovery assessment answering architectural inquiries.
- Verified test suites for core regulatory engines, RBAC, NBE simulator, biometrics, PDF generation, and IndexedDB storage.
