#!/usr/bin/env python3
"""
Generate REFERENCE_INDEX.yaml from enriched transcript files.

Scans all .md files in referencias_transcripts/, extracts YAML frontmatter,
and generates a consolidated index mapping doc_id -> metadata.

Usage:
    python tools/generate_reference_index.py \
        --transcripts referencias_transcripts/ \
        --output referencias_transcripts/REFERENCE_INDEX.yaml
"""

import argparse
import io
import re
import sys
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import yaml
except ImportError:
    yaml = None


def extract_frontmatter(file_path: Path) -> dict:
    """Extract YAML-like frontmatter from markdown file."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  [X] Could not read {file_path.name}: {e}", file=sys.stderr)
        return {}

    # Try to find YAML frontmatter between --- markers
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        # Try alternative: look for key: value pairs at top
        lines = content.split('\n')
        frontmatter_lines = []
        in_frontmatter = False
        for line in lines:
            if line.strip() == '---':
                if in_frontmatter:
                    break
                in_frontmatter = True
                continue
            if in_frontmatter:
                frontmatter_lines.append(line)

        if not frontmatter_lines:
            return {"_error": "no_frontmatter"}

        frontmatter_text = '\n'.join(frontmatter_lines)
    else:
        frontmatter_text = match.group(1)

    # Parse YAML if available
    if yaml:
        try:
            data = yaml.safe_load(frontmatter_text)
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    # Fallback: manual key-value parsing
    result = {}
    current_key = None
    current_list = None

    for line in frontmatter_text.split('\n'):
        stripped = line.strip()

        # Skip comments and empty lines
        if stripped.startswith('#') or not stripped:
            continue

        # Check for key: value
        kv_match = re.match(r'^(\w[\w_]*)\s*:\s*(.*)', stripped)
        if kv_match:
            key = kv_match.group(1)
            value = kv_match.group(2).strip()

            if value.startswith('[') and value.endswith(']'):
                # Inline list
                items = [v.strip().strip('"').strip("'") for v in value[1:-1].split(',') if v.strip()]
                result[key] = items
            elif value.startswith('|'):
                # Multiline string (skip for now, just mark)
                result[key] = "(multiline)"
                current_key = key
            elif value == '':
                # Might be start of list or nested
                current_key = key
                current_list = []
            elif value.lower() in ('true', 'false'):
                result[key] = value.lower() == 'true'
            elif value.replace('.', '').replace('-', '').isdigit():
                try:
                    result[key] = float(value) if '.' in value else int(value)
                except ValueError:
                    result[key] = value.strip('"').strip("'")
            else:
                result[key] = value.strip('"').strip("'")
            current_key = key
            current_list = None
            continue

        # Check for list item
        if stripped.startswith('- ') and current_key:
            item = stripped[2:].strip().strip('"').strip("'")
            if current_key not in result:
                result[current_key] = []
            if isinstance(result[current_key], list):
                result[current_key].append(item)
            continue

    return result


def get_transcript_path(file_path: Path, base_dir: Path) -> str:
    """Get relative path from base directory."""
    try:
        return str(file_path.relative_to(base_dir))
    except ValueError:
        return file_path.name


def generate_index(transcripts_dir: Path) -> dict:
    """Generate REFERENCE_INDEX from all transcript files."""
    documents = []
    by_taxonomy = {}
    quality_metrics = {
        "total": 0,
        "with_frontmatter": 0,
        "with_doc_id": 0,
        "with_title": 0,
        "with_topics": 0,
        "with_summary": 0,
        "needs_human_review": 0,
    }

    # Find all .md files
    md_files = sorted(transcripts_dir.rglob("*.md"))

    # Exclude index/report files
    md_files = [f for f in md_files if f.name not in (
        "REFERENCE_INDEX.yaml", "quality_report.md", "insights_consolidated.md"
    )]

    print(f"[.] Found {len(md_files)} transcript files")

    for file_path in md_files:
        quality_metrics["total"] += 1
        rel_path = get_transcript_path(file_path, transcripts_dir)

        print(f"  [.] Processing: {rel_path}")

        frontmatter = extract_frontmatter(file_path)

        if not frontmatter or "_error" in frontmatter:
            print(f"  [!] No frontmatter: {file_path.name}")
            doc_entry = {
                "transcript_file": rel_path,
                "status": "missing_frontmatter",
                "needs_review": True,
            }
            documents.append(doc_entry)
            quality_metrics["needs_human_review"] += 1
            continue

        quality_metrics["with_frontmatter"] += 1

        # Extract key fields
        doc_id = frontmatter.get("doc_id", "")
        title = frontmatter.get("title", frontmatter.get("titulo", ""))
        taxonomy = frontmatter.get("taxonomy", frontmatter.get("taxonomia", "unknown"))
        doc_type = frontmatter.get("doc_type", frontmatter.get("tipo", ""))
        topics = frontmatter.get("topics", frontmatter.get("topicos", []))
        clinical_relevance = frontmatter.get("clinical_relevance", frontmatter.get("relevancia_clinica", ""))
        source_file = frontmatter.get("source_file", frontmatter.get("arquivo_fonte", ""))
        pages_total = frontmatter.get("pages_total", frontmatter.get("paginas_total", 0))
        authors = frontmatter.get("authors", frontmatter.get("autores", []))
        year = frontmatter.get("year", frontmatter.get("ano", ""))
        summary = frontmatter.get("summary", frontmatter.get("resumo", ""))
        references_count = frontmatter.get("references_count", frontmatter.get("contagem_referencias", 0))
        target_audience = frontmatter.get("target_audience", frontmatter.get("publico_alvo", []))
        key_concepts = frontmatter.get("key_concepts", frontmatter.get("conceitos_chave", []))
        related_protocols = frontmatter.get("related_protocols", frontmatter.get("protocolos_relacionados", []))

        # Quality flags — needs_review only when explicitly flagged via dict schema
        quality_flags = frontmatter.get("quality_flags", {})
        needs_review = False
        if isinstance(quality_flags, dict):
            needs_review = quality_flags.get("needs_human_review", False)
        elif isinstance(quality_flags, list):
            # Legacy list schema: documented limitations, not review flags
            print(f"  [!] Legacy list schema: {rel_path}", file=sys.stderr)

        # Track metrics
        if doc_id:
            quality_metrics["with_doc_id"] += 1
        if title:
            quality_metrics["with_title"] += 1
        if topics:
            quality_metrics["with_topics"] += 1
        if summary and summary != "(multiline)":
            quality_metrics["with_summary"] += 1
        if needs_review:
            quality_metrics["needs_human_review"] += 1

        # Track taxonomy
        tax_key = str(taxonomy) if taxonomy else "unknown"
        if tax_key not in by_taxonomy:
            by_taxonomy[tax_key] = {"total": 0, "with_doc_id": 0}
        by_taxonomy[tax_key]["total"] += 1
        if doc_id:
            by_taxonomy[tax_key]["with_doc_id"] += 1

        doc_entry = {
            "doc_id": doc_id or f"MISSING-{quality_metrics['total']:03d}",
            "title": title or file_path.stem,
            "transcript_file": rel_path,
            "source_file": source_file,
            "taxonomy": tax_key,
            "doc_type": doc_type,
            "pages_total": pages_total,
            "authors": authors if isinstance(authors, list) else [authors] if authors else [],
            "year": year,
            "topics": topics if isinstance(topics, list) else [topics] if topics else [],
            "key_concepts": key_concepts if isinstance(key_concepts, list) else [],
            "related_protocols": related_protocols if isinstance(related_protocols, list) else [],
            "clinical_relevance": clinical_relevance,
            "target_audience": target_audience if isinstance(target_audience, list) else [target_audience] if target_audience else [],
            "references_count": references_count,
            "needs_review": needs_review,
        }

        documents.append(doc_entry)

    # Sort by doc_id
    documents.sort(key=lambda d: d.get("doc_id", "ZZZ"))

    index = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_documents": quality_metrics["total"],
            "generator": "tools/generate_reference_index.py",
            "project": "Protocolo SM Extrema 2026",
        },
        "summary": {
            "by_taxonomy": by_taxonomy,
            "quality_metrics": quality_metrics,
        },
        "documents": documents,
    }

    return index


def write_yaml_manual(data: dict, output_path: Path):
    """Write YAML without pyyaml dependency."""
    lines = []

    def write_value(value, indent=0):
        prefix = "  " * indent
        if isinstance(value, dict):
            for k, v in value.items():
                if isinstance(v, (dict, list)) and v:
                    lines.append(f"{prefix}{k}:")
                    if isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict):
                                lines.append(f"{prefix}  -")
                                for dk, dv in item.items():
                                    if isinstance(dv, list) and dv:
                                        lines.append(f"{prefix}    {dk}:")
                                        for li in dv:
                                            lines.append(f"{prefix}      - \"{li}\"")
                                    elif isinstance(dv, bool):
                                        lines.append(f"{prefix}    {dk}: {'true' if dv else 'false'}")
                                    elif isinstance(dv, (int, float)):
                                        lines.append(f"{prefix}    {dk}: {dv}")
                                    else:
                                        safe_val = str(dv).replace('"', '\\"')
                                        lines.append(f"{prefix}    {dk}: \"{safe_val}\"")
                            else:
                                safe_item = str(item).replace('"', '\\"')
                                lines.append(f"{prefix}  - \"{safe_item}\"")
                    else:
                        write_value(v, indent + 1)
                elif isinstance(v, bool):
                    lines.append(f"{prefix}{k}: {'true' if v else 'false'}")
                elif isinstance(v, (int, float)):
                    lines.append(f"{prefix}{k}: {v}")
                elif v is None or v == "" or v == []:
                    lines.append(f"{prefix}{k}: \"\"")
                else:
                    safe_val = str(v).replace('"', '\\"')
                    lines.append(f"{prefix}{k}: \"{safe_val}\"")

    lines.append("# REFERENCE_INDEX.yaml")
    lines.append(f"# Generated: {datetime.now().isoformat()}")
    lines.append(f"# Project: Protocolo SM Extrema 2026")
    lines.append("")

    write_value(data)

    output_path.write_text('\n'.join(lines), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description="Generate REFERENCE_INDEX.yaml")
    parser.add_argument("--transcripts", type=Path, required=True, help="Transcripts directory")
    parser.add_argument("--output", type=Path, help="Output YAML file")
    args = parser.parse_args()

    transcripts_dir = args.transcripts
    output_path = args.output or (transcripts_dir / "REFERENCE_INDEX.yaml")

    if not transcripts_dir.exists():
        print(f"Error: Directory not found: {transcripts_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"\n[.] Generating REFERENCE_INDEX from {transcripts_dir}")

    index = generate_index(transcripts_dir)

    # Write output
    if yaml:
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(index, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    else:
        write_yaml_manual(index, output_path)

    print(f"\n[>] REFERENCE_INDEX written to: {output_path}")
    print(f"    Total documents: {index['summary']['quality_metrics']['total']}")
    print(f"    With doc_id: {index['summary']['quality_metrics']['with_doc_id']}")
    print(f"    With title: {index['summary']['quality_metrics']['with_title']}")
    print(f"    Needs review: {index['summary']['quality_metrics']['needs_human_review']}")

    # Print taxonomy breakdown
    print(f"\n    By taxonomy:")
    for tax, counts in index['summary']['by_taxonomy'].items():
        print(f"      {tax}: {counts['total']} docs ({counts['with_doc_id']} with doc_id)")

    print()


if __name__ == "__main__":
    main()
