"""Command-line interface for generating genetic health reports."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Iterable, Sequence

from .subjects import AVAILABLE_SUBJECTS, normalise_subjects
from .tools.subject_analysis import build_subject_report
from .tools.vcf_parser import extract_gene_variants


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generează rapoarte tematice pe baza unui fișier VCF adnotat.",
    )
    parser.add_argument(
        "vcf_path",
        help="Calea către fișierul VCF adnotat (acceptă și prefixul ~ pentru directorul home).",
    )
    parser.add_argument(
        "-s",
        "--subject",
        dest="subjects",
        action="append",
        metavar="SUBIECT",
        help="Subiectul analizat (poate fi specificat de mai multe ori). Implicit: toate",
    )
    parser.add_argument(
        "--list-subjects",
        action="store_true",
        help="Afișează subiectele disponibile și iese imediat.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Returnează rezultatul în format JSON structurabil în locul formatului textat.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Scrie raportul în fișierul indicat în loc să-l afișeze în consolă.",
    )
    return parser.parse_args(argv)


def _format_recommendations(recommendations: Iterable[str]) -> str:
    items = [rec.strip() for rec in recommendations if rec]
    if not items:
        return "    - Nu au fost generate recomandări pentru acest subiect."
    return "\n".join(f"    - {rec}" for rec in items)


def _format_subject_report(report: dict[str, object]) -> str:
    subject_key = str(report.get("subject", ""))
    subject_label = AVAILABLE_SUBJECTS.get(subject_key, subject_key.capitalize())
    entries = list(report.get("entries") or [])  # type: ignore[arg-type]
    irrelevant = list(report.get("irrelevant_genes") or [])  # type: ignore[arg-type]

    gene_descriptions = []
    for entry in entries:
        gene = str(entry.get("gene", ""))
        mutations = [str(m) for m in entry.get("mutations", []) or []]
        if mutations:
            gene_descriptions.append(f"{gene} ({'; '.join(mutations)})")
        elif gene:
            gene_descriptions.append(gene)

    if gene_descriptions:
        gene_line = ", ".join(gene_descriptions)
    elif irrelevant:
        gene_line = "Gene identificate fără reguli dedicate: " + ", ".join(irrelevant)
    else:
        gene_line = "Nu au fost identificate gene relevante."

    argument = str(report.get("summary_argument") or "").strip()
    if not argument:
        if irrelevant:
            argument = (
                "Genele identificate nu au încă reguli dedicate în baza de cunoștințe. "
                "Personalizează ghidajul pentru recomandări specifice."
            )
        else:
            argument = "Nu există argumente deoarece nu au fost găsite gene relevante pentru acest subiect."

    recommendations = report.get("recommendations") or []
    if not recommendations and irrelevant:
        recommendations = [
            "Adaugă reguli pentru genele analizate fără recomandări dedicate: "
            + ", ".join(irrelevant)
        ]

    lines = [
        f"Subiect: {subject_label}",
        f"- Gene/mutații relevante: {gene_line}",
        f"- Argumentare: {argument}",
        "- Recomandări:",
        _format_recommendations(recommendations),
    ]
    return "\n".join(lines)


def _build_reports(vcf_path: str, subjects: Iterable[str] | None) -> dict[str, object]:
    gene_payload = extract_gene_variants(vcf_path)
    selected_subjects = normalise_subjects(subjects)
    subject_reports = [build_subject_report(subject, gene_payload) for subject in selected_subjects]
    return {
        "subjects": subject_reports,
        "gene_summary": gene_payload,
        "requested_subjects": selected_subjects,
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)

    if args.list_subjects:
        for key, label in AVAILABLE_SUBJECTS.items():
            print(f"{key} – {label}")
        return 0

    reports = _build_reports(args.vcf_path, args.subjects)

    if args.json:
        output = json.dumps(reports, indent=2, ensure_ascii=False)
    else:
        output_lines = [
            _format_subject_report(report)
            for report in reports["subjects"]
        ]
        output = "\n\n".join(output_lines)

    if args.output:
        destination = Path(os.path.expanduser(args.output))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)

    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    raise SystemExit(main())

