from fastapi import FastAPI

from app.api.event_routes import router as event_router


app = FastAPI(
    title="GuardX Backend",
    description="Context-Aware AI Safety and Response System",
    version="0.1.0"
)

app.include_router(event_router)


@app.get("/")
def root():
    return {
        "message": "GuardX backend is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }