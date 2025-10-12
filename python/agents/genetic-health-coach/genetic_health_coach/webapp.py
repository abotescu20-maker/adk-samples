"""Local HTTP demo server for the Genetic Health Coach agent."""

from __future__ import annotations

import argparse
import cgi
import html
import json
import os
import sys
import tempfile
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterable, List, Sequence

from .subjects import AVAILABLE_SUBJECTS, SUBJECT_SYNONYMS, normalise_subjects
from .tools.subject_analysis import build_subject_report
from .tools.vcf_parser import extract_gene_variants


def render_subject_html(report: dict[str, object]) -> str:
    """Return an HTML fragment for a subject report."""

    subject_key = str(report.get("subject", ""))
    title = AVAILABLE_SUBJECTS.get(subject_key, subject_key.capitalize())
    entries: Sequence[dict[str, object]] = list(report.get("entries") or [])  # type: ignore[arg-type]
    irrelevant_genes: Sequence[str] = list(report.get("irrelevant_genes") or [])  # type: ignore[arg-type]
    if not entries:
        if irrelevant_genes:
            missing = ", ".join(html.escape(g) for g in irrelevant_genes)
            return (
                f"<article><h2>Subiect: {html.escape(title)}</h2>"
                f"<p><strong>Gene analizate:</strong> {missing}</p>"
                "<p><em>Pentru genele de mai sus nu există încă reguli dedicate în agent. "
                "Personalizează baza de cunoștințe pentru recomandări specifice.</em></p>"
                "</article>"
            )
        return (
            f"<article><h2>Subiect: {html.escape(title)}</h2>"
            "<p><em>Nu au fost găsite gene relevante pentru acest subiect.</em></p></article>"
        )

    gene_details: List[str] = []
    for entry in entries:
        gene = html.escape(str(entry.get("gene", "")))
        mutations = entry.get("mutations") or []
        if mutations:
            mutation_text = "; ".join(html.escape(str(m)) for m in mutations if m)
            gene_details.append(f"{gene} ({mutation_text})")
        else:
            gene_details.append(gene)

    arguments = []
    for entry in entries:
        argument = str(entry.get("argument") or "")
        if argument:
            arguments.append(argument)

    recommendations: List[str] = []
    for entry in entries:
        for rec in entry.get("recommendations", []) or []:
            if rec not in recommendations:
                recommendations.append(rec)

    argument_block = " ".join(arguments) or "Nu există argumente suplimentare pentru acest subiect."
    gene_section = ", ".join(gene_details) if gene_details else "Nespecificat"
    recommendation_items = "".join(
        f"<li>{html.escape(rec)}</li>" for rec in recommendations if rec
    ) or "<li>Nu au fost generate recomandări specifice.</li>"

    extra_note = ""
    if irrelevant_genes:
        extra_note = (
            "<p><em>Gene suplimentare identificate fără reguli dedicate: "
            + ", ".join(html.escape(g) for g in irrelevant_genes)
            + "</em></p>"
        )

    return (
        f"<article><h2>Subiect: {html.escape(title)}</h2>"
        f"<p><strong>Gene/mutații relevante:</strong> {gene_section}</p>"
        f"<p><strong>Argumentare:</strong> {html.escape(argument_block)}</p>"
        f"<h3>Recomandări</h3><ul>{recommendation_items}</ul>{extra_note}</article>"
    )


def render_gene_summary(gene_payload: dict[str, object]) -> str:
    """Return an HTML fragment summarising all detected genes."""

    genes: Sequence[dict[str, object]] = list(gene_payload.get("genes") or [])  # type: ignore[arg-type]
    if not genes:
        return (
            "<section><h2>Gene identificate</h2><p><em>Nu au fost detectate variante în fișierul VCF.</em></p></section>"
        )

    items: list[str] = []
    for entry in genes:
        gene = html.escape(str(entry.get("gene", "")))
        variants: Sequence[dict[str, object]] = list(entry.get("variants") or [])  # type: ignore[arg-type]
        count = entry.get("variant_count") or len(variants)
        variant_descriptions: list[str] = []
        for variant in variants:
            chrom = variant.get("chrom")
            position = variant.get("position")
            ref = variant.get("ref")
            alt = variant.get("alt")
            effects = "/".join(variant.get("effects") or [])
            location = f"{chrom}:{position}" if chrom and position else "Locus nespecificat"
            change = f"{ref}>{alt}" if ref and alt else ""
            pieces = [location]
            if change:
                pieces.append(change)
            if effects:
                pieces.append(effects)
            variant_descriptions.append(" – ".join(pieces))
        details = "<br>".join(html.escape(text) for text in variant_descriptions if text)
        items.append(
            "<li><strong>{gene}</strong> – {count} variantă/variante".format(gene=gene, count=count)
            + (f"<br>{details}" if details else "")
            + "</li>"
        )

    return (
        "<section><h2>Gene identificate</h2><ul>"
        + "".join(items)
        + "</ul></section>"
    )


def _build_reports(vcf_path: Path, subjects: Iterable[str]) -> dict[str, object]:
    gene_payload = extract_gene_variants(str(vcf_path))
    subject_reports = [
        build_subject_report(subject, gene_payload) for subject in normalise_subjects(subjects)
    ]
    return {
        "vcf_path": str(vcf_path),
        "subjects": subject_reports,
        "gene_summary": gene_payload,
    }


def build_reports_from_bytes(vcf_bytes: bytes, subjects: Iterable[str]) -> dict[str, object]:
    """Persist uploaded bytes temporarily and build the structured reports."""

    if not vcf_bytes:
        raise ValueError("Fișierul VCF este gol.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".vcf") as tmp:
        tmp.write(vcf_bytes)
        temp_path = Path(tmp.name)

    try:
        return _build_reports(temp_path, subjects)
    finally:
        try:
            os.unlink(temp_path)
        except OSError:
            pass


def render_full_page(body: str) -> str:
    """Wrap content inside the demo HTML layout."""

    return f"""
    <!doctype html>
    <html lang=\"ro\">
      <head>
        <meta charset=\"utf-8\">
        <title>Genetic Health Coach Demo</title>
        <style>
          body {{ font-family: Arial, sans-serif; margin: 2rem; line-height: 1.6; }}
          header {{ margin-bottom: 2rem; }}
          form label {{ display: block; margin-top: 1rem; }}
          article {{ border: 1px solid #ddd; padding: 1rem 1.5rem; margin-bottom: 1.5rem; border-radius: 8px; background-color: #fafafa; }}
          h1 {{ font-size: 1.8rem; }}
          h2 {{ color: #0b5394; }}
          button {{ margin-top: 1.5rem; padding: 0.6rem 1.4rem; font-size: 1rem; }}
        </style>
      </head>
      <body>
        <header>
          <h1>Genetic Health Coach – demo local</h1>
          <p>Încarcă un fișier VCF adnotat, selectează temele dorite și apasă „Generează raport”. După pornirea serverului vei accesa linkul local <code>http://localhost:8000</code>.</p>
        </header>
        <section>
          <form action=\"/analyze\" method=\"post\" enctype=\"multipart/form-data\">
            <label for=\"file\">Fișier VCF adnotat</label>
            <input type=\"file\" id=\"file\" name=\"file\" accept=\".vcf,text/vcf\" required>
            <fieldset>
              <legend>Subiecte analizate</legend>
              <label><input type=\"checkbox\" name=\"subjects\" value=\"sport\" checked> Sport</label>
              <label><input type=\"checkbox\" name=\"subjects\" value=\"nutriție\" checked> Nutriție</label>
              <label><input type=\"checkbox\" name=\"subjects\" value=\"terapii\" checked> Terapii</label>
            </fieldset>
            <button type=\"submit\">Generează raport</button>
          </form>
        </section>
        <section>
          {body}
        </section>
      </body>
    </html>
    """


class DemoRequestHandler(BaseHTTPRequestHandler):
    """HTTP handler that serves the demo interface and API."""

    server_version = "GeneticHealthCoachDemo/0.1"

    def log_message(self, format: str, *args) -> None:  # pragma: no cover - keep console quiet
        return

    def _send(self, status: HTTPStatus, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path in {"/", "/index.html"}:
            document = render_full_page("")
            self._send(HTTPStatus.OK, document.encode("utf-8"), "text/html; charset=utf-8")
        elif self.path == "/healthz":
            self._send(HTTPStatus.OK, b"ok", "text/plain; charset=utf-8")
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Resursa nu a fost găsită.")

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path not in {"/analyze", "/api/analyze"}:
            self.send_error(HTTPStatus.NOT_FOUND, "Resursa nu a fost găsită.")
            return

        content_type = self.headers.get("Content-Type", "")
        content_length = int(self.headers.get("Content-Length", "0"))
        environ = {
            "REQUEST_METHOD": "POST",
            "CONTENT_TYPE": content_type,
            "CONTENT_LENGTH": str(content_length),
        }

        try:
            form = cgi.FieldStorage(  # type: ignore[call-arg]
                fp=self.rfile,
                headers=self.headers,
                environ=environ,
                keep_blank_values=True,
            )
        except Exception as exc:  # pragma: no cover - defensive
            self.send_error(HTTPStatus.BAD_REQUEST, f"Nu s-a putut procesa formularul: {exc}")
            return

        if "file" not in form:
            self.send_error(HTTPStatus.BAD_REQUEST, "Nu a fost trimis niciun fișier VCF.")
            return

        file_field = form["file"]
        file_bytes = file_field.file.read() if getattr(file_field, "file", None) else b""
        if not file_bytes:
            self.send_error(HTTPStatus.BAD_REQUEST, "Fișierul VCF este gol.")
            return

        subjects = form.getlist("subjects") if hasattr(form, "getlist") else []

        try:
            reports = build_reports_from_bytes(file_bytes, subjects)
        except FileNotFoundError as exc:  # pragma: no cover - defensive
            self.send_error(HTTPStatus.NOT_FOUND, str(exc))
            return
        except ValueError as exc:
            self.send_error(HTTPStatus.BAD_REQUEST, str(exc))
            return

        if self.path == "/api/analyze":
            body = json.dumps(reports, ensure_ascii=False, indent=2).encode("utf-8")
            self._send(HTTPStatus.OK, body, "application/json; charset=utf-8")
            return

        summary_html = render_gene_summary(reports["gene_summary"])
        rendered_sections = "".join(render_subject_html(report) for report in reports["subjects"])
        document = render_full_page(f"<h2>Rezultate</h2>{summary_html}{rendered_sections}")
        self._send(HTTPStatus.OK, document.encode("utf-8"), "text/html; charset=utf-8")


def run_demo_server(host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    """Start the demo HTTP server and return the server instance."""

    server = ThreadingHTTPServer((host, port), DemoRequestHandler)
    if host in {"0.0.0.0", "::"}:
        display_host = "localhost"
    else:
        display_host = host
    print(f"Serverul rulează pe http://{display_host}:{port}")
    if host in {"0.0.0.0", "::"}:
        print("Serverul acceptă conexiuni de la alte dispozitive din rețea.")
    print("Apasă Ctrl+C pentru a opri.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:  # pragma: no cover - manual exit
        pass
    finally:
        server.server_close()
    return server


__all__ = [
    "DemoRequestHandler",
    "build_reports_from_bytes",
    "render_gene_summary",
    "render_full_page",
    "render_subject_html",
    "run_demo_server",
    "_parse_args",
    "main",
]


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the demo server."""

    parser = argparse.ArgumentParser(description="Pornește serverul demo Genetic Health Coach.")
    parser.add_argument(
        "--host",
        default=os.environ.get("GENETIC_HEALTH_COACH_HOST", "127.0.0.1"),
        help="Adresa pe care ascultă serverul (implicit 127.0.0.1).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("GENETIC_HEALTH_COACH_PORT", "8000")),
        help="Portul pe care ascultă serverul (implicit 8000).",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point for launching the demo server."""

    args = _parse_args(argv)
    run_demo_server(args.host, args.port)
    return 0


if __name__ == "__main__":  # pragma: no cover - manual usage
    sys.exit(main())
