"""
Content parser — structured content mapped to each slide in the plan.

The content file uses YAML (human-friendly) and maps content blocks
to slides by their title or index. Each slide can have multiple
content blocks (text, quote, data, image, list, chart).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any
from pathlib import Path

import yaml
import json


@dataclass
class TextBlock:
    """A text content block."""
    text: str
    style: str = "body"  # body, heading, subheading, bullet
    bullets: list[str] = field(default_factory=list)


@dataclass
class QuoteBlock:
    """A quote block."""
    text: str
    author: Optional[str] = None
    source: Optional[str] = None


@dataclass
class DataBlock:
    """A data / chart block."""
    title: str
    data_points: list[dict] = field(default_factory=list)
    chart_type: str = "bar"  # bar, line, pie, number
    unit: Optional[str] = None


@dataclass
class ImageBlock:
    """An image block."""
    path: Optional[str] = None  # local path (or None = chart-generated)
    caption: Optional[str] = None
    alt_text: Optional[str] = None


@dataclass
class ListBlock:
    """A bullet list block."""
    items: list[str] = field(default_factory=list)
    ordered: bool = False
    title: Optional[str] = None


@dataclass
class SlideContent:
    """All content for a single slide."""
    slide_ref: str  # title or index to match the plan
    title: Optional[str] = None  # optional override
    subtitle: Optional[str] = None
    text_blocks: list[TextBlock] = field(default_factory=list)
    quotes: list[QuoteBlock] = field(default_factory=list)
    data: list[DataBlock] = field(default_factory=list)
    images: list[ImageBlock] = field(default_factory=list)
    lists: list[ListBlock] = field(default_factory=list)
    notes: Optional[str] = None


@dataclass
class Content:
    """Complete content for a presentation."""
    slides: list[SlideContent] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


def parse_content(path: str | Path) -> Content:
    """Parse a content file (YAML or JSON)."""
    path = Path(path)
    raw = path.read_text(encoding="utf-8")

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError("Could not parse content file.")

    return _parse_content_data(data)


def parse_content_string(raw: str) -> Content:
    """Parse content from a raw string."""
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError("Could not parse content string.")
    return _parse_content_data(data)


def _parse_content_data(data: dict) -> Content:
    if not isinstance(data, dict):
        raise ValueError("Content must be a dictionary.")

    slides_raw = data.get("slides", [])
    if not isinstance(slides_raw, list):
        raise ValueError("'slides' must be a list.")

    slides = []
    for i, entry in enumerate(slides_raw):
        if not isinstance(entry, dict):
            raise ValueError(f"Slide content {i}: must be a dictionary.")

        text_blocks = []
        for tb in entry.get("text", []):
            text_blocks.append(TextBlock(
                text=tb.get("text", ""),
                style=tb.get("style", "body"),
                bullets=tb.get("bullets", []),
            ))

        quotes = []
        for q in entry.get("quotes", []):
            quotes.append(QuoteBlock(
                text=q.get("text", ""),
                author=q.get("author"),
                source=q.get("source"),
            ))

        data_blocks = []
        for d in entry.get("data", []):
            data_blocks.append(DataBlock(
                title=d.get("title", ""),
                data_points=d.get("points", []),
                chart_type=d.get("chart_type", "bar"),
                unit=d.get("unit"),
            ))

        images = []
        for img in entry.get("images", []):
            images.append(ImageBlock(
                path=img.get("path"),
                caption=img.get("caption"),
                alt_text=img.get("alt_text"),
            ))

        lists = []
        for lst in entry.get("lists", []):
            lists.append(ListBlock(
                items=lst.get("items", []),
                ordered=lst.get("ordered", False),
                title=lst.get("title"),
            ))

        slides.append(SlideContent(
            slide_ref=entry.get("slide_ref", str(i)),
            title=entry.get("title"),
            subtitle=entry.get("subtitle"),
            text_blocks=text_blocks,
            quotes=quotes,
            data=data_blocks,
            images=images,
            lists=lists,
            notes=entry.get("notes"),
        ))

    return Content(slides=slides)


def content_from_template(dna, plan):
    """
    Generate a content template file based on the plan.
    Useful as a starting point — fill in your content.
    """
    template = {"slides": []}
    for slide in plan.slides:
        entry = {"slide_ref": slide.title, "type": slide.type}

        # Suggest placeholders based on slide type
        if slide.type == "title":
            entry["subtitle"] = "Enter subtitle here"
        elif slide.type == "content":
            entry["text"] = [
                {"style": "body", "bullets": ["First bullet point", "Second bullet point"]}
            ]
        elif slide.type == "quote":
            entry["quotes"] = [{"text": "Quote text", "author": "Author name"}]
        elif slide.type == "data":
            entry["data"] = [
                {"title": "Metric", "chart_type": "bar",
                 "points": [{"label": "Item A", "value": 42}]}
            ]
        elif slide.type == "section":
            entry["subtitle"] = "Section description"

        template["slides"].append(entry)

    return yaml.dump(template, default_flow_style=False, allow_unicode=True, sort_keys=False)
