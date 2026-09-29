# CHANGELOG

All notable changes and engineering enhancements for the Oromia Bank NBE Regulatory Reporting Platform are recorded in this file.

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
- Comprehensive recovery assessment answering all 10 architectural inquiries.
- Confirmation of Express/Node.js architecture and clarification of Django non-existence.
- Verified test suites for core regulatory engines, RBAC, NBE simulator, biometrics, PDF generation, and IndexedDB storage.
