from datetime import datetime, timedelta, timezone
from app.database import SessionLocal, engine, Base
from app import models
from app.auth import hash_password


def _upcoming_slots(days_ahead: list[int], hours: list[int]) -> list[tuple[datetime, datetime]]:
    """Build (start, end) 45-minute slot pairs on given weekday offsets/hours from tomorrow."""
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    slots = []
    for day_offset in days_ahead:
        day = now + timedelta(days=day_offset)
        for hour in hours:
            start = day.replace(hour=hour)
            slots.append((start, start + timedelta(minutes=45)))
    return slots


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(models.Provider).count() > 0:
        db.close()
        return

    admin = models.User(
        email="admin@foresight.com",
        hashed_password=hash_password("admin123"),
        full_name="Admin User",
        role=models.UserRole.admin,
    )
    patient = models.User(
        email="patient@example.com",
        hashed_password=hash_password("patient123"),
        full_name="Jane Doe",
        role=models.UserRole.patient,
    )

    providers = [
        models.Provider(
            full_name="Dr. Alice Kim",
            specialty="Anxiety & Depression",
            state="NY",
            location="New York, NY",
            accepted_insurance="BlueCross, Aetna",
            available_days="Monday,Wednesday,Friday",
            accepting_new_patients=True,
            languages="English, Korean",
            bio="Specializing in CBT for anxiety and mood disorders.",
            years_experience=12,
        ),
        models.Provider(
            full_name="Dr. Carlos Rivera",
            specialty="Trauma & PTSD",
            state="CA",
            location="Los Angeles, CA",
            accepted_insurance="United, Cigna",
            available_days="Tuesday,Thursday",
            accepting_new_patients=True,
            languages="English, Spanish",
            bio="Evidence-based trauma therapy with a compassionate approach.",
            years_experience=9,
        ),
        models.Provider(
            full_name="Dr. Sarah Chen",
            specialty="Child & Adolescent",
            state="WA",
            location="Seattle, WA",
            accepted_insurance="Aetna, Humana",
            available_days="Monday,Wednesday",
            accepting_new_patients=True,
            languages="English, Mandarin",
            bio="Helping children and teens navigate mental health challenges.",
            years_experience=7,
        ),
        models.Provider(
            full_name="Dr. Marcus Johnson",
            specialty="Depression & Bipolar",
            state="TX",
            location="Austin, TX",
            accepted_insurance="BlueCross, United",
            available_days="Thursday,Friday",
            accepting_new_patients=True,
            languages="English",
            bio="Integrative psychiatry for mood disorders and life transitions.",
            years_experience=15,
        ),
        models.Provider(
            full_name="Dr. Emily Nguyen",
            specialty="Anxiety & OCD",
            state="FL",
            location="Miami, FL",
            accepted_insurance="Aetna, Cigna",
            available_days="Monday,Tuesday,Wednesday",
            accepting_new_patients=True,
            languages="English, Vietnamese",
            bio="Exposure and response prevention therapy for OCD and anxiety.",
            years_experience=6,
        ),
        models.Provider(
            full_name="Dr. Robert Walsh",
            specialty="Trauma & PTSD",
            state="NY",
            location="Buffalo, NY",
            accepted_insurance="United, BlueCross",
            available_days="Wednesday,Thursday",
            accepting_new_patients=False,
            languages="English",
            bio="EMDR-certified therapist focused on trauma recovery.",
            years_experience=20,
        ),
        models.Provider(
            full_name="Dr. Priya Sharma",
            specialty="Anxiety & Depression",
            state="CA",
            location="San Francisco, CA",
            accepted_insurance="Aetna, BlueCross",
            available_days="Tuesday,Friday",
            accepting_new_patients=True,
            languages="English, Hindi",
            bio="Mindfulness-based therapy for anxiety and depressive disorders.",
            years_experience=10,
        ),
        models.Provider(
            full_name="Dr. James Okafor",
            specialty="Addiction & Substance Use",
            state="IL",
            location="Chicago, IL",
            accepted_insurance="Cigna, Humana",
            available_days="Monday,Thursday,Friday",
            accepting_new_patients=True,
            languages="English",
            bio="Motivational interviewing and evidence-based addiction counseling.",
            years_experience=11,
        ),
    ]

    db.add_all([admin, patient] + providers)
    db.commit()

    # Give every provider a handful of upcoming slots so the search/detail/booking
    # flow has real data to demo against. Robert Walsh (accepting_new_patients=False)
    # is deliberately left without slots to show that case too.
    slot_hours = [9, 14]
    for provider in providers:
        if provider.full_name == "Dr. Robert Walsh":
            continue
        for start, end in _upcoming_slots(days_ahead=[1, 2, 3, 4, 5], hours=slot_hours):
            db.add(
                models.AppointmentSlot(
                    provider_id=provider.id,
                    start_time=start,
                    end_time=end,
                    is_available=True,
                )
            )

    db.commit()
    db.close()
    print("Database seeded with demo users, providers, and appointment slots.")


if __name__ == "__main__":
    seed()
