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


app = FastAPI(title="VEYTRA API")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Routers
app.include_router(detection_router)
app.include_router(ocr_router)
app.include_router(tracking_router)
app.include_router(verification_router)
app.include_router(analytics_router)
app.include_router(cameras_router)
app.include_router(vehicles_router)
app.include_router(alerts_router)
app.include_router(simulation_router)


# Root endpoint
@app.get("/")
def root():
    return {
        "message": "VEYTRA API is running"
    }


# Health check
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "VEYTRA backend"
    }