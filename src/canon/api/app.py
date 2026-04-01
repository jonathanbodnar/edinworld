from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.canon.api.routes import actors, admin, chapters, events, places, timeline
from src.canon.config import settings

app = FastAPI(
    title="Edinworld Canon API",
    description="Canon & Living World-State Engine",
    version="0.1.0",
    root_path="/world-api",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chapters.router, prefix="/chapters", tags=["Chapters"])
app.include_router(actors.router, prefix="/actors", tags=["Actors"])
app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(places.router, prefix="/places", tags=["Places"])
app.include_router(timeline.router, prefix="/timeline", tags=["Timeline"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "edinworld-canon"}
