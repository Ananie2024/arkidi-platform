# 002 — Frontend Stack: React 19 / Tailwind v4 (formally deferred)

- **Status:** Deferred (decision recorded, not yet executed)
- **Date:** 2026-08-26
- **Applies to:** `frontend/`

## Context

The frontend currently pins:

- React **18.3.1** (`react`, `react-dom`, `@types/react`)
- Tailwind CSS **3.4.4** (JS config `frontend/tailwind.config.ts`, PostCSS)

React 19 and Tailwind v4 are both stable and this codebase is still small, so
now is the cheapest possible time to upgrade. However, upgrading during the
current work (delivering the Survey / Document / Governance / sacramental
amendment APIs and RBAC) would couple a large dependency migration to feature
delivery and force compatibility checks across every dependency that consumes
the React runtime.

## Decision

**Formally defer the React 19 and Tailwind v4 upgrades.** Remain on React 18.3 +
Tailwind 3.4 until one of the explicit triggers below fires, then upgrade both
in a single, dedicated change — never as part of a feature PR.

### Deferral rationale

- **Risk isolation.** React 19 and Tailwind v4 are breaking releases. Mixing a
  migration with the present feature/security work makes regressions harder to
  bisect.
- **Dependency surface.** `lucide-react`, `react-leaflet`, `qrcode.react`,
  `@vitejs/plugin-react`, and `@testing-library/react` all have React-19 or
  Tailwind-v4 compatibility caveats that need a deliberate verification step;
  that is a separate work item, not a side quest.
- **Near-term feature value is flat.** No planned UI work depends on a React 19
  feature or a Tailwind v4 primitive.

### Triggers that force the upgrade

1. A security or maintenance fix requires React ≥ 19 (or a transitive
   dependency drops React 18 support).
2. Tailwind v3 enters maintenance-only and a required plugin/primitives need v4.
3. An approved feature requires `react-server` / concurrent-only capabilities
   present only in React 19.
4. The next major feature milestone after blockers clear (data entry begins), at
   which point the frontend is still small enough to migrate cheaply.

## Consequences

- Until a trigger fires, `package.json` constraints stay at `react ^18.3.1` and
  `tailwindcss ^3.4.4`.
- When the upgrade happens it must: bump core deps + `@types/*`, migrate
  Tailwind config to the v4 CSS-first model, update the `vite`/PostCSS chain,
  run the existing Vitest suite (`npm test`) and `npm run build`, and be
  reviewed with no feature changes in the same diff.
- This decision is re-evaluated whenever a new dependency is added to the
  frontend.