from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.detection import router as detection_router
from backend.routers.ocr import router as ocr_router
from backend.routers.tracking import router as tracking_router
from backend.routers.verification import router as verification_router
from backend.routers.analytics import router as analytics_router
from backend.routers.cameras import router as cameras_router
from backend.routers.vehicles import router as vehicles_router
from backend.routers.alerts import router as alerts_router
from backend.routers.simulation import router as simulation_router


app = FastAPI(
    title="VEYTRA API",
    description="City-wide vehicle and traffic intelligence platform",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================
# Allow the Vite development server to communicate with FastAPI.
# Vite may use either port 5173 or 5174 depending on availability.

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(detection_router)
app.include_router(ocr_router)
app.include_router(tracking_router)
app.include_router(verification_router)
app.include_router(analytics_router)
app.include_router(cameras_router)
app.include_router(vehicles_router)
app.include_router(alerts_router)
app.include_router(simulation_router)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "VEYTRA API is running",
        "status": "online",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "VEYTRA backend",
    }