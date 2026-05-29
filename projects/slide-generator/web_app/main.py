#!/usr/bin/env python3
"""
Slide Generator — Web App (FastAPI)
Exposes the slide generator as a web app with file upload.
"""

import os
import sys
import json
import uuid
import tempfile
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Add src to path — absolute import style
SRC_DIR = str(Path(__file__).resolve().parent.parent / "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from slide_builder import SlideBuilder
from plan_parser import parse_plan_string
from content_parser import parse_content_string
from template_parser import parse_template

app = FastAPI(title="Slide Generator", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HERE = Path(__file__).resolve().parent
UPLOAD_DIR = HERE / "uploads"
TEMPLATES_DIR = HERE / "templates"
UPLOAD_DIR.mkdir(exist_ok=True)

# Ensure the static directory exists
STATIC_DIR = HERE / "static"
STATIC_DIR.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def index():
    html = (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@app.post("/api/generate")
async def generate(
    template: UploadFile = File(...),
    plan: UploadFile = File(...),
    content: Optional[UploadFile] = File(None),
):
    # Validate file extensions
    if not template.filename.endswith(".pptx"):
        raise HTTPException(400, "Le template doit être un fichier .pptx")

    if not (plan.filename.endswith((".yaml", ".yml", ".json"))):
        raise HTTPException(400, "Le plan doit être un fichier .yaml, .yml ou .json")

    # Save uploaded files
    session_id = uuid.uuid4().hex[:12]
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(exist_ok=True)

    template_path = session_dir / "template.pptx"
    plan_path = session_dir / "plan.yaml"
    content_path = session_dir / "content.yaml"

    try:
        # Write template
        with open(template_path, "wb") as f:
            f.write(await template.read())

        # Write plan
        plan_raw = (await plan.read()).decode("utf-8")
        plan_path.write_text(plan_raw, encoding="utf-8")

        # Parse plan
        plan_data = parse_plan_string(plan_raw)

        # Optional content
        content_data = None
        if content and content.filename:
            content_raw = (await content.read()).decode("utf-8")
            content_path.write_text(content_raw, encoding="utf-8")
            content_data = parse_content_string(content_raw)

        # Validate template
        dna = parse_template(template_path)
        if not dna.layouts:
            raise HTTPException(400, "Le template ne contient aucun layout exploitable")

        # Build presentation
        builder = SlideBuilder(template_path)
        output_name = f"{builder._safe_filename(plan_data.title) or 'presentation'}.pptx"
        output_path = builder.build(
            plan=plan_data,
            content=content_data,
            output_path=session_dir / output_name,
            include_icons_slide=True,
        )

        # Return the file
        return FileResponse(
            path=output_path,
            filename=output_name,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={
                "content-disposition": f'attachment; filename="{output_name}"'
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erreur de génération : {str(e)}")
    finally:
        # Clean up after 5 minutes (handled by tmp cleaner or keep for retry)
        pass


@app.post("/api/analyze")
async def analyze(template: UploadFile = File(...)):
    """Analyze a template and return its layout info."""
    if not template.filename.endswith(".pptx"):
        raise HTTPException(400, "Le template doit être un fichier .pptx")

    session_id = uuid.uuid4().hex[:8]
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(exist_ok=True)
    template_path = session_dir / "template.pptx"

    with open(template_path, "wb") as f:
        f.write(await template.read())

    try:
        dna = parse_template(template_path)
        return {
            "slide_width": round(dna.slide_width, 2),
            "slide_height": round(dna.slide_height, 2),
            "layouts": [
                {
                    "name": l.name,
                    "type": l.type,
                    "placeholders": len(l.placeholders),
                }
                for l in dna.layouts
            ],
            "theme": {
                "font_major": dna.theme.font_major,
                "font_minor": dna.theme.font_minor,
                "accent_colors": dna.theme.accent_colors[:5],
            },
            "shapes_count": len(dna.template_shapes),
        }
    except Exception as e:
        raise HTTPException(500, f"Erreur d'analyse : {str(e)}")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "slide-generator"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8012"))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port, log_level="info")
