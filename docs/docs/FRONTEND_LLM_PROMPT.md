# AI Assistant System Prompt — Frontend

Copy and paste the text block below into your IDE's AI rules (e.g., `.cursorrules`, GitHub Copilot Custom Instructions, or ChatGPT Custom Instructions) so the AI contextually understands our frontend architecture and generates code that automatically adheres to our conventions.

````text
# Frontend Architecture — LLM Reference

> **Instructions:** Use this as a system prompt or project context when scaffolding new frontend projects. Treat every rule as a hard constraint.

---

## Core Principles (Non-Negotiable)

1. **Domain colocation** — Group by business domain, not technical layer. All code for "leads" lives in `lib/leads/`.
2. **Server state ≠ Client state** — API data → React Query / SWR. UI-only state → Zustand / Pinia. Never mix.
3. **Transform at the boundary** — `snake_case` → `camelCase` once in the service layer. Components never see backend shapes.
4. **Single responsibility** — One component per file. One store per domain. One transformer per domain.
5. **Explicit over implicit** — Type everything. Name every constant. No `any`. No magic strings.
6. **Minimal coupling** — Domains are self-contained. A change in `leads/` never requires touching `meetings/`.

---

## Project Structure

```

src/
├── app/ # Router (Next.js App Router / equivalent)
│ ├── (auth)/ # Unauthenticated pages
│ ├── (dashboard)/ # Authenticated dashboards
│ │ └── <role>/ # One folder per user role
│ │ ├── config.ts # Nav items, route constants — NO JSX
│ │ ├── layout.tsx # Role layout wrapper
│ │ ├── page.tsx # Overview page
│ │ └── <feature>/page.tsx
│ ├── api/ # Route handlers (BFF layer)
│ ├── globals.css # Design tokens (single source of truth)
│ ├── layout.tsx # Root layout — provider stack
│ └── page.tsx # Root redirect
│
├── components/
│ ├── layout/ # Shell (sidebar, top nav, mobile dock)
│ ├── providers/ # Context providers — no visual output
│ ├── shared/ # Reusable feature components
│ │ ├── index.ts # Barrel exports
│ │ └── <name>/index.tsx
│ └── ui/ # Primitives (Button, Badge, Input, Dialog)
│
├── hooks/ # App-wide custom hooks
│
├── lib/ # Business logic — DOMAIN-BASED
│ ├── api-client.ts # Singleton HTTP client (stateless, no stored tokens)
│ ├── <domain>/ # One folder per business domain
│ │ ├── types.ts # Backend\* (snake_case) + Frontend (camelCase) types
│ │ ├── transformers.ts # snake_case <-> camelCase converters
│ │ ├── api.ts # Service functions -> apiClient -> transform -> return
│ │ ├── hooks.ts # React Query hooks (useQuery / useMutation)
│ │ ├── store.ts # Zustand — ONLY for shared UI state (optional)
│ │ └── index.ts # Barrel exports
│ └── utils/ # Pure utilities (cn, formatDate, etc.)
│
├── middleware.ts # Route protection + API auth injection
└── types/ # Global enums & shared interfaces

```

---

## Domain Folder Rules

Every domain (`lib/<domain>/`) follows this template exactly:

| File              | Content                                         | Rule                                                        |
| ----------------- | ----------------------------------------------- | ----------------------------------------------------------- |
| `types.ts`        | `BackendLead` (snake_case) + `Lead` (camelCase) | Backend types use `Backend*` prefix                         |
| `transformers.ts` | `transformLead(raw) -> Lead`                    | Only place backend field names appear                       |
| `api.ts`          | `fetchLeads(params) -> LeadListResult`          | Always returns frontend types, never raw backend            |
| `hooks.ts`        | `useLeads()`, `useCreateLead()`                 | Query key factory per domain. Set `staleTime` deliberately  |
| `store.ts`        | UI-only state (selectedTab, isOpen)             | Optional. Never `isLoading`, `error`, `items[]`, `fetchX()` |
| `index.ts`        | Barrel — export only what others need           | Keep it tight                                               |

Transformer example (manual mapping, never auto-mappers):

// lib/leads/transformers.ts
export function transformLead(raw: BackendLead): Lead {
  return {
    id: raw.id,
    leadName: raw.lead_name,
    createdAt: raw.created_at,
    assignedUserId: raw.assigned_user_id,
  };
}

---

## State Management Decision

Does this data come from an API?
├─ YES -> Is it initial page load data with no client interactivity?
│        ├─ YES -> Server Component (RSC) — async/await, no JS shipped
│        └─ NO  -> React Query (client-side cache, refetch, pagination)
└─ NO -> Shared across unrelated components?
         ├─ YES -> Zustand store
         └─ NO -> useState

CRITICAL ANTI-PATTERN — Never put API data (items[], isLoading, fetchX()) in Zustand.
This recreates every problem React Query solves: no cache, no background refetch, no dedup, race conditions.

// WRONG — re-implementing React Query inside Zustand
const useLeadStore = create((set) => ({
  leads: [],
  isLoading: false,
  error: null,
  fetchLeads: async (params) => {
    set({ isLoading: true });
    const data = await fetchLeads(params);
    set({ leads: data.items, isLoading: false });
  },
}));

// RIGHT — Zustand holds ONLY UI state, React Query handles API data
const useLeadUIStore = create((set) => ({
  selectedTab: "all",
  isSlideOverOpen: false,
  setSelectedTab: (tab) => set({ selectedTab: tab }),
}));
// API data lives in: const { data, isLoading } = useLeads(params);

React Query hook pattern (use this exact structure per domain):

// lib/leads/hooks.ts
export const leadKeys = {
  all: ["leads"] as const,
  lists: () => [...leadKeys.all, "list"] as const,
  list: (params) => [...leadKeys.lists(), params] as const,
  details: () => [...leadKeys.all, "detail"] as const,
  detail: (id) => [...leadKeys.details(), id] as const,
};

export function useLeads(params, options) {
  return useQuery({
    queryKey: leadKeys.list(params),
    queryFn: () => leadService.fetchLeads(params),
    staleTime: 30_000,
    ...options,
  });
}

export function useCreateLead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: leadService.createLead,
    onSuccess: () => qc.invalidateQueries({ queryKey: leadKeys.lists() }),
  });
}

---

## Server Components & Hydration

For frameworks with SSR/RSC (Next.js, Nuxt, SvelteKit):

- Static first-load data: Fetch in Server Component (async/await). No hooks, no JS shipped.
- Interactive data (tables, filters, pagination): Use React Query in a "use client" component.
- Best of both worlds: Server-fetch initial data -> pass as initialData to React Query -> no spinner on first load, full cache on navigation.
- Mutations: Use Server Actions for simple forms. Use React Query mutations when you need optimistic updates or cross-component cache invalidation. Pick one per operation, never both.

Mutation rule of thumb: If the mutation needs optimistic UI or updates shared client cache -> React Query. Otherwise -> default to Server Actions.

Hydration pattern (eliminates loading spinners):

// app/(dashboard)/admin/leads/page.tsx — Server Component
export default async function LeadsPage() {
  const initialData = await fetchLeads({ page: 1, limit: 50 }); // server-side
  return <LeadTable initialData={initialData} />;
}

// lead-table.tsx — "use client"
export function LeadTable({ initialData }) {
  const { data } = useLeads({ page: 1 }, { initialData }); // no spinner on first load
  return <DataTable data={data?.items ?? []} />;
}

---

## API Layer

Component -> Hook (hooks.ts) -> Service (api.ts) -> apiClient (api-client.ts) -> Backend

- All requests go through apiClient. No direct fetch() in components.
- apiClient is stateless — never stores tokens. Auth is handled by middleware.
- On server-side (RSC/Route Handlers), use a per-request client factory or pass auth explicitly.
- Accept framework-specific fetch options ({ next: { revalidate: 60 } }).
- Throw AppError for all non-OK responses.
- On 401: refresh token -> retry once -> redirect to /login on second 401.

---

## Component Rules

| Directory               | Purpose                                         |
| ----------------------- | ----------------------------------------------- |
| components/layout/      | Shell layout (sidebar, topnav)                  |
| components/providers/   | Context wrappers — no visual output             |
| components/shared/      | Reusable feature components — import via barrel |
| components/ui/          | Primitives — no business logic                  |

- One component per folder, kebab-case folder name, index.tsx main file.
- Import shared components via barrel: import { DataTable } from "@/components/shared".
- Split barrels when > 20 exports (or use optimizePackageImports).

Hard constraint — component sizing:

| Type             | Max lines | If exceeded                             |
| ---------------- | --------- | --------------------------------------- |
| Page component   | ~200      | Extract sub-components or custom hooks  |
| Shared component | ~150      | Extract sub-components into same folder |
| Custom hook      | ~80       | Split into smaller hooks                |
| Zustand store    | ~50       | You're probably storing server state    |

NEVER generate a single file exceeding 200 lines. Always extract.

---

## Authentication

- HTTP-only cookies — JS never reads tokens.
- Middleware injects Authorization header for /api/v1/* requests.
- Auth store (Zustand) holds user object — valid because it's session state, not server data.
- ROLE_DASHBOARD_MAP must be synced between middleware.ts and lib/auth/store.ts.

---

## Styling

- All tokens in globals.css — colors, spacing, radii, shadows, fonts.
- Use semantic tokens: text-primary, bg-muted. Never text-gray-700, bg-[#f5f5f5].
- Fonts loaded once in root layout. Never import fonts in component files.
- Animations < 300ms. Use CSS transitions for colors.

---

## TypeScript

- No `any` without eslint-disable + explaining comment.
- Type all params and return types.
- Use @/ path aliases. No relative imports beyond ../
- Prefer string unions for small sets. Use enums when backend sends matching values.
- Use `export type` for type-only exports.

---

## Error Handling

class AppError extends Error {
  statusCode: number; // 400, 401, 403, 422, 500
  message: string;    // Human-readable — safe to show in toast
  detail: unknown;    // Backend's structured detail (e.g., field-level validation errors)
  data: unknown;      // Full raw response body
}

- All API errors are AppError instances — thrown by apiClient.
- Never swallow errors. Always show toast or field-level message.
- Map 422 responses to individual form field errors via err.detail.
- Use onError callback in mutations, not try/catch in components.
- Root <ErrorBoundary> for unhandled render errors.

---

## Forms

- Use a form library (React Hook Form, Formik) with schema validation (Zod, Yup).
- Schema = single source of truth for validation + TypeScript types.
- Keep form state local. Never in Zustand.
- Define schemas in the domain folder alongside types.

---

## Performance

- Lazy-load heavy components (ssr: false, skeleton fallback). Register in shared/lazy.tsx.
- Set staleTime on queries (not 0).
- Virtualize long lists (> 100 rows).
- Debounce search inputs (300ms+).
- Use React.memo only when profiling shows re-render issues.

---

## Module Config

Each role folder has config.ts (pure data, zero JSX, zero hooks):
- navItems array for sidebar
- ROUTES constants for all URLs (use functions for dynamic routes)
- Optional theme constants

---

## Provider Order

ErrorBoundary > QueryClientProvider > ThemeProvider > AuthProvider > ToastProvider > ConfirmDialogProvider > {children}

Only truly global providers in root layout. Feature-specific providers in feature layout.tsx.

---

## New Feature Checklist

1. Create lib/<domain>/ with types.ts, transformers.ts, api.ts, hooks.ts, index.ts
2. Create app/(dashboard)/<role>/<feature>/page.tsx
3. Add nav item + route constant to role's config.ts
4. Import shared components from barrel — don't re-implement
5. Register heavy components in shared/lazy.tsx
6. Export new shared components through barrel

---

## Hard Don'ts

- NO API data in Zustand (isLoading, error, items[], fetchX())
- NO direct fetch() in components
- NO hex colors / rgba() in component files
- NO silent error swallowing
- NO domain files scattered across layer folders
- NO tokens stored in apiClient singleton
- NO deep relative imports (../../..)
- NO `any` without explanation
- NO JSX or hooks in config.ts
- NO raw hardcoded role strings
- NO mixing Server Actions + React Query mutations for the same operation
- NO backend snake_case fields leaking into components

---

## Tech Stack (Defaults — Substitute as Needed)

| Concern      | Default               | Alternatives                   |
| ------------ | --------------------- | ------------------------------ |
| Framework    | Next.js (App Router)  | Nuxt, SvelteKit, Remix, Vite   |
| Server State | React Query           | SWR, Apollo, tRPC              |
| Client State | Zustand               | Pinia, Jotai, Valtio           |
| Styling      | Tailwind CSS          | CSS Modules, Styled Components |
| Forms        | React Hook Form + Zod | Formik + Yup                   |
| Testing      | Vitest + Playwright   | Jest + Cypress                 |
| API Mocking  | MSW                   | Mirage.js                      |

Substitute tools, keep principles: domain colocation, server/client state split, transform at boundary, stateless HTTP client, design tokens as single source of truth.
````
