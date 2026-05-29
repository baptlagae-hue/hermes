#!/usr/bin/env python3
"""
Slide Generator CLI — generate Google Slides-compatible .pptx from template + plan + content.

Usage:
  slide-generator init <template.pptx> <plan.yaml>    # Init a new project
  slide-generator build <template.pptx> <plan.yaml> [content.yaml]  # Build presentation
  slide-generator layouts <template.pptx>              # List available layouts
  slide-generator template <content.yaml> <plan.yaml>  # Generate content template from plan

Examples:
  slide-generator build my-template.pptx plan.yaml content.yaml -o output.pptx
  slide-generator layouts my-template.pptx
  slide-generator template plan.yaml > content.yaml
"""

from __future__ import annotations

import sys
import json
from pathlib import Path
from typing import Optional

import click

from .template_parser import parse_template, list_layouts
from .plan_parser import parse_plan
from .content_parser import parse_content, content_from_template
from .slide_builder import SlideBuilder


@click.group()
def cli():
    """Slide Generator — generate Google Slides from template + plan + content."""
    pass


@cli.command()
@click.argument("template_path", type=click.Path(exists=True, dir_okay=False))
def layouts(template_path):
    """List all available layouts in a template."""
    try:
        result = list_layouts(template_path)
        click.echo(f"\nTemplate: {template_path}")
        click.echo(f"Found {len(result)} layouts:\n")

        for i, layout in enumerate(result):
            click.echo(f"  [{i}] {layout['name']}  (inferred: {layout['type']})")
            if layout["ph_details"]:
                click.echo(f"       Placeholders: {layout['placeholders']}")
                for ph in layout["ph_details"]:
                    click.echo(f"         - {ph['name']} ({ph['type']})")
            else:
                click.echo(f"       No placeholders (blank layout)")
            click.echo()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("template_path", type=click.Path(exists=True, dir_okay=False))
@click.argument("plan_path", type=click.Path(exists=True, dir_okay=False))
@click.argument("content_path", type=click.Path(exists=True, dir_okay=False), required=False)
@click.option("--output", "-o", type=click.Path(), help="Output .pptx path")
@click.option("--no-icons", is_flag=True, help="Skip the icons reference slide")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed build info")
def build(template_path, plan_path, content_path, output, no_icons, verbose):
    """Build a presentation from template + plan + optional content."""
    try:
        plan = parse_plan(plan_path)
        if verbose:
            click.echo(f"Plan loaded: {plan.title} ({len(plan.slides)} slides)")

        content = None
        if content_path:
            content = parse_content(content_path)
            if verbose:
                click.echo(f"Content loaded: {len(content.slides)} slide entries")

        builder = SlideBuilder(template_path)

        if verbose:
            dna = builder.dna
            click.echo(f"Template DNA: {dna.slide_width:.1f}x{dna.slide_height:.1f}in")
            click.echo(f"  Layouts: {len(dna.layouts)}")
            click.echo(f"  Theme font: {dna.theme.font_minor or dna.theme.font_major or 'N/A'}")
            click.echo()

        output_path = builder.build(
            plan=plan,
            content=content,
            output_path=output,
            include_icons_slide=not no_icons,
        )

        click.echo(f"\n✅ Presentation generated: {output_path.resolve()}")

    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument("template_path", type=click.Path(exists=True, dir_okay=False))
@click.argument("plan_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--output", "-o", type=click.Path(), help="Output content template path")
def template(template_path, plan_path, output):
    """Generate a content template YAML from a plan, ready to fill in."""
    try:
        dna = parse_template(template_path)
        plan = parse_plan(plan_path)
        content_yaml = content_from_template(dna, plan)

        if output:
            Path(output).write_text(content_yaml, encoding="utf-8")
            click.echo(f"Content template saved to: {output}")
        else:
            click.echo(content_yaml)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("template_path", type=click.Path(exists=True, dir_okay=False))
def info(template_path):
    """Show detailed info about a template."""
    try:
        dna = parse_template(template_path)
        click.echo(f"\n📐 Template Info")
        click.echo(f"   Dimensions: {dna.slide_width:.1f} × {dna.slide_height:.1f} inches")
        click.echo(f"   Slides in template: {dna.slide_count}")
        click.echo(f"   Layouts: {len(dna.layouts)}")

        if dna.theme.font_major:
            click.echo(f"   Heading font: {dna.theme.font_major}")
        if dna.theme.font_minor:
            click.echo(f"   Body font: {dna.theme.font_minor}")
        if dna.theme.accent_colors:
            click.echo(f"   Theme colors: {', '.join(dna.theme.accent_colors[:5])}")

        click.echo(f"\n📋 Layouts ({len(dna.layouts)}):")
        for i, layout in enumerate(dna.layouts):
            emoji_map = {
                "title": "🏠", "section": "📂", "content": "📄",
                "quote": "💬", "data": "📊", "end": "👋", "icons": "🎨",
            }
            emoji = emoji_map.get(layout.type, "📄")
            click.echo(f"  {emoji} [{i}] {layout.name} ({layout.type})")

        click.echo(f"\n📦 Template shapes: {len(dna.template_shapes)}")
        icon_count = sum(1 for s in dna.template_shapes if "icon" in s.name.lower())
        if icon_count:
            click.echo(f"   Likely icons: {icon_count}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
