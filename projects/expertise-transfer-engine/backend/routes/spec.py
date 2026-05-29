import re
from fastapi import APIRouter, HTTPException
from models.schema import SpecResponse, SpecSection

router = APIRouter(prefix="/api")

from routes.voice import _sessions


@router.get("/spec/{session_id}", response_model=SpecResponse)
async def generate_spec(session_id: str):
    from services.llm import generate_spec

    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    transcript = session["transcript"]
    qa_pairs = session.get("qa_pairs", [])

    if not qa_pairs:
        raise HTTPException(400, "No Q&A data yet — answer some questions first")

    markdown = generate_spec(transcript, qa_pairs)

    # Split markdown into sections by headers
    sections = []
    lines = markdown.split("\n")
    current_title = "Introduction"
    current_content = []

    for line in lines:
        header_match = re.match(r"^#{1,3}\s+(.+)$", line)
        if header_match:
            if current_content:
                sections.append(SpecSection(
                    title=current_title,
                    content="\n".join(current_content).strip(),
                ))
            current_title = header_match.group(1).strip()
            current_content = []
        else:
            current_content.append(line)

    if current_content:
        sections.append(SpecSection(
            title=current_title,
            content="\n".join(current_content).strip(),
        ))

    return SpecResponse(
        session_id=session_id,
        sections=sections,
        raw_markdown=markdown,
    )


@router.get("/spec/{session_id}/export")
async def export_spec(session_id: str):
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    from services.llm import generate_spec
    markdown = generate_spec(session["transcript"], session.get("qa_pairs", []))

    return {"markdown": markdown}
