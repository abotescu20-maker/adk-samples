"""Local HTTP demo server for the Genetic Health Coach agent."""

from __future__ import annotations

import cgi
import html
import json
import os
import tempfile
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterable, List, Sequence

from .tools.subject_analysis import build_subject_report
from .tools.vcf_parser import extract_gene_variants

AVAILABLE_SUBJECTS = {
    "sport": "Sport",
    "nutriție": "Nutriție",
    "terapii": "Terapii",
}

SUBJECT_SYNONYMS = {
    "nutritie": "nutriție",
    "terapie": "terapii",
}


def _normalise_subjects(subjects: Iterable[str] | None) -> List[str]:
    normalised: List[str] = []
    if not subjects:
        return ["sport", "nutriție", "terapii"]
    for subject in subjects:
        if not subject:
            continue
        key = subject.strip().lower()
        if key in AVAILABLE_SUBJECTS:
            canonical = key
        else:
            canonical = SUBJECT_SYNONYMS.get(key, key)
        if canonical not in ("sport", "nutriție", "terapii"):
            continue
        if canonical not in normalised:
            normalised.append(canonical)
    return normalised or ["sport", "nutriție", "terapii"]


def render_subject_html(report: dict[str, object]) -> str:
    """Return an HTML fragment for a subject report."""

    subject_key = str(report.get("subject", ""))
    title = AVAILABLE_SUBJECTS.get(subject_key, subject_key.capitalize())
    entries: Sequence[dict[str, object]] = list(report.get("entries") or [])  # type: ignore[arg-type]
    if not entries:
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

    return (
        f"<article><h2>Subiect: {html.escape(title)}</h2>"
        f"<p><strong>Gene/mutații relevante:</strong> {gene_section}</p>"
        f"<p><strong>Argumentare:</strong> {html.escape(argument_block)}</p>"
        f"<h3>Recomandări</h3><ul>{recommendation_items}</ul></article>"
    )


def _build_reports(vcf_path: Path, subjects: Iterable[str]) -> dict[str, object]:
    gene_payload = extract_gene_variants(str(vcf_path))
    subject_reports = [
        build_subject_report(subject, gene_payload) for subject in _normalise_subjects(subjects)
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

        rendered_sections = "".join(render_subject_html(report) for report in reports["subjects"])
        document = render_full_page(f"<h2>Rezultate</h2>{rendered_sections}")
        self._send(HTTPStatus.OK, document.encode("utf-8"), "text/html; charset=utf-8")


def run_demo_server(host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    """Start the demo HTTP server and return the server instance."""

    server = ThreadingHTTPServer((host, port), DemoRequestHandler)
    print(f"Serverul rulează pe http://{host}:{port}")
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
    "render_full_page",
    "render_subject_html",
    "run_demo_server",
]


if __name__ == "__main__":  # pragma: no cover - manual usage
    run_demo_server()
