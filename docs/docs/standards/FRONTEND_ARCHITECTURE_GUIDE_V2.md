# Frontend Architecture Guide v2

> **Purpose:** A universal, framework-agnostic reference for building production-grade frontend applications. Feed this entire document as a system prompt or project context to any LLM before scaffolding a new project. Every rule here is a hard constraint.
>
> **Scope:** The architectural principles apply universally. Examples use Next.js + React + TypeScript, but substitute your framework and keep the principles.

---

## Table of Contents

1. [Core Principles](#1-core-principles)
2. [Project Structure](#2-project-structure)
3. [Routing & Navigation](#3-routing--navigation)
4. [API Layer](#4-api-layer)
5. [Server Components & Server Actions](#5-server-components--server-actions)
6. [State Management](#6-state-management)
7. [Component Architecture](#7-component-architecture)
8. [Authentication & Authorization](#8-authentication--authorization)
9. [Styling & Design Tokens](#9-styling--design-tokens)
10. [TypeScript Conventions](#10-typescript-conventions)
11. [Error Handling](#11-error-handling)
12. [Form Handling](#12-form-handling)
13. [Performance](#13-performance)
14. [Testing Strategy](#14-testing-strategy)
15. [Module Configuration Pattern](#15-module-configuration-pattern)
16. [Provider Composition](#16-provider-composition)
17. [Adding a New Feature (Checklist)](#17-adding-a-new-feature-checklist)
18. [Do's and Don'ts](#18-dos-and-donts)
19. [Appendix: Recommended Tech Stack](#appendix-recommended-tech-stack)

---

## 1. Core Principles

These six rules override everything else. When in doubt, refer back here.

| #   | Principle                       | What it means                                                                                                                                                                                                                                          |
| --- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | **Domain colocation**           | Group code by business domain, not by technical layer. All files for "leads" live in one folder. No scattering across `api/services/`, `store/`, `api/types/`.                                                                                         |
| 2   | **Single responsibility**       | Each file does exactly one thing. One component per file. One store per domain. One transformer per domain. One hook per concern.                                                                                                                      |
| 3   | **Server state ≠ Client state** | Data from the API is **server state** (React Query / SWR). UI toggles, auth sessions, sidebar state is **client state** (Zustand / Pinia / Svelte stores). Never mix them. Never put `isLoading`, `error`, `items[]`, or `fetchX()` in a client store. |
| 4   | **Transform at the boundary**   | Backend shapes (`snake_case`) are converted to frontend shapes (`camelCase`) **exactly once**, in the service/API layer. No backend shapes leak into components.                                                                                       |
| 5   | **Explicit over implicit**      | Type every function. Name every constant. Export through barrels. No magic strings, no `any`, no implicit return types.                                                                                                                                |
| 6   | **Minimal coupling**            | Each domain should be self-contained. A change in `leads/` should never require touching `meetings/`. Shared logic goes in `lib/shared/` or `lib/utils/`.                                                                                              |

### Why These Matter

Violating principle 3 is the single most common mistake in frontend projects. When you put API data into a Zustand/Pinia store with manual `isLoading` flags, `fetchX()` methods, and `items[]` arrays, you lose:

- **Automatic caching** — the same data re-fetched on every mount
- **Background refetching** — stale data shown until manual refresh
- **Race condition handling** — rapid navigation causes state corruption
- **Cache invalidation** — manual `refetch()` calls scattered everywhere
- **Deduplication** — two components mounting = two API calls

A server-state library (React Query, SWR, Apollo) solves all of these. Your client store should only hold **things that don't exist on the server**: selected tab, sidebar collapsed, modal open/close, theme preference.

---

## 2. Project Structure

```
.
├── src/
│   ├── app/                              # Framework router (Next.js App Router / equivalent)
│   │   ├── (auth)/                       # Unauthenticated pages (login, signup, forgot-password)
│   │   ├── (dashboard)/                  # Authenticated dashboard modules
│   │   │   └── <role>/                   # One folder per user role
│   │   │       ├── config.ts             # Nav items, route constants, theme — NO JSX
│   │   │       ├── layout.tsx            # Role-specific layout wrapper
│   │   │       ├── page.tsx              # Overview / home page for this role
│   │   │       └── <feature>/
│   │   │           └── page.tsx
│   │   ├── api/                          # Route handlers (BFF layer for auth cookies, proxying)
│   │   ├── globals.css                   # Design tokens & global styles (single source of truth)
│   │   ├── layout.tsx                    # Root layout — provider composition
│   │   └── page.tsx                      # Root redirect handler
│   │
│   ├── components/
│   │   ├── layout/                       # Shell layout (sidebar, top nav, mobile dock)
│   │   ├── providers/                    # Context providers — no visual output
│   │   ├── shared/                       # Reusable feature-level components (tables, modals, panels)
│   │   │   ├── index.ts                  # Barrel — ALL shared imports go through here
│   │   │   └── <component-name>/
│   │   │       └── index.tsx
│   │   └── ui/                           # Primitives (Button, Badge, Input, Dialog…)
│   │
│   ├── hooks/                            # App-wide custom hooks (useMediaQuery, useDebounce, etc.)
│   │
│   ├── lib/                              # Business logic & state — DOMAIN-BASED
│   │   ├── api-client.ts                 # Singleton HTTP client — the ONLY place fetch is called
│   │   ├── <domain>/                     # One folder per business domain
│   │   │   ├── api.ts                    # Service functions — calls apiClient
│   │   │   ├── hooks.ts                  # React Query hooks (useQuery / useMutation)
│   │   │   ├── store.ts                  # Client state store (UI-only — optional)
│   │   │   ├── transformers.ts           # Backend ↔ Frontend shape conversions
│   │   │   ├── types.ts                  # Domain types (Backend* + Frontend shapes)
│   │   │   ├── constants.ts              # Domain-specific constants (optional)
│   │   │   └── index.ts                  # Barrel — export only what other code needs
│   │   └── utils/                        # Pure utility functions (formatDate, cn, etc.)
│   │
│   ├── middleware.ts                      # Route protection + API auth injection
│   └── types/                            # System-wide global TypeScript types & enums
│
├── public/                               # Static assets (images, icons, SVGs)
├── next.config.ts                        # Framework configuration
├── tsconfig.json                         # TypeScript — path aliases configured here
└── package.json
```

### Why Domain-Based?

| Layer-Based (avoid)                  | Domain-Based (use this)             |
| --------------------------------------- | -------------------------------------- |
| All API services in `api/services/`     | Each domain owns its `api.ts`          |
| All stores in `store/`                  | Each domain owns its `store.ts`        |
| All types in `api/types.ts`             | Each domain owns its `types.ts`        |
| All transformers in one file            | Each domain owns its `transformers.ts` |
| Finding lead code = search 4+ folders   | Finding lead code = open `lib/leads/`  |
| Adding a domain = edit 4+ layer folders | Adding a domain = create 1 folder      |

**The test:** If you search the codebase for "where does lead data get fetched, transformed, cached, and typed?" — the answer should be **one folder**: `lib/leads/`. If the answer involves 4+ directories, you have a layer-based structure that will not scale.

### Domain Folder Template

Every domain folder follows this exact structure. No exceptions.

```
lib/leads/
├── api.ts              # Service functions (fetchLeads, createLead, etc.)
├── hooks.ts            # React Query hooks (useLeads, useCreateLead, etc.)
├── store.ts            # Zustand store — ONLY if this domain needs shared UI state
├── transformers.ts     # snake_case ↔ camelCase conversions
├── types.ts            # BackendLead (snake_case) + Lead (camelCase)
├── constants.ts        # Domain-specific constants (optional)
└── index.ts            # Barrel exports
```

---

## 3. Routing & Navigation

### Route Group Convention

Use framework grouping mechanisms (parenthesized folders in Next.js) to organize pages without affecting the URL:

- `(auth)/` — Unauthenticated pages (login, signup). No shared layout with dashboard.
- `(dashboard)/` — All authenticated role dashboards. Each sub-folder is a URL segment.

### Role → URL Mapping

Each user role maps to a unique URL prefix and folder:

```
<role-name>  ←→  /<url-prefix>  ←→  (dashboard)/<url-prefix>/
```

This mapping **must** be maintained in sync across:

1. **`middleware.ts`** — `ROLE_DASHBOARD_MAP` (server-side route protection & redirect)
2. **`lib/auth/store.ts`** — `ROLE_DASHBOARD_MAP` (client-side redirect after login)

> **Rule:** If you add a new role, update **both** files. If they drift, users land on wrong dashboards or get access denied.

### Page & Layout Convention

```
(dashboard)/<role>/
├── config.ts       # Nav items, route constants — NO JSX, no hooks
├── layout.tsx      # Wraps children in DashboardShell — "use client"
├── page.tsx        # Overview page
└── <feature>/
    └── page.tsx
```

### Route Constants

Never hardcode URL strings in components. Define them in `config.ts`:

```ts
export const ADMIN_ROUTES = {
  overview: "/admin",
  users: "/admin/users",
  userDetail: (id: string) => `/admin/users/${id}`,
} as const;
```

Use these constants in navigation: `router.push(ADMIN_ROUTES.userDetail(id))`.

---

## 4. API Layer

### Architecture (Request Flow)

```
Component
     ↓ calls hook
Query Hook          (lib/<domain>/hooks.ts)
     ↓ calls service
Service Function    (lib/<domain>/api.ts)
     ↓ calls singleton
apiClient           (lib/api-client.ts)
     ↓ fetch with credentials
Middleware           (injects Bearer token from cookie)
     ↓
Backend API          (/api/v1/*)
```

**Every HTTP request goes through `apiClient`.** Components never call `fetch()` directly.

### The `apiClient` (`lib/api-client.ts`)

A singleton class (or module) wrapping `fetch`. Key behaviors:

- Always sends `credentials: 'include'` — cookies flow automatically.
- On **401**: attempts token refresh via `/api/auth/refresh`, then **retries once**.
- On second **401**: redirects to `/login`.
- Handles **204 No Content** gracefully (returns `null`).
- Throws a structured `AppError` for all non-OK responses — never a raw `Error`.
- Provides typed methods: `get<T>()`, `post<T>()`, `patch<T>()`, `delete()`.
- Accepts an optional **`fetchOptions`** parameter to pass through framework-specific options.

```ts
import { apiClient } from "@/lib/api-client";

const { data } = await apiClient.get<ResponseType>("/api/v1/items", {
  page: "1",
});
const { data } = await apiClient.post<ResponseType>("/api/v1/items", payload);
const { data } = await apiClient.patch<ResponseType>(
  `/api/v1/items/${id}`,
  updates,
);
await apiClient.delete(`/api/v1/items/${id}`);
```

### Singleton Safety on the Server

> **Security Warning:** In server-side environments (Node.js), a singleton `apiClient` is shared across **all incoming requests from all users**. If the singleton stores a user's Bearer token, cookie, or any per-user state as an instance property, **User B will make requests using User A's credentials.**

**The rule:** `apiClient` must be **stateless**. It should never hold per-user data in memory.

- **Safe:** `apiClient` delegates auth to middleware (middleware reads cookies per-request and injects `Authorization` headers). The `apiClient` itself knows nothing about tokens.
- **Safe:** `apiClient` accepts auth headers as function parameters, not stored state.
- **Unsafe:** `apiClient.setToken(token)` storing a token as a class property.
- **Unsafe:** A constructor that reads cookies at instantiation time.

**For server-side code (RSCs, Route Handlers, Server Actions)** that needs auth, use one of these approaches:

```ts
// Option 1: Per-request client factory (preferred for server-side)
import { cookies } from "next/headers";

function createServerClient() {
  const token = cookies().get("access_token")?.value;
  return {
    get: <T>(url: string) =>
      fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      }).then((r) => r.json() as Promise<T>),
  };
}

// Option 2: Pass auth as a parameter to the stateless singleton
await apiClient.get<T>("/api/v1/leads", {
  headers: { Authorization: `Bearer ${token}` },
});
```

**Summary:** On the client → use the singleton (middleware handles auth). On the server → either use a per-request factory or pass auth explicitly. Never store tokens in the singleton.

### Domain Service (`lib/<domain>/api.ts`)

Each domain wraps `apiClient` and applies transformations. Service functions **always return frontend types** — never raw backend shapes:

```ts
// lib/leads/api.ts
import { apiClient } from "@/lib/api-client";
import { transformLead } from "./transformers";
import type {
  BackendLeadListResponse,
  Lead,
  FetchLeadsParams,
  LeadListResult,
} from "./types";

export async function fetchLeads(
  params: FetchLeadsParams,
): Promise<LeadListResult> {
  const { data } = await apiClient.get<BackendLeadListResponse>(
    "/api/v1/leads",
    {
      page: String(params.page ?? 1),
      limit: String(params.limit ?? 50),
    },
  );
  return {
    items: data.items.map(transformLead), // ← transform at the boundary
    total: data.total,
  };
}
```

### Domain Types (`lib/<domain>/types.ts`)

Keep backend and frontend shapes in the **same file**, separated by clear sections:

```ts
// lib/leads/types.ts

// ── Backend shapes (match wire format exactly) ──────────────
export interface BackendLead {
  id: string;
  lead_name: string;
  created_at: string;
  assigned_user_id: string | null;
}

export interface BackendLeadListResponse {
  items: BackendLead[];
  total: number;
  skip: number;
  limit: number;
}

// ── Frontend shapes (used in components) ────────────────────
export interface Lead {
  id: string;
  leadName: string;
  createdAt: string;
  assignedUserId: string | null;
}

export interface LeadListResult {
  items: Lead[];
  total: number;
}

// ── Query/mutation parameter types ──────────────────────────
export interface FetchLeadsParams {
  page?: number;
  limit?: number;
  status?: string;
}
```

**Naming rule:** Backend types use `Backend*` prefix and `snake_case` fields. Frontend types use no prefix and `camelCase` fields.

### Domain Transformers (`lib/<domain>/transformers.ts`)

All `snake_case` → `camelCase` conversions live here. This is the **only** place where backend field names appear:

```ts
// lib/leads/transformers.ts
import type { BackendLead, Lead } from "./types";

export function transformLead(raw: BackendLead): Lead {
  return {
    id: raw.id,
    leadName: raw.lead_name,
    createdAt: raw.created_at,
    assignedUserId: raw.assigned_user_id,
  };
}

// Reverse transformer for mutations (frontend → backend)
export function toBackendLead(lead: Partial<Lead>): Record<string, unknown> {
  return {
    lead_name: lead.leadName,
    assigned_user_id: lead.assignedUserId,
  };
}
```

> **Rule:** Transform at the service boundary (in `api.ts`). Components and query hooks **never** see `snake_case` fields.

### Domain Barrel (`lib/<domain>/index.ts`)

Export only what the rest of the app needs:

```ts
// lib/leads/index.ts
export { fetchLeads, createLead, updateLead, deleteLead } from "./api";
export { useLeads, useLead, useCreateLead } from "./hooks";
export type { Lead, FetchLeadsParams } from "./types";
```

### Next.js Fetch Compatibility

> **Important if using Next.js App Router:** Next.js heavily patches the native `fetch` API to support granular caching (`force-cache`, `revalidate`), server-side request deduplication, and static generation. Your `apiClient` must not fight this.

**Rules for Next.js compatibility:**

- The `apiClient` should accept an optional `fetchOptions` bag that gets spread into the underlying `fetch()` call. This allows service functions to pass through Next.js-specific options like `{ next: { revalidate: 60 } }` or `{ cache: 'no-store' }`.
- On the **server** (inside RSCs or Server Actions), use native `fetch` with Next.js options directly when you need framework caching. The `apiClient` singleton is primarily for **client-side** requests.
- Never instantiate `apiClient` at module scope with hardcoded headers that prevent Next.js from deduplicating requests on the server.

```ts
// In a service function that may be called from an RSC:
export async function fetchLeads(
  params: FetchLeadsParams,
): Promise<LeadListResult> {
  const { data } = await apiClient.get<BackendLeadListResponse>(
    "/api/v1/leads",
    { page: String(params.page ?? 1) },
    { next: { revalidate: 60 } }, // ← passed through to fetch()
  );
  return { items: data.items.map(transformLead), total: data.total };
}
```

---

## 5. Server Components & Server Actions

> **This section applies to frameworks with server rendering capabilities** (Next.js App Router, Nuxt 3, SvelteKit). If your framework is fully client-rendered (Vite + React SPA), skip this section — all data fetching goes through React Query on the client.

### The Key Distinction

Modern frameworks introduce **Server Components** (RSCs in React/Next.js) that run on the server and ship **zero JavaScript** to the client. They are designed for **initial data loading**, not interactive state.

| Scenario                                                           | Use                                       | Why                                                           |
| ------------------------------------------------------------------ | ----------------------------------------- | ------------------------------------------------------------- |
| Page first-load data (dashboard overview, profile, static lists)   | **Server Component** with `async/await`   | No JS shipped, faster TTFB, SEO-friendly                      |
| Interactive, paginated data (tables with sorting, search, filters) | **Client Component** with React Query     | Needs client-side cache, background refetch, pagination state |
| Form submissions / write operations                                | **Server Action** or React Query mutation | Both valid — see decision guide below                         |
| Real-time or polling data                                          | **Client Component** with React Query     | Needs `refetchInterval`, WebSocket integration                |
| Data shared across many client components                          | **Client Component** with React Query     | Needs shared cache accessible from multiple components        |

### Server Component Data Fetching

For initial page loads, fetch data directly in the Server Component. No hooks, no `"use client"`, no React Query:

```tsx
// app/(dashboard)/admin/page.tsx — this is a Server Component by default
import { fetchDashboardStats } from "@/lib/dashboard/api";

export default async function AdminOverview() {
  const stats = await fetchDashboardStats(); // runs on server, no JS shipped

  return (
    <div>
      <h1>Dashboard</h1>
      <StatsDisplay stats={stats} /> {/* can be a Server Component too */}
      <InteractiveLeadTable /> {/* "use client" — uses React Query */}
    </div>
  );
}
```

### Server → Client Hydration Pattern (Eliminating Loading Spinners)

The biggest user-facing performance win: **fetch data on the server, pass it to a client component as `initialData`, and let React Query take over for subsequent interactions.** This eliminates the initial loading spinner entirely.

```tsx
// app/(dashboard)/admin/leads/page.tsx — Server Component
import { fetchLeads } from "@/lib/leads/api";
import { LeadTable } from "./lead-table"; // "use client" component

export default async function LeadsPage() {
  // Fetched on the server — no spinner, HTML arrives with data
  const initialData = await fetchLeads({ page: 1, limit: 50 });

  return <LeadTable initialData={initialData} />;
}
```

```tsx
// app/(dashboard)/admin/leads/lead-table.tsx — Client Component
"use client";
import { useLeads } from "@/lib/leads";
import type { LeadListResult, FetchLeadsParams } from "@/lib/leads";

export function LeadTable({ initialData }: { initialData: LeadListResult }) {
  const [params, setParams] = useState<FetchLeadsParams>({ page: 1 });

  const { data, isLoading } = useLeads(params, {
    initialData: params.page === 1 ? initialData : undefined,
    // React Query uses server data for page 1 — no loading spinner
    // Subsequent pages/filters fetch client-side as normal
  });

  return (
    <DataTable
      data={data?.items ?? []}
      isLoading={isLoading}
      onPageChange={(page) => setParams((p) => ({ ...p, page }))}
    />
  );
}
```

**Why this is optimal:**

| Approach                      | Initial load                                         | Navigation                           | Complexity  |
| ----------------------------- | ---------------------------------------------------- | ------------------------------------ | ----------- |
| Client-only (React Query)     | Spinner → download JS → parse → API call → render | Instant (cached)                  | Simple   |
| Server-only (RSC)             | HTML arrives with data                            | Full page reload for interactions | Simple   |
| **Server + Client hydration** | **HTML arrives with data**                        | **Instant (React Query cache)**   | Moderate |

**Use the hydration pattern for:** Any page that has both an initial data load AND interactive features (sorting, pagination, filtering). This is the majority of dashboard pages.

**Skip it for:** Purely static pages (About, Settings) — just use a Server Component. Purely interactive components with no meaningful first-load (modals, search dropdowns) — just use React Query.

### Server Actions for Mutations

Server Actions can replace React Query mutations for simple form submissions. They run on the server, have direct access to cookies, and integrate with Next.js revalidation:

```ts
// lib/leads/actions.ts
"use server";

import { revalidatePath } from "next/cache";

export async function createLeadAction(formData: FormData) {
  const response = await fetch(`${process.env.API_URL}/api/v1/leads`, {
    method: "POST",
    body: JSON.stringify(Object.fromEntries(formData)),
    headers: { "Content-Type": "application/json" },
  });

  if (!response.ok) throw new Error("Failed to create lead");

  revalidatePath("/admin/leads"); // ← automatically refreshes the page data
}
```

### When to Use Server Actions vs React Query Mutations

```
Does the mutation need optimistic UI updates?
├─ YES → React Query mutation (onMutate + rollback)
└─ NO → Does it need to update React Query cache across components?
         ├─ YES → React Query mutation (queryClient.invalidateQueries)
         └─ NO → Server Action (simpler, runs on server, revalidatePath)
```

**Practical guidance:**

- **Server Actions** work best for: simple forms, admin CRUD, settings updates — anything where a page refresh/revalidation is acceptable.
- **React Query mutations** work best for: interactive UIs where the user expects instant feedback (optimistic updates), or when multiple components need to react to the mutation.
- **Don't mix both for the same operation.** Pick one pattern per mutation.

---

## 6. State Management

> **This is the most critical architectural decision.** Get this wrong and the codebase becomes unmaintainable. Split state into two categories based on its **origin** — never mix them.

### The Two-Bucket Rule

| Bucket              | Tool              | What belongs here                                                                  |
| ------------------- | ----------------- | ---------------------------------------------------------------------------------- |
| **Server state**    | React Query / SWR | Anything from the API: lists, records, counts, stats, paginated results            |
| **Client/UI state** | Zustand / Pinia   | Auth session, modal open/close, selected tab, sidebar collapsed, local form drafts |

> **Important:** Use `useState` for component-local UI state (opening/closing a tab). Use Zustand/Pinia only if **multiple unrelated components** need to share that state.

### Server State — React Query Hooks (`lib/<domain>/hooks.ts`)

```ts
// lib/leads/hooks.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as leadService from "./api";
import type { FetchLeadsParams, CreateLeadPayload } from "./types";

// Query key factory — always arrays, never plain strings
export const leadKeys = {
  all: ["leads"] as const,
  lists: () => [...leadKeys.all, "list"] as const,
  list: (params: FetchLeadsParams) => [...leadKeys.lists(), params] as const,
  details: () => [...leadKeys.all, "detail"] as const,
  detail: (id: string) => [...leadKeys.details(), id] as const,
};

export function useLeads(params: FetchLeadsParams) {
  return useQuery({
    queryKey: leadKeys.list(params),
    queryFn: () => leadService.fetchLeads(params),
    staleTime: 30_000, // 30s — adjust per domain
  });
}

export function useCreateLead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateLeadPayload) => leadService.createLead(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: leadKeys.lists() });
    },
  });
}
```

**React Query rules:**

- Use a **query key factory** per domain — predictable invalidation, no typos.
- Set `staleTime` deliberately — `0` causes waterfall refetches on every mount.
- Prefer **optimistic updates** for mutations that update visible list items.
- Never duplicate fetched data into a client store.
- Use `enabled` option for conditional queries (e.g., only fetch when ID is present).

### Client State — Zustand Stores (`lib/<domain>/store.ts`)

Reserved **only** for state with no server equivalent:

```ts
// lib/leads/store.ts — only if this domain needs persistent UI state
import { create } from "zustand";

interface LeadUIState {
  selectedTab: string;
  isSlideOverOpen: boolean;
  activeLeadId: string | null;
  setSelectedTab: (tab: string) => void;
  openSlideOver: (id: string) => void;
  closeSlideOver: () => void;
}

export const useLeadUIStore = create<LeadUIState>((set) => ({
  selectedTab: "all",
  isSlideOverOpen: false,
  activeLeadId: null,
  setSelectedTab: (tab) => set({ selectedTab: tab }),
  openSlideOver: (id) => set({ isSlideOverOpen: true, activeLeadId: id }),
  closeSlideOver: () => set({ isSlideOverOpen: false, activeLeadId: null }),
}));
```

**Client store rules:**

- Select granularly: `useStore((s) => s.specificValue)` — never subscribe to the whole store.
- **Never** put `isLoading`, `error`, `items[]`, or `fetchX()` methods in a client store.
- Keep stores small (< 50 lines). One store per domain, only if needed.
- Most UI state belongs in `useState` — Zustand is for **cross-component shared** state only.

### The Anti-Pattern to Avoid (Critical)

```ts
// WRONG — This is re-implementing React Query inside Zustand
export const useLeadStore = create((set) => ({
  leads: [],
  isLoading: false,
  error: null,
  pagination: { page: 1, limit: 50 },
  fetchLeads: async (params) => {
    set({ isLoading: true });
    try {
      const data = await leadService.fetchLeads(params);
      set({ leads: data.items, isLoading: false });
    } catch (err) {
      set({ error: err, isLoading: false });
    }
  },
}));
```

**Why this is wrong:** No caching, no background refetching, no stale-while-revalidate, manual loading/error flags, race conditions on rapid navigation, duplicate requests on remount, no retry logic. This pattern creates **every problem** that React Query was designed to solve.

### Decision Flowchart

```
Does this data come from an API?
├─ YES → Is it initial page load data with no client interactivity?
│        ├─ YES → Fetch in a Server Component (RSC) — no JS shipped
│        └─ NO  → Use React Query (client-side server state)
└─ NO → Does it need to be shared across unrelated components?
         ├─ YES → Use Zustand (client state)
         └─ NO → Use useState (local component state)
```

---

## 7. Component Architecture

### Directory Roles

| Directory               | Purpose                                               | Example contents                                  |
| ----------------------- | ----------------------------------------------------- | ------------------------------------------------- |
| `components/layout/`    | Shell layout — sidebar, top nav, mobile dock          | `DashboardShell`, `MobileDockNav`                 |
| `components/providers/` | Context wrappers — no visual output                   | `AuthProvider`, `ThemeProvider`                   |
| `components/shared/`    | Reusable feature components shared across roles/pages | `DataTable`, `SlideOver`, `StatsCard`             |
| `components/ui/`        | Low-level primitives — no business logic              | `Button`, `Badge`, `Input`, `Dialog`              |
| `hooks/`                | App-wide custom hooks (not tied to one domain)        | `useMediaQuery`, `useDebounce`, `useLocalStorage` |

### File & Folder Conventions

- **One component per folder**, folder name in `kebab-case`.
- Main component file is `index.tsx`.
- Colocate sub-components, hooks, and helpers in the same folder.
- If a sub-component is only used within its parent, do **not** export it from `shared/`.

```
shared/
└── data-table/
    ├── index.tsx          # export const DataTable = ...
    ├── table-header.tsx   # sub-component, not exported from shared/
    ├── table-row.tsx      # sub-component
    └── use-sorting.ts     # local hook
```

### Import Shared Components via the Barrel

```ts
// Correct
import { DataTable, StatsCard, SlideOver } from "@/components/shared";

// Wrong — bypasses the barrel
import { DataTable } from "@/components/shared/data-table";
```

### Barrel File Performance Note

> **Caveat:** In large projects, a single massive barrel file (`index.ts` re-exporting 30+ components) can hurt **HMR speed** and **tree-shaking** in bundlers like Webpack. Importing one component evaluates the entire barrel, pulling in all dependencies.

**Mitigation strategies (apply as the project grows):**

1. **Next.js `optimizePackageImports`** — Add `components/shared` to the `optimizePackageImports` array in `next.config.ts`. This tells Next.js to transform barrel imports into direct imports at build time.
2. **Domain-scoped barrels** — Instead of one giant `shared/index.ts`, group into smaller barrels: `shared/tables/index.ts`, `shared/overlays/index.ts`, etc.
3. **Direct imports as escape hatch** — If profiling shows a specific barrel causing slow HMR, bypass it with a direct import and add a comment explaining why.

```ts
// next.config.ts
module.exports = {
  experimental: {
    optimizePackageImports: ["@/components/shared", "lucide-react"],
  },
};
```

**Rule of thumb:** Start with a single barrel. When the barrel exceeds ~20 re-exports or HMR becomes noticeably slow, split into domain-scoped barrels.

### `DashboardShell`

Every role's `layout.tsx` renders `<DashboardShell>`, which provides:

- Collapsible sidebar with the role's `navItems`
- Mobile dock navigation
- Context hook exposing shell state (`isCollapsed`, etc.)
- Configurable module title, badge styles, user profile slot

```tsx
// (dashboard)/admin/layout.tsx
<DashboardShell
  navItems={adminNavItems} // from config.ts
  basePath="/admin"
  moduleTitle="Admin"
  userProfile={<UserProfile />}
>
  {children}
</DashboardShell>
```

### Component Sizing Guidelines

| Component type   | Max lines | If exceeded                                            |
| ---------------- | --------- | ------------------------------------------------------ |
| Page component   | ~200      | Extract sub-components or custom hooks                 |
| Shared component | ~150      | Extract sub-components into the same folder            |
| Custom hook      | ~80       | Split into smaller hooks                               |
| Zustand store    | ~50       | You're probably storing server state — use React Query |

---

## 8. Authentication & Authorization

### Cookie-Based Auth

Authentication uses **HTTP-only cookies** (`access_token`, `refresh_token`). JavaScript never reads the raw token values — this is intentional for XSS protection.

### Request Flow

```
Browser Request
     ↓
middleware.ts
├── /api/v1/* → injects Authorization: Bearer <token> from cookie
└── /<protected-route> → redirects to /login if no cookie
     ↓
Route Handler (/app/api/auth/*) ← BFF layer, manages cookies
     ↓
Backend API
```

### `middleware.ts`

- Defines `PROTECTED_PREFIXES` — routes requiring authentication.
- Defines `AUTH_ROUTES` — routes only for unauthenticated users.
- For API proxy calls (`/api/v1/*`), reads the cookie and injects `Authorization` header — **no manual token management anywhere else**.
- Defines `ROLE_DASHBOARD_MAP` for role-based redirects.

### Auth Store (`lib/auth/store.ts`)

This is a valid use of Zustand because the current user is **client-side session state**, not server-cached data:

| Method                   | Purpose                                                  |
| ------------------------ | -------------------------------------------------------- |
| `fetchMe()`              | Called on app mount — populates user from `/api/auth/me` |
| `login(email, password)` | Posts to `/api/auth/login`, sets user state              |
| `logout()`               | Posts to `/api/auth/logout`, clears state, redirects     |
| `getUserRole()`          | Returns the primary role string                          |
| `getDashboardPath()`     | Resolves the dashboard URL for the current user's role   |

### Checking Roles

```tsx
// Use the auth store
const role = useAuthStore((s) => s.getUserRole)();

// Never read cookies from JavaScript
// Never hardcode role strings — use constants
```

---

## 9. Styling & Design Tokens

### `globals.css` — Single Source of Truth

All design tokens are defined **once** in `globals.css`:

```css
:root {
  --color-primary: 142 71% 45%;
  --color-destructive: 0 84% 60%;
  --color-muted: 210 40% 96%;
  --color-border: 214 32% 91%;

  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;

  --shadow-card: 0 1px 3px 0 rgb(0 0 0 / 0.1);

  --font-sans: "Inter", sans-serif;
  --font-mono: "JetBrains Mono", monospace;
}

.dark {
  --color-primary: 142 71% 55%;
  --color-muted: 217 33% 17%;
}
```

> **Rule:** If you're about to write a hex value, `rgba()`, or `style={{ color: '#...' }}` — stop. Either use an existing token, or add a new named token to `globals.css` first.

### Use Semantic Tokens

```
  text-foreground       bg-background
  text-muted-foreground bg-muted
  text-primary          bg-primary/10
  border-border         bg-destructive

  text-gray-700         bg-[#f5f5f5]
  border-gray-200       text-[#333]
```

### Typography

Fonts are loaded **once** in the root layout and exposed as CSS variables. Never import a font in a component file.

### Animations

- Keep animations subtle (< 300ms).
- Use `layout` transitions for DOM changes.
- Never animate colors with JavaScript — use CSS transitions.
- Use a consistent animation library (Framer Motion, Auto Animate, CSS transitions).

---

## 10. TypeScript Conventions

### Type Location

| Location                | Naming            | Case         | Purpose                         |
| ----------------------- | ----------------- | ------------ | ------------------------------- |
| `lib/<domain>/types.ts` | `Backend*` prefix | `snake_case` | Wire types from the backend     |
| `lib/<domain>/types.ts` | No prefix         | `camelCase`  | Frontend domain types (UI-side) |
| `src/types/`            | Varies            | `camelCase`  | Global enums, shared interfaces |

### Rules

- **No `any`** — if genuinely unavoidable, add an `eslint-disable` with an explaining comment.
- Type all function parameters and return types explicitly.
- Use `export type` for pure type-only exports.
- Use **`@/` path aliases** for all imports — no relative paths beyond one level (`../`).

```ts
// Aliases everywhere
import { useLeadUIStore } from "@/lib/leads";
import { DataTable } from "@/components/shared";
import { cn } from "@/lib/utils";

// Deep relative paths
import { cn } from "../../../lib/utils";
```

### Enum vs Union Type

Prefer string union types for small sets. Use enums only when the backend sends matching values and they're used across many files:

```ts
// For small, fixed sets
type Priority = "LOW" | "MEDIUM" | "HIGH";

// For backend-matching enums used across many files
enum LeadStatus {
  NEW = "NEW",
  WARM = "WARM",
  HOT = "HOT",
  CLOSED = "CLOSED",
}
```

---

## 11. Error Handling

### `AppError` Class

All API errors thrown by the HTTP client are instances of `AppError`:

```ts
class AppError extends Error {
  message: string; // Human-readable — show to user
  statusCode: number; // HTTP status (400, 401, 403, 422, 500…)
  detail: unknown; // Backend's structured detail — use for field-level errors
  data: unknown; // Full raw response body
}
```

### Error Handling in Mutations

```ts
useMutation({
  mutationFn: createLead,
  onError: (err) => {
    if (!(err instanceof AppError)) throw err;

    // 1. Always show the top-level message
    toast.error(err.message);

    // 2. For 422 validation errors — map to form fields
    if (err.statusCode === 422 && Array.isArray(err.detail)) {
      err.detail.forEach((issue: { loc: string[]; msg: string }) => {
        const field = issue.loc.at(-1);
        if (field) form.setError(field, { message: issue.msg });
      });
    }
  },
});
```

### Error Handling Rules

- **Never silently swallow errors** — always show a toast or field-level message.
- **Show `err.detail` when actionable** — don't show only "Something went wrong" when the backend gives you field-level errors.
- For form submissions: map `422` errors to individual input fields.
- For mutations: use the server-state library's error callback (`onError`), not try/catch in the component.
- `<ErrorBoundary>` wraps the app tree for unhandled **render** errors — async errors are handled by the query library.

### Error Boundary

Every app should have a root `<ErrorBoundary>` that:

- Catches unhandled render errors
- Shows a user-friendly fallback UI
- Provides a "retry" action
- Logs errors to a monitoring service (Sentry, LogRocket, etc.) in production

---

## 12. Form Handling

### Recommended Approach

Use a form library (React Hook Form, Formik, VeeValidate) with schema validation (Zod, Yup):

```ts
// lib/leads/schemas.ts
import { z } from "zod";

export const createLeadSchema = z.object({
  name: z.string().min(1, "Name is required"),
  email: z.string().email("Invalid email").optional(),
  phone: z.string().min(10, "Phone must be at least 10 digits"),
  priority: z.enum(["LOW", "MEDIUM", "HIGH"]),
});

export type CreateLeadFormData = z.infer<typeof createLeadSchema>;
```

### Form Rules

- Define validation schemas alongside domain types (in the domain folder).
- Use the schema as the single source of truth for both frontend validation and TypeScript types.
- Map backend `422` errors to form field errors (see Error Handling section).
- Keep form state local — forms don't belong in Zustand.
- Separate form submission logic into mutation hooks.

---

## 13. Performance

### Lazy Loading

Heavy interactive components (tables, charts, editors) should be lazy-loaded:

```ts
// components/shared/lazy.tsx
import dynamic from "next/dynamic";

export const LazyDataTable = dynamic(() => import("./data-table"), {
  ssr: false,
  loading: () => <div className="h-64 w-full animate-pulse rounded-2xl bg-muted/20" />,
});
```

**Rules:**

- All lazy imports use `ssr: false` for browser-only components.
- Every lazy import defines a **skeleton fallback** — never a blank space.
- Register all heavy components in a central `shared/lazy.tsx` file.

### General Performance Rules

- Use the query library's `staleTime` to avoid unnecessary refetches.
- Use `React.memo` sparingly — only when profiling shows a re-render problem.
- Virtualize long lists (> 100 rows) with `@tanstack/react-virtual` or equivalent.
- Images use the framework's image component (or `<img>` with explicit `width` / `height`).
- Avoid barrel re-exports that pull in the entire domain — export only what's needed.
- Use `Suspense` boundaries to show loading states for lazy components.
- Debounce search inputs (300ms+) to avoid excessive API calls.

---

## 14. Testing Strategy

### Test Pyramid

| Layer                 | Tool                  | What to test                                                  |
| --------------------- | --------------------- | ------------------------------------------------------------- |
| **Unit tests**        | Vitest / Jest         | Transformers, utility functions, query key factories, schemas |
| **Component tests**   | Testing Library       | Shared components render correctly, handle props, fire events |
| **Integration tests** | Testing Library + MSW | Hooks + components working together with mocked API responses |
| **E2E tests**         | Playwright / Cypress  | Critical user flows (login, create lead, navigation)          |

### What to Test Per Domain

For each domain folder (`lib/<domain>/`), test:

1. **Transformers** — `transformLead(backendData)` returns correct frontend shape.
2. **Query hooks** — Using MSW to mock API, verify correct key structure and data flow.
3. **Schemas** — Valid data passes, invalid data fails with correct error messages.

### What NOT to Test

- Don't test implementation details (internal state of React Query cache).
- Don't test third-party library behavior.
- Don't write tests that break when styling changes.
- Don't test `apiClient` internals — test the domain hooks that use it.

---

## 15. Module Configuration Pattern

Every role/module folder has a `config.ts` file:

```ts
// (dashboard)/admin/config.ts
import { LayoutDashboard, Users, FileText } from "lucide-react";

// 1. Nav items — consumed by DashboardShell
export const adminNavItems: NavItem[] = [
  { name: "Overview", href: "/admin", icon: LayoutDashboard },
  { name: "Users", href: "/admin/users", icon: Users },
  { name: "Leads", href: "/admin/leads", icon: FileText },
];

// 2. Route constants — never hardcode URL strings in components
export const ADMIN_ROUTES = {
  overview: "/admin",
  users: "/admin/users",
  userDetail: (id: string) => `/admin/users/${id}`,
  leads: "/admin/leads",
  leadDetail: (id: string) => `/admin/leads/${id}`,
} as const;

// 3. Theme constants (optional)
export const ADMIN_THEME = { primary: "emerald" };
```

**Rules:**

- `config.ts` contains **zero** JSX and **zero** hooks — it's pure data.
- Import route strings from `ROUTES` constants — never inline `/admin/leads` in a component.
- Use functions for dynamic routes: `ROUTES.userDetail(id)`, not string interpolation in components.

---

## 16. Provider Composition

The root layout stacks all global providers in a specific order:

```tsx
<ErrorBoundary>
  <QueryClientProvider client={queryClient}>
    <ThemeProvider>
      <AuthProvider>
        {" "}
        {/* calls fetchMe() on mount */}
        <ToastProvider>
          <ConfirmDialogProvider>
            {children}
            <Toaster />
          </ConfirmDialogProvider>
        </ToastProvider>
      </AuthProvider>
    </ThemeProvider>
  </QueryClientProvider>
</ErrorBoundary>
```

**Rules:**

- Only add providers here if they are **truly global** across every page.
- Feature-specific providers go in the feature's `layout.tsx`, not the root.
- Provider order matters: `ErrorBoundary` outermost, `QueryClient` before anything that uses queries, `Auth` before anything that needs user context.
- Never nest more than 6-7 providers — if you need more, compose them in a `<Providers>` wrapper component.

---

## 17. Adding a New Feature (Checklist)

Follow these steps in order when adding a new page or feature area:

### Step 1: Create the Domain Folder

Create `src/lib/<domain>/` with these files:

| File              | Purpose                                                                                 |
| ----------------- | --------------------------------------------------------------------------------------- |
| `types.ts`        | Backend response types (`Backend*` prefix, `snake_case`) + frontend types (`camelCase`) |
| `transformers.ts` | `Backend*` → frontend type conversion functions                                         |
| `api.ts`          | Service functions using `apiClient`, returning frontend types                           |
| `hooks.ts`        | Server-state hooks (`useQuery` / `useMutation`)                                         |
| `store.ts`        | Client state store — **only if** this domain needs shared UI state                      |
| `constants.ts`    | Domain-specific constants — **only if** needed                                          |
| `index.ts`        | Barrel: export only what the rest of the app needs                                      |

### Step 2: Create the Page

Create `src/app/(dashboard)/<role>/<feature>/page.tsx`

### Step 3: Update Config

Update the role's `config.ts` — add a nav item and a route constant.

### Step 4: Use Shared Components

Import from `@/components/shared` — do not re-implement data tables, slide-overs, or stat cards.

### Step 5: Register Heavy Components

If your feature introduces a new heavy component, register it in `shared/lazy.tsx`.

### Step 6: Export New Shared Components

If you created a new reusable component, export it through `components/shared/index.ts`.

> **The domain folder structure (Step 1) is the canonical template.** Every domain folder should look the same. A developer navigating to any domain should immediately know where types, API calls, hooks, and state live.

---

## 18. Do's and Don'ts

### Do

- Add `"use client"` at the top of any file using hooks, browser APIs, or event handlers
- Use **Server Components** for initial page data that doesn't need client interactivity
- Use a **server-state library** (React Query / SWR) for interactive, client-side API data
- Use **Server Actions** for simple form submissions where optimistic UI isn't needed
- Use a **client store** (Zustand / Pinia) only for UI state with no server equivalent
- Use a **query key factory** for every domain — structured, predictable invalidation
- Define all design tokens in `globals.css` — never in component files
- Use semantic CSS tokens (`text-primary`, `bg-muted`) — never raw color values
- Surface `err.detail` from `AppError` — show field errors, not just generic toasts
- Select from stores granularly: `useStore((s) => s.specificValue)`
- Keep service functions thin — call `apiClient`, transform, return domain types
- Export all shared components through barrel files (split barrels if > 20 exports)
- Define all route strings in `config.ts` `ROUTES` constants
- Use `@/` path aliases for all imports
- Keep domain folders self-contained — types, API, hooks, transformers in one place
- Use `void` when calling async functions in event handlers without `await`
- Prefer `useState` for component-local UI state before reaching for a store
- Validate forms with schemas (Zod / Yup) — single source of truth for validation + types
- Debounce search inputs and expensive computations
- Pass framework-specific fetch options through `apiClient` (e.g., `{ next: { revalidate } }`)
- Prefer Server Component data fetching over client-only React Query for initial page loads when using a framework that supports it (SSR/RSC)

### Don't

- Use client stores (Zustand) to cache API responses, loading flags, or fetch functions
- Write hex colors, `rgba()`, or hardcoded values in component files
- Swallow errors silently or show only generic messages
- Scatter one domain's files across `api/services/`, `store/`, and `api/types/`
- Read or manage auth tokens from JavaScript — cookies are server-managed
- Use relative imports beyond one level (`../../`)
- Add `any` without an explaining comment
- Add global providers without strong justification
- Hardcode role names as raw strings — use constants
- Put JSX or hooks in `config.ts`
- Create monolithic stores (> 100 lines with fetch logic) — use React Query
- Mix backend `snake_case` and frontend `camelCase` in the same type
- Import `fetch` directly in components — use `apiClient`
- Put form state in global stores — keep it local
- Use Server Actions and React Query mutations for the same operation — pick one

---

## Appendix: Recommended Tech Stack

This guide is designed for the following stack, but the principles apply broadly. Substitute libraries as needed — keep the architecture.

| Layer          | Library                | Purpose                              | Alternatives                                    |
| -------------- | ---------------------- | ------------------------------------ | ----------------------------------------------- |
| Framework      | Next.js (App Router)   | File-system routing, SSR, middleware | Nuxt, SvelteKit, Remix, Vite + Router           |
| UI Library     | React                  | Component model                      | Vue, Svelte, Solid                              |
| Language       | TypeScript             | Type safety                          | —                                               |
| Server State   | React Query (TanStack) | Data fetching, caching, sync         | SWR, Apollo Client, tRPC                        |
| Client State   | Zustand                | Lightweight client-side stores       | Pinia (Vue), Svelte stores, Jotai, Valtio       |
| Styling        | Tailwind CSS           | Utility-first CSS                    | CSS Modules, Styled Components, Vanilla Extract |
| Form Handling  | React Hook Form + Zod  | Forms + validation                   | Formik + Yup, VeeValidate (Vue)                 |
| Animations     | Framer Motion          | Layout & entrance animations         | Auto Animate, CSS transitions                   |
| Icons          | Lucide React           | Consistent icon set                  | Heroicons, Phosphor                             |
| Toasts         | Sonner                 | Toast notifications                  | React Hot Toast                                 |
| Date Utilities | date-fns               | Date formatting                      | Day.js, Luxon                                   |
| Testing        | Vitest + Playwright    | Unit + E2E testing                   | Jest + Cypress                                  |
| API Mocking    | MSW                    | Mock API for dev/test                | Mirage.js                                       |

> **Adapting for other stacks:** Substitute the tools but keep the **principles**: domain colocation, server/client state split, transform at boundary, centralized HTTP client, single source of truth for design tokens, typed schemas for validation.
