# Frontend Status

_Last updated: 2026-07-19 (added frontend Docker/Nginx deployment + EC2 full-stack Compose)_

## 1. Frontend Overview

A React + Vite single-page app for the Foresight Provider Match API. It covers the full patient
journey (browse providers → get matched → book a slot → track requests) and an admin view for
managing appointment request statuses. Built for a class demo, not production: local JWT storage,
no design system, plain CSS.

## 2. Page List

| Route | Page | Access |
|---|---|---|
| `/login` | `LoginPage` | Public |
| `/` | `ProviderListPage` | Public (summary cards + filters) |
| `/providers/:providerId` | `ProviderDetailPage` | Public to view; booking requires login |
| `/match` | `MatchPage` | Logged in |
| `/appointments` | `MyAppointmentsPage` | Logged in |
| `/appointment-confirmation/:appointmentId` | `AppointmentConfirmationPage` | Logged in |
| `/admin` | `AdminAppointmentsPage` | Logged in as admin only |

## 3. Component Structure

```
src/
├── api/            client.js (axios + JWT interceptor), authApi, providersApi, matchesApi, appointmentsApi
├── components/      Navbar, DemoBanner, ProviderCard, ProviderFilters, AppointmentSlotPicker,
│                     StatusBadge, ProtectedRoute, AdminRoute
├── context/          AuthContext.jsx
├── pages/             LoginPage, ProviderListPage, ProviderDetailPage, MatchPage,
│                       MyAppointmentsPage, AppointmentConfirmationPage, AdminAppointmentsPage
├── utils/formatDate.js  shared date/time formatter (used by cards, slot picker, both appointment tables)
├── App.jsx, main.jsx, styles.css
```

`MatchForm`/`MatchResults`/`AppointmentRequestForm` from the original plan were folded directly into
`MatchPage` and `ProviderDetailPage` — each was only ever used once, so a separate component would
have been a thin wrapper with no reuse benefit.

## 4. API Integration Map

| Frontend action | Endpoint |
|---|---|
| Log in | `POST /auth/login` (form-encoded `username`/`password`) |
| Load current user | `GET /auth/me` |
| Browse/filter providers | `GET /providers/` (state, insurance, specialty, accepting_new_patients) |
| View provider detail | `GET /providers/{id}` |
| Submit match preferences | `POST /provider-matches/` |
| Book a slot | `POST /appointment-requests/` (`{provider_id, slot_id, reason}`) |
| View own requests | `GET /appointment-requests/me` |
| Admin: view all requests | `GET /appointment-requests/` (**new**, admin-only — see §10) |
| Admin: update status | `PATCH /appointment-requests/{id}/status` |

All calls use the exact trailing-slash canonical paths the backend routers define (`/providers/`,
`/provider-matches/`, `/appointment-requests/`) to avoid FastAPI's 307 redirect-on-missing-slash
behavior.

## 5. Auth Behavior

- JWT stored in `localStorage` under `token`.
- Axios request interceptor attaches `Authorization: Bearer <token>` to every call.
- `AuthContext` hydrates the current user via `GET /auth/me` on app load if a token exists; clears
  the token if that call fails (expired/invalid).
- A 401 response anywhere clears the token and hard-redirects to `/login`.
- `ProtectedRoute` redirects unauthenticated visitors to `/login`; `AdminRoute` additionally checks
  `user.role === "admin"` and sends non-admins to `/`.
- After login, the app always lands on `/`. An earlier version tried to redirect back to the page
  that originally required login (a `location.state.from` pattern) — this was removed after testing
  surfaced a real race: in React 18/19 StrictMode (dev), `ProtectedRoute`'s own redirect-on-logout
  could re-fire after the explicit logout navigation and stamp a stale `from` onto the next `/login`
  visit, silently sending the *next* person who logs in (e.g. admin, right after a patient logs out)
  back to the previous user's page instead of home. Since "return to where you were" wasn't a stated
  requirement, removing it was simpler and more robust than fighting the race.

## 6. Demo Credentials

| Role | Email | Password |
|---|---|---|
| Patient | `patient@example.com` | `patient123` |
| Admin | `admin@foresight.com` | `admin123` |

## 7. Demo Flow

1. Load `/` — browse provider summary cards, try the state/insurance/specialty/accepting-patients filters.
2. Log in as the patient.
3. Click a provider card → full detail page with bio, insurance, languages, years of experience, and
   real available slots.
4. `Get Matched` → submit state/concern/insurance/preferred day → ranked provider list with scores.
5. On a provider detail page, pick a slot, add a reason, book it → the app navigates to a dedicated
   **Appointment Confirmation** page showing the provider name, slot time, status (`pending`), reason,
   and a note that the request is pending review, with "View My Appointments" and "Find More
   Providers" buttons.
6. Click "View My Appointments" → the new request appears with status `pending`. Go back to that
   provider's detail page (fresh page load) → the booked slot no longer appears as available.
7. Try booking the exact same slot again (e.g. from a second browser tab logged in separately) →
   `409 Conflict`, "This appointment slot has already been booked." shown inline on the provider page
   (booking errors never navigate away — only a successful booking does).
8. Log out, log in as admin → `Admin` tab → see all requests across all patients → change a status
   in the dropdown → table refetches and shows the new status. Try `/admin` as the patient → bounced
   to `/`.

## 8. How to Run Locally

**Option A — full stack via Docker Compose** (matches production/EC2 exactly: Nginx serving the
built app on port 80):

```bash
docker compose up --build -d
docker ps   # db, api, frontend
```

Open `http://localhost` (port 80).

**Option B — frontend dev mode** (hot reload, for active frontend development):

```bash
docker compose up --build db api -d   # backend only
cd frontend
npm install
cp .env.example .env   # VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

Open `http://localhost:5173`. Either way, the backend must allow the frontend's origin in CORS — the
root `.env`'s `CORS_ORIGINS` includes both `http://localhost:5173` and `http://localhost` by default.

## 9. Production Build & EC2 Deployment

The frontend now has its own `frontend/Dockerfile`: a multi-stage build that runs `npm run build`
in a Node image, then copies the resulting `dist/` into an `nginx:alpine` image (`frontend/nginx.conf`
adds the SPA fallback `try_files $uri $uri/ /index.html`, so client-side routes like
`/appointment-confirmation/3` work on refresh/direct access, not just on in-app navigation).
`docker-compose.yml` builds and runs this as the `frontend` service (port 80), alongside `api` and `db`.

**Important Vite constraint:** `VITE_API_BASE_URL` is compiled into the built JS at *image build
time* — it cannot be changed by setting a container env var at runtime like a normal backend
setting. It's passed as a Docker Compose **build arg**, sourced from the root `.env`.

To deploy both frontend and backend together on one EC2 instance, edit the root `.env` on the host
before building:

```env
VITE_API_BASE_URL=http://EC2_PUBLIC_IP:8000
CORS_ORIGINS=http://localhost:5173,http://localhost,http://EC2_PUBLIC_IP,http://EC2_PUBLIC_IP:80
```

then `docker compose up --build -d`. See the README's [Deploying to EC2](README.md#deploying-to-ec2)
section for the full walkthrough (security group ports, verification steps). If either value changes
later, it requires a rebuild (`--build`), not just a restart — one is baked into the JS bundle, the
other is only read at container start.

## 10. Backend Changes Made to Support the Frontend

Kept intentionally minimal, per the "don't rewrite the backend" constraint:

- **CORS middleware** (`app/main.py`) — was entirely absent before; added with an env-driven
  `CORS_ORIGINS` setting (`app/config.py`), defaulting to `http://localhost:5173`.
- **`GET /appointment-requests/` (admin-only, new)** — the backend previously only exposed
  `GET /appointment-requests/me` (current user's own requests). There was no way for an admin to
  discover *which* request IDs exist to `PATCH` their status, so the Admin page had nothing to
  manage. This is a purely additive, admin-gated endpoint reusing the existing
  `AppointmentRequestOut` schema — it does not change any existing contract.
- **`Settings` now ignores unrecognized env vars** (`app/config.py`, `extra = "ignore"`) — needed
  once `VITE_API_BASE_URL` was added to the shared root `.env` for the Compose frontend build arg.
  Without this, `api` failed to start: pydantic's `Settings` rejects any env var it doesn't declare
  by default, and `api`'s `env_file: .env` loads every var in that file into its environment,
  `VITE_API_BASE_URL` included. This was caught by actually running `docker compose up --build`
  and watching the `api` container exit — `docker ps` silently omitting `api` (instead of showing
  it as failed/restarting) was the first sign something was wrong.

No endpoint request/response shapes changed.

## 11. Appointment Confirmation Page

After a successful `POST /appointment-requests`, `ProviderDetailPage` no longer shows an inline
success message — it navigates to `/appointment-confirmation/:appointmentId`, passing the created
appointment (the full `POST` response, including nested `slot` and `status`) and the provider's name
via React Router **navigation state** (`navigate(path, { state: {...} })`). Booking *errors* (404,
409, etc.) still render inline on the provider page — only success triggers navigation, so the 409
double-booking demo still works exactly as before.

No backend change was needed for this: there is no `GET /appointment-requests/{id}` endpoint, but the
`POST` response already contains everything the confirmation page shows (provider is looked up
client-side from data already loaded on the detail page).

**Refresh/direct-access handling:** navigation state doesn't survive a hard refresh or a bookmarked/
shared URL. The confirmation page checks that `location.state.appointment.id` matches the `:appointmentId`
route param; if it's missing or mismatched, it shows a "Confirmation not available" message explaining
the request was still saved, with a button to My Appointments — no attempt to refetch by ID, since
that endpoint doesn't exist and adding one for a one-off confirmation view wasn't worth a backend change.

**Button target naming:** the task description referenced `/my-appointments` and `/providers` as the
button targets; the app's actual existing routes are `/appointments` and `/` (provider list already
lives at `/`). The buttons are labeled "View My Appointments" / "Find More Providers" but point at
those real routes rather than introducing duplicate/renamed routes for no functional benefit.

## 12. Known Limitations / Future Improvements

- No pagination on provider list, my-appointments, or admin-appointments tables.
- Admin appointment table shows `provider_id`/`patient_id` as numbers (linked to the provider detail
  page) rather than resolved names — the backend's `AppointmentRequestOut` doesn't join those, and
  adding N+1 lookups client-side wasn't worth the complexity for a demo-scale dataset.
- No toast/notification system — errors and success messages are shown inline per-section, which is
  simple but means a user has to be looking at the right part of the page to notice them.
- No automated frontend test suite (e.g. Vitest/RTL) — verification for this milestone was done with
  a one-off Playwright script driving the running dev server end-to-end (list → filter → login →
  detail → book → conflict → admin update → access control), not committed to the repo.
- No dark mode / theming — single light healthcare-style palette (muted teal/green, generous
  whitespace), loosely inspired by real provider-matching sites' warm-but-professional tone, not a
  copy of any specific site's branding or components.
- `VITE_API_BASE_URL` is baked in at build time, not a runtime setting — pointing an already-built
  frontend image at a different backend requires a full `docker compose up --build`, not just an env
  var change or container restart. Fine for a single-EC2-instance class demo; a production setup
  would more likely serve the app behind a reverse proxy and use relative API paths instead.
