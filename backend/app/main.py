
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import Base, engine
from .seed import seed
from .routers import auth, students, rooms, stays, finance, complaints, ai, policies, contracts, stats

BASE = Path(__file__).resolve().parents[2]
BASE = Path(os.getenv("KTX_BASE_DIR", str(Path(__file__).resolve().parents[2])))
Base.metadata.create_all(engine)
seed()

app = FastAPI(title="KTX-AI API", version="1.0.0", description="Backend FastAPI + SQLite + AI + RAG nội quy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(rooms.router, prefix="/api/rooms", tags=["Rooms"])
app.include_router(stays.router, prefix="/api/stays", tags=["Stay"])
app.include_router(finance.router, prefix="/api/finance", tags=["Finance"])
app.include_router(complaints.router, prefix="/api/complaints", tags=["Complaints"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(policies.router, prefix="/api/policies", tags=["Policies"])
app.include_router(contracts.router, prefix="/api/contracts", tags=["Contracts"])
app.include_router(stats.router, prefix="/api/stats", tags=["Statistics"])

@app.get("/api/health")
def health():
    return {"status":"ok","service":"KTX-AI"}

# Serve existing frontend at the same origin.
app.mount("/css", StaticFiles(directory=str(BASE/"css")), name="css")
app.mount("/js", StaticFiles(directory=str(BASE/"js")), name="js")
app.mount("/sinhvien", StaticFiles(directory=str(BASE/"sinhvien"), html=True), name="sinhvien")
app.mount("/quanly", StaticFiles(directory=str(BASE/"quanly"), html=True), name="quanly")
app.mount("/ketoan", StaticFiles(directory=str(BASE/"ketoan"), html=True), name="ketoan")
app.mount("/", StaticFiles(directory=str(BASE), html=True), name="frontend")
