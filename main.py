from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from routers import auth, upload, pins, admin
from config import settings
from database import engine, Base
from models import *  # noqa – ensure all models are registered with Base

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allowed_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(pins.router)
app.include_router(admin.router)


@app.on_event("startup")
def on_startup():
    # We rely exclusively on Alembic for migrations now, not create_all.
    # Migrate existing users table: add is_superuser if missing
    inspector = inspect(engine)
    columns = [col["name"] for col in inspector.get_columns("users")]
    if "is_superuser" not in columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_superuser BOOLEAN DEFAULT FALSE NOT NULL"))


@app.get("/")
def root():
    return {"message": "Hello from backend!"}
