# DESIGN DECISIONS

This file documents choices made during development where the user's input was
ambiguous or left to the developer's discretion.

## 1. Plan format → YAML

**Decision:** YAML, not JSON or Markdown.

**Reason:** The user said "un humain donne le plan" — YAML is the most human-readable
structured format. No brackets, no commas, easy commenting. JSON works too (in case
a machine generates it), but YAML is the default.

## 2. Content format → YAML with `slide_ref` matching

**Decision:** Content is mapped to slides via `slide_ref` (the slide title from the plan).

**Reason:** The user said "à toi de proposer la meilleure solution". Matching by title
is the most intuitive: you don't need to count indices. If titles are duplicated, the
user can use a unique label as `slide_ref`.

## 3. Self-contained slides (no LLM enrichment)

**Decision:** The tool places content as-is, it does not generate or enhance it.

**Reason:** The user said "le contenu te sera donné à l'oral et il faudra l'enrichir"
— this enrichment happens *upstream* (when Hermes structures raw input into the
content.yaml). The tool itself is deterministic: garbage in, garbage out.

## 4. Multi-content per slide

**Decision:** A slide can have text + quotes + data simultaneously, as long as
the layout has enough placeholders.

**Reason:** The user confirmed "oui ça peut avoir, si c'est cohérent". The renderers
iterate all placeholders and fill them in priority order: title → subtitle → body → other.

## 5. Chart rendering → text-based tables, not native charts

**Decision:** Data points are rendered as formatted text in body placeholders.

**Reason:** Native chart objects in python-pptx require Excel data workbooks and
are fragile across different Google Slides versions. Text-based data representation
is deterministic, portable, and always works. The user can replace it with native
Google Sheets charts in Google Slides after import.

## 6. Icons reference slide

**Decision:** Added at the end of every presentation, showing all shapes found
in the template with their type, dimensions, and positions.

**Reason:** The user explicitly requested "une slide avec toutes les icônes" (#10).
It helps the user verify that template assets were correctly extracted.

## 7. CLI-first, no web UI (for now)

**Decision:** Pure CLI with Click. No Flask/Streamlit.

**Reason:** The user said "commence avec la CLI". A web UI can be added later in v2.

## 8. Python 3.10+ with python-pptx

**Decision:** Python 3.10+ target, `python-pptx` for .pptx parsing and generation.

**Reason:** python-pptx is the most mature library for reading and writing .pptx files.
It handles slide masters, layouts, placeholders, and theme extraction natively.

## 9. Slide dimension preservation

**Decision:** The output uses the template's slide dimensions untouched.

**Reason:** The user said "tu ne dois pas utiliser autre chose que ces slides master
et layouts". The output inherits everything from the template.

## 10. Auto-naming output files

**Decision:** Output filename is derived from the plan's title (sanitized).

**Reason:** The user said "trouve un nom adapté à la présentation". Using the plan
title gives a meaningful name without requiring extra input.

## 11. Layout fallback chain

**Decision:**
1. Exact type match (title → title layout)
2. Name keyword match (title → any layout with "title" or "cover" in name)
3. First layout in the template

**Reason:** Not every template will name its layouts in a predictable way. The
fallback chain ensures something always renders.

## 12. Custom shapes (non-placeholder elements)

**Decision:** The tool preserves all non-placeholder shapes from the template
(icons, backgrounds, decorative elements) by keeping the slide layout structure.
For truly custom shapes beyond the layout, the user should add them in Google
Slides after generation.

**Reason:** The user said "tu pourras créer des formes si c'est nécessaire" but
this is complex to implement generically. The layout approach already preserves
all template icons and shapes. Additional decorative shapes on slides can be
added manually — this is the most reliable approach.
