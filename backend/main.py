import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.voice import router as voice_router
from routes.interview import router as interview_router
from routes.spec import router as spec_router

app = FastAPI(title="Expertise Transfer Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice_router)
app.include_router(interview_router)
app.include_router(spec_router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
