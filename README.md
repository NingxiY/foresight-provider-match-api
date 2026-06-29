# Foresight Provider Match API

Backend MVP for mental health provider matching and appointment request management, inspired by [Foresight Health](https://foresighthealth.com).

---

## Project Overview

This project analyzes Foresight Health, a healthcare platform that connects patients with licensed mental health providers, and implements a production-style REST API backend. The API handles provider discovery, rule-based provider matching, and the full lifecycle of appointment requests.

---

## Website & Business Analysis

**Foresight Health** helps patients find and connect with mental health providers (therapists, psychiatrists, counselors) based on their location, insurance, and clinical needs.

**Key observations from the site:**

| Area | Finding |
|---|---|
| Users | Patients seeking mental health care; licensed providers; admin/support staff |
| Core need | Match patients to the right provider based on insurance, specialty, and availability |
| Pain point | Patients don't know which providers accept their insurance or have openings |
| Flow | Browse providers → Submit match preferences → Request appointment → Track status |
| Data sensitivity | Health information requires careful access control (admin vs. patient roles) |

---

## Selected Business Need

**Provider matching and appointment request management.**

Patients can find providers suited to their needs, request appointments, and track request status. Admins review and update appointment status on behalf of providers.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | FastAPI |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT (python-jose) + bcrypt |
| Dependency management | uv |
| Containerization | Docker + Docker Compose |

---

## Database Models

| Model | Table | Purpose |
|---|---|---|
| `User` | `users` | Registered users with a `patient` or `admin` role. Stores hashed password and profile. |
| `Provider` | `providers` | Mental health providers with specialty, state, insurance accepted, available days, and whether they are accepting new patients. |
| `ProviderMatchRequest` | `provider_match_requests` | A patient's submitted matching preferences (state, insurance, concern, preferred day). Linked to the patient user. |
| `AppointmentRequest` | `appointment_requests` | A patient's appointment request for a specific provider, with a preferred date, reason, and status (pending → approved/declined/cancelled). |

---

## Business Endpoints

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `POST` | `/auth/register` | No | Create a new patient (or admin) account |
| `POST` | `/auth/login` | No | Log in and receive a JWT access token |
| `GET` | `/auth/me` | Bearer | Return the currently authenticated user's profile |
| `GET` | `/providers` | No | List all providers; supports `?state=`, `?insurance=`, `?specialty=`, `?accepting_new_patients=` filters |
| `GET` | `/providers/{id}` | No | Get a single provider's detail; returns 404 if not found |
| `POST` | `/provider-matches` | Bearer | Submit match preferences; returns providers ranked by rule-based score |
| `POST` | `/appointment-requests` | Bearer | Create an appointment request for a provider; returns 404 if provider not found |
| `GET` | `/appointment-requests/me` | Bearer | Return only the current user's appointment requests |
| `PATCH` | `/appointment-requests/{id}/status` | Bearer (admin only) | Update appointment status; returns 403 if caller is not admin |
| `DELETE` | `/appointment-requests/{id}` | Bearer | Patient cancels their own request (403 for others); admin can delete any |
| `GET` | `/health` | No | Health check — returns `{"status": "ok"}` |

---

## Provider Match Scoring

When a patient submits match preferences, every provider is scored and results are returned ranked highest to lowest. Only providers with a score > 0 are returned.

| Criterion | Points |
|---|---|
| Provider's state matches patient's state | +3 |
| Patient's insurance is accepted | +3 |
| Patient's concern matches provider's specialty | +2 |
| Provider is accepting new patients | +2 |
| Patient's preferred day matches provider's available days | +1 |
| **Maximum possible score** | **11** |

---

## Authentication

The API uses **JWT Bearer token authentication**.

### Flow

1. **Register** — `POST /auth/register` with `email`, `password`, `full_name`, and optional `role` (`patient` or `admin`).
2. **Login** — `POST /auth/login` with `username` (email) and `password` as a form body. Returns `access_token`.
3. **Use the token** — Include `Authorization: Bearer <token>` in the request header for all protected endpoints.

### Roles

| Role | Capabilities |
|---|---|
| `patient` | Browse providers, submit match requests, create and cancel their own appointment requests |
| `admin` | All patient capabilities + update any appointment request status + delete any appointment request |

Passwords are hashed with **bcrypt**. Tokens expire after **60 minutes** (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env`).

---

## Environment Variables

Copy `.env.example` to `.env` before running locally.

```env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/foresight
SECRET_KEY=foresight-dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> **Note:** When running with Docker Compose, `DATABASE_URL` must use `db` as the hostname, not `localhost`. The `.env` file shipped with this project already has the correct value for Docker.

---

## Running Locally (without Docker)

Requires Python 3.12+ and a running PostgreSQL instance.

```bash
# Install uv if not already installed
pip install uv

# Install dependencies
uv sync

# Set up .env (update DATABASE_URL to point to your local Postgres)
cp .env.example .env

# Run the API
uv run uvicorn app.main:app --reload
```

The API will start at `http://localhost:8000`. The database tables and seed data are created automatically on first startup.

---

## Running with Docker Compose

Requires Docker Desktop.

```bash
# Build and start the API + PostgreSQL database
docker compose up --build
```

| Service | Port |
|---|---|
| FastAPI API | `http://localhost:8000` |
| Swagger UI | `http://localhost:8000/docs` |
| PostgreSQL | `localhost:5432` |

To stop and remove all containers and data:

```bash
docker compose down -v
```

---

## Demo Credentials

These accounts are seeded automatically on first startup.

| Role | Email | Password |
|---|---|---|
| Admin | `admin@foresight.com` | `admin123` |
| Patient | `patient@example.com` | `patient123` |

---

## Swagger Demo Flow

Open `http://localhost:8000/docs` and follow these steps:

### Step 1 — Browse providers (no login needed)

- `GET /providers` — see all 8 seeded providers
- `GET /providers?state=NY` — filter to New York providers
- `GET /providers?insurance=Aetna&accepting_new_patients=true` — combine filters
- `GET /providers/1` — view Dr. Alice Kim's full profile

### Step 2 — Register and log in

- `POST /auth/register` — create a new patient account
- `POST /auth/login` — log in with that account (use the form fields: `username` = email, `password`)
- Copy the `access_token` from the response
- Click **Authorize** (lock icon, top right of Swagger) and paste the token

### Step 3 — Submit a provider match

- `POST /provider-matches` with:
  ```json
  {
    "state": "NY",
    "insurance": "BlueCross",
    "concern": "Anxiety",
    "preferred_day": "Monday"
  }
  ```
- The response returns providers ranked by score. Dr. Alice Kim should score highest (11/11) for this input.

### Step 4 — Request an appointment

- `POST /appointment-requests` with:
  ```json
  {
    "provider_id": 1,
    "preferred_date": "2026-08-01",
    "reason": "Anxiety management support"
  }
  ```
- `GET /appointment-requests/me` — confirm the request appears with status `pending`

### Step 5 — Admin approves the request

- Log out of the patient account (click Authorize → Logout)
- `POST /auth/login` as `admin@foresight.com` / `admin123`
- Authorize with the admin token
- `PATCH /appointment-requests/1/status` with `{"status": "approved"}`
- Try the same PATCH as a patient — observe the `403 Forbidden` response

### Step 6 — Cancel and delete

- Log back in as the patient
- `DELETE /appointment-requests/1` — patient cancels their own request (204)
- Try to delete a request belonging to another user — observe `403 Forbidden`

---

## Project Structure

```
app/
├── main.py          # FastAPI app, lifespan (create_all + seed)
├── config.py        # Settings loaded from .env
├── database.py      # SQLAlchemy engine and session
├── models.py        # ORM models: User, Provider, ProviderMatchRequest, AppointmentRequest
├── schemas.py       # Pydantic request/response schemas
├── auth.py          # Password hashing (bcrypt) and JWT creation/decoding
├── deps.py          # FastAPI dependencies: get_db, get_current_user, require_admin
├── seed.py          # Demo data seeded on first startup
└── routers/
    ├── auth.py          # /auth/register, /auth/login, /auth/me
    ├── providers.py     # /providers, /providers/{id}
    ├── matches.py       # /provider-matches
    └── appointments.py  # /appointment-requests (CRUD + status)
```

---

## Future Improvements

| Area | Improvement |
|---|---|
| **Matching algorithm** | Weight by patient rating history, provider response rate, and distance (geocoding) rather than simple keyword matching |
| **Real availability** | Replace the `available_days` string with a structured availability calendar; check for existing appointments before accepting new ones |
| **HIPAA / privacy** | Encrypt PII at rest, enforce field-level access control, add audit logging for all record access and mutations |
| **Notifications** | Send email or SMS confirmation when an appointment is approved or declined (e.g. via SendGrid or Twilio) |
| **Provider portal** | Allow providers to manage their own availability, accept/decline directly, and view their schedule |
| **Pagination** | Add `limit`/`offset` query params to `/providers` and `/appointment-requests/me` for production-scale data |
