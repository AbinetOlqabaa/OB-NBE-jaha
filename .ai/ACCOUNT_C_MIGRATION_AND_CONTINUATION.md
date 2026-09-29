QUOTA-SAFETY RULE

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
- **Frontend**: React 19 SPA, TypeScript, Vite, Tailwind CSS v4, Lucide icons, Motion.
- **Backend**: Real Express server running in Node.js v22 on port 3000 (`server.ts`).
- **Django**: **DOES NOT EXIST.** There are zero Python files or Django configurations. Ignore historical references to Django in legacy prompt files.
- **Database**:
  - Backend server storage is in-memory (`Map` structures) seeded with verified Oromia Bank departments and accounts.
  - Client storage is real browser `IndexedDB` (`OromiaBank_NBE_Regulatory_DB`) supporting offline field drafts and audit trail caching.
- **Central Bank Gateway**: Simulated locally via `src/services/nbeSimulator.ts` (`/api/nbe-simulator/*`) due to production NBE requiring dedicated physical leased-line VPN and mTLS hardware smart cards.

## 2. Recovery Assessment Status
- **Build Status**: Verified passing (`compile_applet` and `npm run build`).
- **Type Checking**: Verified clean with 0 errors (`npm run lint` / `tsc --noEmit`).
- **Automated Tests**: 100% green across all 7 test categories (`npx tsx src/tests/run-all-tests.ts`).
- **Current State of Documentation**:
  - `.ai/CURRENT_IMPLEMENTATION_STATUS.md`: Created and up-to-date with complete answers to all 10 recovery audit questions.
  - `.ai/CHANGELOG.md`: Created and recording milestone history.
  - `.ai/COMPLETION_EVIDENCE.md`: Contains verified gate execution logs.
  - 4 empty placeholder files identified for future documentation fill:
    - `.ai/BACKEND_DJANGO_ARCHITECTURE.md` (Should document that Express is used instead of Django)
    - `.ai/AUTH_SEED_DATA_AND_BIOMETRIC_TESTING.md`
    - `.ai/AUDITOR_ROLE_AND_AUDIT_WORKFLOW.md`
    - `.ai/NBE_SIMULATOR_MICROSERVICE.md`

## 3. Directives for Next Agent
1. **DO NOT REBUILD EXISTING FUNCTIONALITY**: The 24 report templates, formula engine, validation engine, maker-checker workflow, biometric authentication, NBE simulator, and UI dashboards are fully functional and tested.
2. **Authoritative Backend Entry**: Always execute or verify backend changes against `server.ts`.
3. **Verification Commands**:
   - `npm run lint` (`tsc --noEmit`)
   - `npx tsx src/tests/run-all-tests.ts`
   - `npm run build`
4. **Active Tasks / Unfinished Work**:
   - The recovery assessment requested by the user is complete.
   - All tests are passing.
   - Wait for explicit user instructions before beginning new feature development or architecture changes.
