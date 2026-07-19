# Project Status

_Last updated: 2026-07-19_

## 1. Current Project Overview

Foresight Provider Match API is a backend MVP for a healthcare provider matching and appointment
request system, inspired by [Foresight Health](https://foresighthealth.com). Patients can browse
mental health providers, get ranked matches based on their needs, and book real appointment slots.
Admins review and manage appointment requests.

## 2. Business Domain and Selected Business Need

**Domain:** Mental health provider discovery and appointment scheduling.

**Selected business need:** Provider matching and appointment request management — patients find
providers suited to their needs, book a concrete appointment slot, and track request status. Admins
approve/decline requests on behalf of providers.

## 3. Current Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | FastAPI |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT (python-jose) + bcrypt |
| Dependency management | uv |
| Containerization | Docker + Docker Compose |
| Migrations | None — `Base.metadata.create_all` on startup (no Alembic; acceptable since there is no production data to preserve) |

## 4. Current Project Structure

```
app/
├── main.py          # FastAPI app, lifespan (create_all + seed)
├── config.py        # Settings loaded from .env
├── database.py      # SQLAlchemy engine and session
├── models.py         # ORM models
├── schemas.py        # Pydantic request/response schemas
├── auth.py           # Password hashing (bcrypt) and JWT creation/decoding
├── deps.py            # FastAPI dependencies: get_db, get_current_user, require_admin
├── seed.py            # Demo data seeded on first startup
└── routers/
    ├── auth.py          # /auth/register, /auth/login, /auth/me
    ├── providers.py     # /providers (summary), /providers/{id} (detail)
    ├── matches.py       # /provider-matches
    └── appointments.py  # /appointment-requests
```

## 5. Current Database Models and Relationships

| Model | Table | Key fields | Relationships |
|---|---|---|---|
| `User` | `users` | email, hashed_password, full_name, role (patient/admin) | has many `ProviderMatchRequest`, `AppointmentRequest` |
| `Provider` | `providers` | full_name, specialty, state, location, accepted_insurance, available_days (legacy text), accepting_new_patients, languages, bio, years_experience | has many `AppointmentSlot`, `AppointmentRequest` |
| `AppointmentSlot` | `appointment_slots` | provider_id (FK), start_time, end_time, is_available | belongs to `Provider`; has one `AppointmentRequest` (optional) |
| `ProviderMatchRequest` | `provider_match_requests` | patient_id (FK), state, insurance, concern, preferred_day | belongs to `User` |
| `AppointmentRequest` | `appointment_requests` | patient_id (FK), provider_id (FK), slot_id (FK, **unique**), reason, status | belongs to `User`, `Provider`, `AppointmentSlot` |

**Key constraints:**
- `appointment_slots.(provider_id, start_time)` — unique, prevents duplicate slot creation for the same provider/time.
- `appointment_requests.slot_id` — nullable + unique. Nullable so a slot reference can be detached when
  a request is declined/cancelled (multiple `NULL`s are allowed by Postgres unique constraints); unique
  so **at most one appointment request can ever hold a given slot at a time** — this is the concurrency guard.

## 6. Current API Endpoints

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `POST` | `/auth/register` | No | Create a new patient (or admin) account |
| `POST` | `/auth/login` | No | Log in, receive a JWT |
| `GET` | `/auth/me` | Bearer | Current user's profile |
| `GET` | `/providers` | No | List providers as **summary** cards; filters: state, insurance, specialty, accepting_new_patients |
| `GET` | `/providers/{id}` | No | Full provider **detail**, including upcoming available slots; 404 if not found |
| `POST` | `/provider-matches` | Bearer | Submit match preferences; returns providers (summary form) ranked by score |
| `POST` | `/appointment-requests` | Bearer | Book a specific `slot_id` for a `provider_id`; 404 (provider/slot missing), 409 (slot taken) |
| `GET` | `/appointment-requests/me` | Bearer | Current user's appointment requests |
| `GET` | `/appointment-requests` | Bearer (admin) | All appointment requests across all patients (added for the admin frontend page) |
| `PATCH` | `/appointment-requests/{id}/status` | Bearer (admin) | Update status; declining/cancelling releases the slot |
| `DELETE` | `/appointment-requests/{id}` | Bearer | Cancel own request (or any, if admin); releases the slot |
| `GET` | `/health` | No | Health check |

## 7. Provider Search Behavior

**Summary response** (`GET /providers`) — mirrors a real provider search results page: enough to decide
whether to click into a provider, not the full record.
```json
{
  "id": 1,
  "full_name": "Dr. Alice Kim",
  "specialty": "Anxiety & Depression",
  "state": "NY",
  "accepting_new_patients": true,
  "headline": "Specializing in CBT for anxiety and mood disorders.",
  "next_available_slot": "2026-07-20T09:00:00Z"
}
```

**Detail response** (`GET /providers/{id}`) — the full profile:
```json
{
  "id": 1,
  "full_name": "Dr. Alice Kim",
  "specialty": "Anxiety & Depression",
  "state": "NY",
  "location": "New York, NY",
  "accepted_insurance": "BlueCross, Aetna",
  "available_days": "Monday,Wednesday,Friday",
  "accepting_new_patients": true,
  "languages": "English, Korean",
  "bio": "Specializing in CBT for anxiety and mood disorders.",
  "years_experience": 12,
  "created_at": "...",
  "available_slots": [ { "id": 2, "provider_id": 1, "start_time": "...", "end_time": "...", "is_available": true }, ... ]
}
```

All existing filters (`state`, `insurance`, `specialty`, `accepting_new_patients`) still work unchanged
on `GET /providers`.

## 8. Appointment Availability Behavior

- `AppointmentSlot` is the source of truth for real, bookable time — not the old `available_days` text
  field (kept only as legacy/informational text on the provider detail response).
- Booking flow (`POST /appointment-requests`):
  1. Provider not found → `404`
  2. Slot not found (or belongs to a different provider) → `404`
  3. Slot found but `is_available=false` → `409`
  4. Otherwise: mark the slot unavailable and create the appointment request in the same transaction.
- Cancelling (`DELETE`) or the admin declining/cancelling (`PATCH status`) a request releases its slot
  (`is_available=true`, `slot_id` detached to `NULL`) so it becomes bookable again — this was a deliberate
  small addition beyond the literal ask, since otherwise a declined request would permanently lock a slot
  with no way to free it back up.
- Approving a request leaves the slot booked (no change).

## 9. Concurrency / Double-Booking Protection

The real guarantee is a **database-level unique constraint**, not an application-level check:

- `appointment_requests.slot_id` is `UNIQUE` at the schema level.
- The booking endpoint still does an `is_available` pre-check for a fast, friendly error — but that check
  alone has a race window under concurrent requests.
- The actual safety net: the `INSERT` of the new `AppointmentRequest` row is wrapped in a `try/except
  IntegrityError`. If two requests race for the same slot, only one `INSERT` can succeed; the database
  itself rejects the second with a uniqueness violation, which is caught and turned into a clean
  `409 Conflict` — `"This appointment slot has already been booked."`
- **Verified under real concurrency:** 5 simultaneous `POST /appointment-requests` calls against the same
  `slot_id` (fired in parallel, not sequentially) resulted in exactly one `201 Created` and four
  `409 Conflict` responses.

## 10. Demo Credentials

| Role | Email | Password |
|---|---|---|
| Admin | `admin@foresight.com` | `admin123` |
| Patient | `patient@example.com` | `patient123` |

## 11. Swagger Demo Checklist

Open `http://localhost:8000/docs` and verify:

- [ ] `GET /providers` returns summary fields only (no bio/insurance/full slot list)
- [ ] `GET /providers/1` returns full detail, including `available_slots`
- [ ] `POST /provider-matches` still ranks providers correctly (Dr. Alice Kim scores 11/11 for
      `{"state":"NY","insurance":"BlueCross","concern":"Anxiety","preferred_day":"Monday"}`)
- [ ] `POST /appointment-requests` with a real `slot_id` succeeds (`201`)
- [ ] That slot disappears from `GET /providers/{id}`'s `available_slots`
- [ ] Repeating the same booking returns `409 Conflict`
- [ ] Booking a non-existent `slot_id` returns `404`
- [ ] `GET /appointment-requests/me` shows the booked request
- [ ] Admin can `PATCH /appointment-requests/{id}/status`; a patient attempting the same gets `403`
- [ ] Declining/cancelling a request frees its slot back to `available_slots`

## 12. Known Limitations / Future Improvements

- No Alembic — schema changes require a fresh dev database (`docker compose down -v`); fine for an MVP/
  class project with no production data, but would need real migrations before going further.
- Slot generation in `seed.py` is fixed-date demo data, not a recurring schedule generator.
- No pagination on `/providers` or `/appointment-requests/me`.
- No provider portal — providers can't manage their own slots yet; only seeded/admin-controlled.
- No notifications (email/SMS) on status changes.
- `available_days` free-text field kept for legacy/informational display but is no longer used for any
  booking logic — could be removed in a later cleanup once it's no longer needed for display purposes.
