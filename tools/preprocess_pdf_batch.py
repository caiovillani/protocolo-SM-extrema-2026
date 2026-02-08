#!/usr/bin/env python3
"""
Batch PDF Preprocessing Tool - Phase 1

Processa lote de PDFs extraindo texto, tabelas e metadados de forma determinística.
Gera arquivos .md preliminares com validação técnica para Phase 2 (PIPS semantic enrichment).

Usage:
    python tools/preprocess_pdf_batch.py \\
        --input referencias/ \\
        --output referencias_preprocessed/ \\
        --exclude archive Licitacoes_Compras_e_Contratos \\
        --concurrency 4
"""

import argparse
import hashlib
import io
import json
import sys
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Fix Windows console encoding for UTF-8 filenames
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber not installed. Run: pip install pdfplumber>=0.10", file=sys.stderr)
    sys.exit(1)

# Import shared utilities (will create in src/context_engine/pdf_utils.py)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from context_engine.pdf_utils import (
    detect_ocr_needed,
    extract_tables_pdfplumber,
    format_preliminary_markdown,
    validate_preliminary_extraction,
    extract_taxonomy_from_path,
    infer_doc_type,
    MarkdownTable,
    ProcessingResult,
    ValidationResult
)


def get_page_count(pdf_path: Path) -> int:
    """Retorna número de páginas do PDF."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            return len(pdf.pages)
    except Exception as e:
        print(f"Warning: Could not get page count for {pdf_path}: {e}", file=sys.stderr)
        return 0


def compute_md5(file_path: Path) -> str:
    """Calcula MD5 hash do arquivo."""
    md5_hash = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    except Exception as e:
        print(f"Warning: Could not compute MD5 for {file_path}: {e}", file=sys.stderr)
        return "unknown"


def extract_text_native(pdf_path: Path) -> str:
    """Extrai texto de PDF text-based usando pdfplumber."""
    pages_text = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                pages_text.append(text)
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}", file=sys.stderr)
        return ""

    return "\n\n".join(pages_text)


def extract_text_with_fallback(pdf_path: Path) -> str:
    """Extrai texto de PDF scanned com fallback para modo OCR."""
    # TODO: Implement OCR mode with pdfplumber
    # For now, use native extraction (OCR requires additional setup)
    return extract_text_native(pdf_path)


def split_by_pages(text: str, pages_total: int) -> List[str]:
    """Divide texto em páginas (heurística baseada em quebras de página)."""
    # Simples: dividir por \f (form feed) se presente, senão dividir proporcionalmente
    if "\f" in text:
        return text.split("\f")

    # Fallback: dividir proporcionalmente
    lines = text.split("\n")
    lines_per_page = max(1, len(lines) // pages_total) if pages_total > 0 else len(lines)

    pages = []
    for i in range(0, len(lines), lines_per_page):
        pages.append("\n".join(lines[i:i + lines_per_page]))

    return pages


def preprocess_single_pdf(args: Tuple[Path, Path]) -> ProcessingResult:
    """Processa 1 PDF: detecção OCR, extração, validação.

    Args:
        args: Tuple de (pdf_path, output_base_dir)

    Returns:
        ProcessingResult com status, markdown, metadata, validation
    """
    pdf_path, output_base_dir = args

    try:
        print(f"[.] Processing: {pdf_path.name}", flush=True)

        # 1. OCR detection
        needs_ocr, text_ratio = detect_ocr_needed(pdf_path)

        # 2. Text extraction
        if needs_ocr:
            text = extract_text_with_fallback(pdf_path)
        else:
            text = extract_text_native(pdf_path)

        # 3. Table extraction
        tables = extract_tables_pdfplumber(pdf_path)

        # 4. Metadata rule-based
        pages_total = get_page_count(pdf_path)

        # Get relative path from referencias/
        try:
            # Find "referencias" in path and get relative part
            parts = pdf_path.parts
            if "referencias" in parts:
                idx = parts.index("referencias")
                source_file = str(Path(*parts[idx+1:]))
            else:
                source_file = pdf_path.name
        except Exception:
            source_file = pdf_path.name

        metadata = {
            "source_file": source_file,
            "taxonomy": extract_taxonomy_from_path(pdf_path),
            "doc_type": infer_doc_type(pdf_path.name),
            "pages_total": pages_total,
            "ocr_applied": needs_ocr,
            "text_extraction_quality": text_ratio,
            "tables_detected": len(tables),
            "file_hash": compute_md5(pdf_path),
            "processed_at": datetime.now().isoformat()
        }

        # 5. Generate preliminary markdown
        pages_text = split_by_pages(text, pages_total)
        md_content = format_preliminary_markdown(
            pages_text=pages_text,
            tables=tables,
            metadata=metadata
        )

        # 6. Technical validation
        validation = validate_preliminary_extraction(
            pdf_path=pdf_path,
            markdown=md_content,
            metadata=metadata
        )

        # 7. Write output
        # Mirror directory structure
        rel_path = pdf_path.relative_to(pdf_path.parent.parent.parent)  # Remove up to referencias/
        output_path = output_base_dir / rel_path.with_suffix('.md')
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_text(md_content, encoding='utf-8')

        print(f"[>] Completed: {pdf_path.name} -> {output_path.name}", flush=True)

        return ProcessingResult(
            pdf_path=pdf_path,
            output_path=output_path,
            markdown=md_content,
            metadata=metadata,
            validation=validation,
            status="success"
        )

    except Exception as e:
        print(f"[X] Failed: {pdf_path.name} - {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()

        return ProcessingResult(
            pdf_path=pdf_path,
            output_path=None,
            markdown="",
            metadata={"error": str(e)},
            validation=ValidationResult(success=False, issues=[{"type": "processing_error", "message": str(e)}], warnings=[]),
            status="failed"
        )


def generate_batch_report(results: List[ProcessingResult], processing_time: float) -> Dict[str, Any]:
    """Gera relatório consolidado do batch."""
    successful = [r for r in results if r.status == "success"]
    failed = [r for r in results if r.status == "failed"]

    # Aggregate by taxonomy
    by_taxonomy = {}
    for result in successful:
        taxonomy = result.metadata.get("taxonomy", "unknown")
        if taxonomy not in by_taxonomy:
            by_taxonomy[taxonomy] = {"total": 0, "success": 0}
        by_taxonomy[taxonomy]["total"] += 1
        by_taxonomy[taxonomy]["success"] += 1

    for result in failed:
        # Try to get taxonomy from path
        taxonomy = "unknown"
        if hasattr(result.pdf_path, 'parts'):
            parts = result.pdf_path.parts
            if len(parts) > 1:
                taxonomy = parts[-2]

        if taxonomy not in by_taxonomy:
            by_taxonomy[taxonomy] = {"total": 0, "success": 0}
        by_taxonomy[taxonomy]["total"] += 1

    # Calculate metrics
    ocr_applied_count = sum(1 for r in successful if r.metadata.get("ocr_applied", False))
    avg_text_quality = sum(r.metadata.get("text_extraction_quality", 0) for r in successful) / max(1, len(successful))
    total_tables = sum(r.metadata.get("tables_detected", 0) for r in successful)

    report = {
        "timestamp": datetime.now().isoformat(),
        "total_pdfs": len(results),
        "successful": len(successful),
        "failed": len(failed),
        "processing_time_seconds": int(processing_time),
        "files": [
            {
                "pdf": str(r.pdf_path.name),
                "output": str(r.output_path.name) if r.output_path else None,
                "status": r.status,
                "metadata": r.metadata,
                "validation": {
                    "success": r.validation.success,
                    "issues": r.validation.issues,
                    "warnings": r.validation.warnings
                } if r.validation else None
            }
            for r in results
        ],
        "summary": {
            "by_taxonomy": by_taxonomy,
            "ocr_applied_count": ocr_applied_count,
            "avg_text_quality": round(avg_text_quality, 2),
            "total_tables_extracted": total_tables
        }
    }

    return report


def write_issues_summary(results: List[ProcessingResult], output_dir: Path):
    """Gera summary markdown de issues e warnings."""
    lines = [
        "# Issues Summary - Phase 1 Batch Preprocessing",
        f"Generated: {datetime.now().isoformat()}",
        "",
        "## Failed Files",
        ""
    ]

    failed = [r for r in results if r.status == "failed"]
    if failed:
        for result in failed:
            lines.append(f"### {result.pdf_path.name}")
            lines.append(f"**Error:** {result.metadata.get('error', 'Unknown error')}")
            lines.append("")
    else:
        lines.append("No failed files.")
        lines.append("")

    lines.extend([
        "## Warnings",
        ""
    ])

    successful_with_warnings = [r for r in results if r.status == "success" and r.validation and r.validation.warnings]
    if successful_with_warnings:
        for result in successful_with_warnings:
            lines.append(f"### {result.pdf_path.name}")
            for warning in result.validation.warnings:
                lines.append(f"- **{warning.get('type')}** ({warning.get('severity')}): {warning.get('message')}")
            lines.append("")
    else:
        lines.append("No warnings.")
        lines.append("")

    output_path = output_dir / "_reports" / "issues_summary.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding='utf-8')

    print(f"\n[>] Issues summary written to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Batch PDF preprocessing for Phase 1")
    parser.add_argument("--input", type=Path, required=True, help="Input directory (e.g., referencias/)")
    parser.add_argument("--output", type=Path, required=True, help="Output directory (e.g., referencias_preprocessed/)")
    parser.add_argument("--exclude", nargs="+", default=["archive", "Licitacoes_Compras_e_Contratos"], help="Folders to exclude")
    parser.add_argument("--concurrency", type=int, default=4, help="Number of parallel processes")
    parser.add_argument("--report-output", type=Path, help="Path for batch report JSON (default: output/_reports/batch_report.json)")

    args = parser.parse_args()

    input_dir = args.input
    output_dir = args.output
    exclusions = args.exclude
    concurrency = args.concurrency

    if not input_dir.exists():
        print(f"Error: Input directory does not exist: {input_dir}", file=sys.stderr)
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Scan for PDFs (exclude specified folders)
    print(f"\n[.] Scanning for PDFs in {input_dir}...")
    print(f"[.] Excluding: {', '.join(exclusions)}")

    pdfs = [
        p for p in input_dir.rglob("*.pdf")
        if not any(excl in str(p) for excl in exclusions)
    ]

    print(f"[>] Found {len(pdfs)} PDFs to process\n")

    if len(pdfs) == 0:
        print("No PDFs found. Exiting.")
        sys.exit(0)

    # Prepare args for multiprocessing
    process_args = [(pdf, output_dir) for pdf in pdfs]

    # Process in parallel
    start_time = datetime.now()

    print(f"[.] Starting batch processing with {concurrency} workers...\n")

    # Windows multiprocessing guard
    if __name__ == "__main__":
        with Pool(concurrency) as pool:
            results = pool.map(preprocess_single_pdf, process_args)

    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()

    # Generate reports
    print(f"\n[.] Generating batch report...")
    report = generate_batch_report(results, processing_time)

    # Write batch report JSON
    report_path = args.report_output or (output_dir / "_reports" / "batch_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"[>] Batch report written to: {report_path}")

    # Write issues summary
    write_issues_summary(results, output_dir)

    # Print summary
    print(f"\n{'='*60}")
    print(f"BATCH PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Total PDFs:       {report['total_pdfs']}")
    print(f"Successful:       {report['successful']} ({report['successful']/report['total_pdfs']*100:.1f}%)")
    print(f"Failed:           {report['failed']}")
    print(f"Processing time:  {int(processing_time//60)}min {int(processing_time%60)}s")
    print(f"Avg text quality: {report['summary']['avg_text_quality']:.2f}")
    print(f"Tables extracted: {report['summary']['total_tables_extracted']}")
    print(f"OCR applied:      {report['summary']['ocr_applied_count']} PDFs")
    print(f"{'='*60}\n")

    if report['failed'] > 0:
        print(f"⚠️  {report['failed']} files failed. See {output_dir}/_reports/issues_summary.md")
        sys.exit(1)
    else:
        print("✅ All files processed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
