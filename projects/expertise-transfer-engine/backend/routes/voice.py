import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schema import RecordingResponse

router = APIRouter(prefix="/api")

# Store transcripts in memory for MVP
_sessions: dict = {}

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/record", response_model=RecordingResponse)
async def record_audio(file: UploadFile = File(...)):
    from services.transcription import transcribe

    session_id = str(uuid.uuid4())[:8]
    audio_data = await file.read()

    if not audio_data:
        raise HTTPException(400, "Empty audio file")

    transcript = transcribe(audio_data, language="fr")

    _sessions[session_id] = {
        "transcript": transcript,
        "qa_pairs": [],
        "answers_context": "",
    }

    return RecordingResponse(session_id=session_id, transcript=transcript)
