from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.kb import get_kb
from app.routers import identify, medicines
from app.store import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_kb()  # fail fast at startup if the data files are broken
    yield


app = FastAPI(title="MediClear API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"])
app.include_router(identify.router)
app.include_router(medicines.router)


@app.get("/api/health")
def health():
    kb = get_kb()
    return {"status": "ok", "drugs": len(kb.drugs), "brands": len(kb.brands)}

async def lifespan(app: FastAPI):
    get_kb()     # fail fast at startup if the data files are broken
    init_db()    # create tables if they don't exist
    yield