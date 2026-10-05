import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config import PRESET_SAREES_DIR, BASE_DIR
from api.routes import router as api_router, get_predictor

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Server] Starting Color-Invariant Saree Recognition Inference Engine...")
    # Pre-warm model and similarity index
    try:
        get_predictor()
        print("[Server] Model and similarity index pre-warmed successfully.")
    except Exception as e:
        print(f"[Server Warning] Cold start pre-warming deferred: {e}")
    yield
    print("[Server] Shutting down...")

app = FastAPI(
    title="Color-Invariant Saree Design Recognition API",
    description="Deep Learning API for recognizing saree motifs, weaves, and borders independent of color.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount preset sarees and sample assets directory for direct thumbnail and image access
PRESET_SAREES_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/presets", StaticFiles(directory=str(PRESET_SAREES_DIR)), name="presets")

samples_dir = BASE_DIR / "frontend" / "public" / "saree_samples"
if samples_dir.exists():
    app.mount("/saree_samples", StaticFiles(directory=str(samples_dir)), name="saree_samples")

# Mount API routes
app.include_router(api_router)

# Mount frontend build if available
dist_dir = BASE_DIR / "frontend" / "dist"
if dist_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(dist_dir / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = dist_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(dist_dir / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=False)
