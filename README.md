# O-YAKU — production frontend

Vite + React + TypeScript rebuild of the O-YAKU site, based on the Claude Design prototype
(`O-Yaku Flow.html` + `oy-*.jsx` + the "O-Yaku Design System" token set). This replaces the
prototype's no-bundler, CDN-script setup with a real build.

## Status

Home, Knowledge Base, and Species read live, read-only data from the production Supabase
project (`o-yaku`). Articles, Studio, Shop, Ceramics, About and Contact still run on the seed
data ported from the prototype — wiring them to the database is future work, not part of this
build's approved scope.

## Getting started

```bash
npm install
cp .env.example .env   # already has the live project's URL + public anon key filled in
npm run dev
```

```bash
npm run build      # type-checks then builds to dist/
npm run typecheck  # tsc --noEmit only
```

## Environment variables

| Variable | Purpose |
|---|---|
| `VITE_SUPABASE_URL` | Live O-YAKU Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Public anon/publishable key — safe to ship client-side, RLS does the rest |

## Project layout

```
src/
  ds/            17 hand-rolled design-system primitives (Badge, Button, Card, Dialog, …)
                 ported from the prototype's _ds_bundle.js, typed, no external UI library
  ds/icons.tsx   hand-embedded subset of the Lucide icon set (see "Icons" below)
  components/
    chrome/      SiteHeader, SiteFooter, Section, StubPage, shared NAV/EYE/WRAP constants
    search/      AskBox, ResultArea, SourceRow, Ask — the knowledge-base search UI
    studio/      LessonForm
    ceramics/    PotPreview (the commission calculator's live SVG preview)
  lib/
    supabase.ts  minimal read-only PostgREST fetch wrapper (see "Why not @supabase/supabase-js")
    data.ts      typed query functions against the live tables
    search.ts    v1 knowledge-base search (see "Search" below)
    useMobile.ts 720px breakpoint hook, matches the prototype
  pages/         one file per route
  data/          seed data for the pages not yet wired to the database
  types/         route types + minimal DB row shapes
```

## Why not @supabase/supabase-js?

`src/lib/supabase.ts` is a small hand-written fetch wrapper around PostgREST instead of the
official client. Everything these pages need is a handful of read-only, RLS-filtered SELECTs —
a thin wrapper keeps the dependency surface small. If the project later needs auth, realtime, or
writes, swap that one file for the real client; every call site goes through `pgFetch`/`pgRpc`,
so nothing else needs to change.

## Search (Knowledge Base "Ask")

The prototype's search box was backed by a deterministic mock (`runSearch()` in `oy-data.jsx`)
that only actually answered one hardcoded question. The live database has a `canonical_answers`
table that looks like the natural real backing for this feature, but **it has no public/anon
read policy** — it's admin-only by design (confirmed via `pg_policies`).

Until the studio adds a public-facing RPC or view for it, `src/lib/search.ts` does a pragmatic
v1: an `ILIKE` keyword search across published `knowledge_segments` (title/summary/content),
returned as a list of matching source segments. It deliberately does **not** synthesize a
single "answer" paragraph the way the prototype did — that would mean putting invented text in
front of users and calling it a curated answer. Revisit this once there's a real Q&A backend.

## Icons

The prototype loaded the full Lucide icon set from a CDN (`window.lucide`) at runtime. This
project instead hand-embeds just the ~14 icon shapes actually used (`src/ds/icons.tsx`), sourced
from Lucide's own (ISC-licensed) path data, behind the same `<Icon name size strokeWidth />` API.
Add more icons there if new ones are needed — no CDN, no extra dependency.

## Images

No brand photography or logo files were supplied with the design handoff. Every place the
prototype used `<image-slot>` (its own Claude-Design-only prototyping tool, not for production)
now renders a plain placeholder `<div>`, and the header/footer logo is a temporary text wordmark
(`src/components/chrome/Logo.tsx`). Swap these for real assets as they become available.

## Annual cycle / seasonal actions (Species page)

The prototype hardcoded a single worked example (olive) with a fixed "now = September, next =
October". The real Species page instead:
- loads the species row live by slug,
- loads its species-specific `seasonal_actions` plus its category's general ones,
- loads each action's applicable months from `seasonal_action_months`,
- computes "now" and "next" from the actual current date, not a hardcoded month.

## Known gaps / next steps

- Articles, Studio, Shop, Ceramics, About/Contact are still seed data (by design, for this pass).
- The "report a missing topic" and contact/order forms are UI-only — no backend to send to yet.
- `species.category` values are assumed to align with `deciduous_broadleaf` / `evergreen_broadleaf`
  / `conifer` (matching `knowledge_segment_categories`) — worth double-checking against the live
  data once this is deployed.
- A separate, previously-flagged issue in the live database (some ingestion RPCs are callable by
  `anon`/`authenticated` despite being intended as `service_role`-only) is out of scope for this
  frontend build but still needs fixing on the database side.
