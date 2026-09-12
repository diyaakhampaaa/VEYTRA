# VEYTRA

Intelligent Traffic Intelligence and Vehicle Tracking System.

## About

VEYTRA is an AI-assisted traffic intelligence platform designed to
detect, track, verify, and analyze vehicles across multiple cameras.

It combines vehicle detection, OCR, cross-camera tracking,
plate verification, traffic analytics, and simulation comparison
into one command center.

## Current Features

- Command Center dashboard
- Live traffic network visualization
- Camera monitoring
- Vehicle search by license plate
- Smart plate verification
- Traffic analytics
- Traffic alerts
- Simulation vs ground-truth comparison
- Real and simulated data badges

## Tech Stack

### Frontend
- React
- Vite
- Tailwind CSS

### Backend
- Python
- FastAPI
- Pydantic

## Running Locally

### Start the Backend

From the project root:

```bash
python -m uvicorn backend.main:app --reload