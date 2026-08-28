# NextBoard — Next.js 16 Feature Showcase

A demo application highlighting App Router patterns, Server Components, Server Actions, caching, streaming, JWT middleware, and more.

## Quick start

```bash
npm install
cp .env.example .env.local
npm run db:init
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

**Demo login:** `demo@example.com` / `password123`

## Feature map

| URL | Feature |
|-----|---------|
| `/` | Route group `(marketing)`, `next/image`, React Compiler counter |
| `/login`, `/register` | Route group `(auth)`, Server Actions + Zod validation |
| `/dashboard` | Parallel routes `@stats` / `@activity`, nested Suspense, slot `loading.tsx` skeletons |
| `/posts` | `unstable_cache` with revalidate tag + timestamp |
| `/posts/[slug]` | Dynamic `[slug]`, `generateMetadata()`, segment `error.tsx` (`?debug=error`) |
| `/gallery` | Intercepting route modal `@modal/(.)[id]` |
| `/gallery/[id]` | Full page on hard navigation |
| `/tasks` | `useOptimistic` + Server Actions (no client fetch / `useEffect`) |
| `middleware.ts` | JWT cookie auth via `jose` |
| `app/error.tsx`, `app/not-found.tsx` | Global error / 404 fallbacks |
| `@stats/default.tsx`, `@activity/default.tsx` | Parallel slot defaults |
| `next.config.ts` | `reactCompiler: true` |

## Stack

- Next.js 16, React 19, TypeScript, Tailwind CSS 4
- SQLite (`better-sqlite3`) — dev only; use Turso/Postgres in production
- Zod, jose, bcryptjs

## Scripts

- `npm run dev` — development server
- `npm run build` — production build
- `npm run db:init` — reset and seed `data/demo.db`

## Architecture

```
(marketing)/  → public landing
(auth)/       → login / register
(app)/        → protected: dashboard, posts, gallery, tasks
middleware    → JWT verification (edge-safe, no DB)
lib/db        → SQLite (Node.js runtime only)
```

SQLite requires `export const runtime = "nodejs"` on DB-backed routes and actions.
