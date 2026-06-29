from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, providers, matches, appointments


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        from app.seed import seed
        seed()
    except Exception as e:
        import logging
        logging.warning(f"DB not available at startup: {e}")
    yield


app = FastAPI(
    title="Foresight Provider Match API",
    description="Backend MVP for mental health provider matching and appointment request management.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(providers.router)
app.include_router(matches.router)
app.include_router(appointments.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
