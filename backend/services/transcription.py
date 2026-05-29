import os
import tempfile
from faster_whisper import WhisperModel

_model = None


def get_whisper():
    global _model
    if _model is None:
        model_size = os.getenv("WHISPER_MODEL", "base")
        _model = WhisperModel(model_size, device="cpu", cpu_threads=4, num_workers=2)
    return _model


def transcribe(audio_data: bytes, language: str = "fr") -> str:
    model = get_whisper()
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(audio_data)
        tmp_path = tmp.name
    try:
        segments, info = model.transcribe(tmp_path, language=language, beam_size=5)
        text = " ".join(seg.text for seg in segments)
        return text.strip()
    finally:
        os.unlink(tmp_path)
