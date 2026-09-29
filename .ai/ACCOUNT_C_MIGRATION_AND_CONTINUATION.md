# QUOTA-SAFETY RULE & RECOVERY CONTINUATION BRIEF

When the agent detects that the current session is approaching a practical
token/quota limit, it must NOT begin another large task.

It must first:
1. finish the current safe code operation,
2. run available tests,
3. save all files,
4. update CURRENT_IMPLEMENTATION_STATUS.md,
5. update CHANGELOG.md,
6. record the exact unfinished task,
7. record the exact files being modified,
8. record known errors,
9. record the next action,
10. leave the project in a buildable state whenever reasonably possible.

The next agent must be able to continue from these files without reconstructing
the previous conversation.

---

# ACCOUNT C MIGRATION & RECOVERY CONTINUATION BRIEF

## 1. Technical Stack Reality & Baseline

- **Frontend**: React 19 SPA, TypeScript, Vite, Tailwind CSS v4, Lucide icons, Motion (`src/`).
- **Express Backend**: Real Express server running in Node.js on port 3000 (`server.ts`). Serves client assets in production, proxies simulator endpoints, and auto-supervises the Django NBE Simulator on port 8001.
- **Django Core Backend**: Real Django 5.2 application in `/backend` (`ob_nbe_platform`), with modular apps (`accounts`, `departments`, `permissions`, `reports`, `workflows`, `audit`, `notifications`, `nbe_gateway`) and persistent SQLite database (`backend/db.sqlite3`).
- **Django NBE Simulator Microservice**: Real independent Django project in `/nbe_simulator_service` (`simulator_project`) running on port 8001 with its own persistent SQLite database (`nbe_simulator_service/simulator_db.sqlite3`).
- **Client Storage**: Real browser `IndexedDB` (`OromiaBank_NBE_Regulatory_DB`) supporting offline field drafts and audit trail caching.
- **NBE Central Bank Adapter**: Outbound HTTP adapter (`src/services/nbeAdapter.ts` and `backend/apps/nbe_gateway/gateway_service.py`) targeting port 8001 with retry backoff, correlation tracking, and idempotency protection.

---

## 2. Recovery Assessment Summary (10 Inquiries)

1. **Actually Implemented**: 
   - 24 canonical NBE report definitions with AST formula calculation and validation rules.
   - Maker Workspace (drafting, Excel import/export, submission gate).
   - Checker Inbox (review, visual diff, 4-eyes approval/rejection/correction).
   - Admin Dashboard (user approvals, department hierarchy, special access delegations).
   - Authentication (password, WebAuthn fingerprint, optical camera Face ID, OTP verification).
   - Audit Trail (immutable compliance ledger, biometric event logging, JSON export).
   - IndexedDB offline storage & cryptographic vault export for remote site visits.
   - Independent Django NBE Simulator microservice (port 8001) supporting 6 scenarios, idempotency, and 24 returns.
   - Express server (`server.ts`) and Django core backend (`/backend`).
2. **Partially Implemented**: 
   - `AUDITOR` role exists in the user seed list (`auditor@oromiabank.com`) and user models, and has read-only submission viewing permissions in `AuthorizationEngine`.
   - Lacks dedicated auditor workflows, work queue, findings system, evidence attachments, remediation tracking, and dedicated auditor dashboard.
3. **Simulated**: 
   - Physical leased-line Central Bank IPsec VPN & mTLS hardware smart cards (simulated via the independent Django simulator microservice on port 8001).
   - Face Biometrics (uses optical camera stream + HTML5 canvas pixel hash extraction).
   - SMS/Email OTP (simulated via console/audit logging).
4. **Missing (for Auditor Role)**:
   - Dedicated Auditor Registration request and admin approval flow.
   - Dedicated Auditor Dashboard (`AuditorDashboard.tsx`).
   - Audit Work Queue (pending review, completed, flagged).
   - Deep Report Audit View (line-by-line inspection, historical diffs).
   - Visual Workflow Timeline (Maker -> Checker -> Delivery history).
   - Evidence Management (uploading, cataloging, viewing supporting evidence).
   - Audit Findings System with severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFORMATIONAL`) and status (`OPEN`, `UNDER_REVIEW`, `REMEDIATION_PENDING`, `CLOSED`).
   - Audit Notes & Comments.
   - Remediation Tracking (assigning action items with deadlines to Makers/Checkers).
   - Formal Audit Reports Generator (exportable memo/report).
   - Django Auditor permission boundary enforcement (strictly preventing Maker/Checker privilege escalation).
   - Dedicated routes, components, APIs, and automated test suite.
5. **Where Previous Agent Stopped**:
   - Completed the independent Django NBE Simulator microservice on port 8001, ran all tests green, created `.ai/NBE_SIMULATOR_AND_TEMPORARY_INTEGRATION.md`, and paused when the user requested the initial recovery assessment for `19_AUDITOR_ROLE_AND_AUDIT_WORKFLOW.md`.
6. **Whether a Django Backend Exists**:
   - **YES, two distinct Django projects exist**: `/backend` (OB Core Platform) and `/nbe_simulator_service` (NBE Simulator Microservice).
7. **Whether Any Backend/Database is Real or Simulated**:
   - Real persistent SQLite databases (`backend/db.sqlite3` and `nbe_simulator_service/simulator_db.sqlite3`).
   - Real browser persistent storage (`IndexedDB`).
   - Simulated external Central Bank network gateway.
8. **How Authentication Currently Works**:
   - Password hashing, account status check, WebAuthn passkey lookup, optical camera Face ID hash check, and OTP verification across both Express and Django.
9. **How Biometric Registration Currently Works**:
   - WebAuthn passkey registration (`navigator.credentials.create()`) and camera Face ID image hashing; zero bypass enforced for un-enrolled accounts.
10. **How NBE Integration Currently Works**:
    - Maker/Checker triggers delivery -> Adapter serializes canonical JSON -> dispatches HTTP POST to simulator on port 8001 with retries and idempotency headers -> receives `NBE-REC-YYYYMMDD-XXXX` receipt -> records in database and audit ledger.

---

## 3. Directives for Next Step

1. **DO NOT REBUILD EXISTING FUNCTIONALITY**: Do not alter or break existing 24 report templates, AST formulas, Maker-Checker workflows, biometric authentication, offline IndexedDB storage, or the NBE Simulator microservice.
2. **Next Action**: Implement the Auditor Role as a first-class role per `19_AUDITOR_ROLE_AND_AUDIT_WORKFLOW.md`:
   - Auditor registration request with requested oversight scope.
   - Auditor approval workflow in Admin Dashboard.
   - Auditor authentication flow and dedicated responsive `AuditorDashboard.tsx`.
   - Audit work queue with filtering and status indicators.
   - Deep report audit view with historical period comparison.
   - Visual workflow timeline.
   - Evidence management (attachments catalog).
   - Audit findings system with severity, status, and remediation tracking.
   - Formal audit reports generator.
   - Enforce Auditor permission boundaries in Django (strictly prohibiting Maker draft creation or Checker review approvals).
   - Dedicated APIs in Express / Django, routes, and automated test suite.
3. **Verification Commands**:
   - `npm run lint` (`tsc --noEmit`)
   - `npm test` (`tsx src/tests/run-all-tests.ts`)
   - `npm run test:simulator` (`python3 nbe_simulator_service/manage.py test apps.simulator.tests`)
   - `npm run build`
