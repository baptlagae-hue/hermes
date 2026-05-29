"""
Plan parser — read a structured plan (YAML or JSON) that defines the slide outline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import json
from pathlib import Path

import yaml


@dataclass
class SlideEntry:
    """A single slide in the plan."""
    title: str
    type: str  # title, section, content, quote, data, end, icons
    subtitle: Optional[str] = None
    notes: Optional[str] = None  # speaker notes
    layout_hint: Optional[str] = None  # hint about which layout to use


@dataclass
class Plan:
    """Complete presentation plan."""
    title: str
    subtitle: Optional[str] = None
    author: Optional[str] = None
    slides: list[SlideEntry] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


def parse_plan(path: str | Path) -> Plan:
    """
    Parse a plan file (YAML or JSON) into a Plan object.

    Expected YAML format:
    ```yaml
    title: "My Presentation"
    subtitle: "Optional subtitle"
    author: "Baptiste"
    slides:
      - title: "Cover"
        type: title
      - title: "Agenda"
        type: content
      - title: "Market Overview"
        type: section
      - title: "Key Metrics"
        type: data
      - title: "Client Quote"
        type: quote
      - title: "Thank You"
        type: end
    ```

    For JSON:
    ```json
    {
      "title": "My Presentation",
      "slides": [...]
    }
    ```
    """
    path = Path(path)
    raw = path.read_text(encoding="utf-8")

    # Try YAML first, then JSON
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError(
                f"Could not parse {path}: not valid YAML or JSON. "
                "Use YAML for human-readable plans."
            )

    return _parse_plan_data(data)


def parse_plan_string(raw: str) -> Plan:
    """Parse a plan from a raw string (YAML or JSON)."""
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError("Could not parse plan string: not valid YAML or JSON.")
    return _parse_plan_data(data)


def _parse_plan_data(data: dict) -> Plan:
    if not isinstance(data, dict):
        raise ValueError("Plan must be a dictionary.")

    slides_raw = data.get("slides", [])
    if not isinstance(slides_raw, list):
        raise ValueError("'slides' must be a list.")

    slides = []
    valid_types = {"title", "section", "content", "quote", "data", "end", "icons"}

    for i, entry in enumerate(slides_raw):
        if not isinstance(entry, dict):
            raise ValueError(f"Slide {i}: must be a dictionary, got {type(entry).__name__}")

        slide_type = entry.get("type", "content")
        if slide_type not in valid_types:
            raise ValueError(
                f"Slide {i} ('{entry.get('title', '?')}'): invalid type '{slide_type}'. "
                f"Valid: {', '.join(sorted(valid_types))}"
            )

        slides.append(SlideEntry(
            title=entry.get("title", f"Slide {i+1}"),
            type=slide_type,
            subtitle=entry.get("subtitle"),
            notes=entry.get("notes"),
            layout_hint=entry.get("layout"),
        ))

    if not slides:
        raise ValueError("Plan must have at least one slide.")

    if slides[0].type != "title":
        slides.insert(0, SlideEntry(
            title=data.get("title", slides[0].title),
            type="title",
            subtitle=data.get("subtitle"),
        ))

    return Plan(
        title=data.get("title", slides[0].title),
        subtitle=data.get("subtitle"),
        author=data.get("author"),
        slides=slides,
        metadata={k: v for k, v in data.items() if k not in ("slides", "title", "subtitle", "author")},
    )
