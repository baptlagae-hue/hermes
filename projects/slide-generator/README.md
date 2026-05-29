# Slide Generator

Generate Google Slides-compatible `.pptx` presentations from a **template** + **plan** + **content**.

## Philosophy

This tool does **not** design slides — it **respects** your template. You provide:

1. **A template** (`.pptx`) — a Google Slides file with your slide masters, layouts, colors, fonts, and icons
2. **A plan** (YAML) — the presentation's outline: what slides, in what order, what type
3. **Content** (YAML) — the text, quotes, data, and images to fill each slide

The output is a `.pptx` that opens cleanly in Google Slides, using your template's layouts exactly as defined.

## Installation

```bash
pip install -e .
```

Requires Python 3.10+.

## Usage

### 1. Explore your template

```bash
slide-generator layouts my-template.pptx
slide-generator info my-template.pptx
```

### 2. Create a plan

Write a `plan.yaml`:

```yaml
title: "Q3 Strategy Review"
slides:
  - title: "Cover"
    type: title
  - title: "Executive Summary"
    type: content
  - title: "Market Overview"
    type: section
  - title: "Key Metrics"
    type: data
  - title: "Client Testimonial"
    type: quote
  - title: "Next Steps"
    type: content
  - title: "Thank You"
    type: end
```

Available slide types: `title`, `section`, `content`, `quote`, `data`, `end`, `icons`

### 3. Generate a content template

```bash
slide-generator template my-template.pptx plan.yaml -o content.yaml
```

This creates a `content.yaml` scaffold you can fill in.

### 4. Fill in content

```yaml
slides:
  - slide_ref: "Executive Summary"
    text:
      - style: body
        bullets:
          - "Revenue up 23% YoY"
          - "3 new enterprise clients"
          - "Expanded to EU market"
    quotes:
      - text: "This has been our best quarter yet"
        author: "CEO"
    data:
      - title: "Quarterly Revenue"
        chart_type: "bar"
        unit: "M€"
        points:
          - label: "Q1"
            value: 12.5
          - label: "Q2"
            value: 15.3
```

### 5. Build the presentation

```bash
slide-generator build my-template.pptx plan.yaml content.yaml -o q3-review.pptx
```

Or without content (uses plan titles only):

```bash
slide-generator build my-template.pptx plan.yaml
```

### 6. Open in Google Slides

Upload the generated `.pptx` to Google Drive and open it in Google Slides — your template's masters and layouts are preserved.

## How it works

1. **Template parsing** — extracts all slide layouts, placeholders, theme colors, and fonts from your `.pptx`
2. **Layout matching** — for each slide, finds the best layout by type (title → title layout, data → chart layout, etc.)
3. **Content mapping** — fills each layout's placeholders with your content (text → title box, bullets → body, quotes → quote box)
4. **Clean output** — saves a `.pptx` with no reference to the original slides, only the master templates

### Layout type inference

The tool infers slide type from layout names:
- "Title", "Cover", "1_" → `title`
- "Section", "Divider" → `section`
- "Quote", "Testimonial" → `quote`
- "Data", "Chart", "Number" → `data`
- "End", "Closing", "Thank" → `end`
- "Icon", "Legend", "Gallery" → `icons`
- Everything else → `content`

## Project structure

```
slide-generator/
├── src/
│   ├── cli.py              # CLI entry point (click)
│   ├── template_parser.py   # .pptx DNA extraction
│   ├── plan_parser.py       # YAML/JSON plan reader
│   ├── content_parser.py    # YAML/JSON content reader
│   ├── slide_builder.py     # Orchestrator
│   └── renderers/
│       └── slides.py        # Per-type slide renderers
├── tests/
│   └── test_generator.py    # 15+ tests
├── requirements.txt
├── setup.py
├── README.md
└── DESIGN_DECISIONS.md
```
