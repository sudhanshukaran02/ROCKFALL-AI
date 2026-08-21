import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure workspace root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.config import config
from backend.app.api.api_router import api_router

app = FastAPI(
    title="NER-LENS Scientific Decision-Support API",
    description=(
        "FastAPI Integration Layer for the North Eastern Region Landslide Early Warning & Risk Monitoring System. "
        "Wraps verified U-Net, SRTM DEM, PyTorch LSTM, and late-fusion ML pipeline."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for React frontend (Vite dev server & production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router under /api
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "NER-LENS FastAPI Integration Service Online",
        "documentation": "/docs",
        "system_status": "RESEARCH_DECISION_SUPPORT",
        "version": config.VERSION,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
