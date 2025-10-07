"""Tests for the local HTTP demo application."""

from __future__ import annotations

import http.client
import json
import threading
from pathlib import Path
from typing import Tuple

from http.server import ThreadingHTTPServer

from genetic_health_coach.webapp import (
    DemoRequestHandler,
    build_reports_from_bytes,
    render_full_page,
    render_subject_html,
)


def _sample_vcf_bytes() -> bytes:
    sample_path = Path(__file__).resolve().parent.parent / "sample_data" / "example_annotated.vcf"
    return sample_path.read_bytes()


def _start_server() -> Tuple[ThreadingHTTPServer, int]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, port


def test_render_full_page_contains_form() -> None:
    html_doc = render_full_page("")
    assert "Genetic Health Coach" in html_doc
    assert "form" in html_doc
    assert "http://localhost:8000" in html_doc


def test_build_reports_from_bytes_generates_subjects() -> None:
    reports = build_reports_from_bytes(_sample_vcf_bytes(), ["sport", "nutriție"])
    subjects = [entry["subject"] for entry in reports["subjects"]]
    assert "sport" in subjects
    assert "nutriție" in subjects
    fragment = render_subject_html(reports["subjects"][0])
    assert "Recomandări" in fragment


def test_http_server_serves_homepage_and_api() -> None:
    server, port = _start_server()
    try:
        conn = http.client.HTTPConnection("127.0.0.1", port)
        conn.request("GET", "/")
        response = conn.getresponse()
        body = response.read().decode("utf-8")
        assert response.status == 200
        assert "Genetic Health Coach" in body
        conn.close()

        boundary = "----GeneticBoundary"
        payload_parts = [
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"subjects\"\r\n\r\nsport\r\n",
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"subjects\"\r\n\r\nterapii\r\n",
            (
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"example.vcf\"\r\n"
                "Content-Type: text/vcf\r\n\r\n"
                + _sample_vcf_bytes().decode("utf-8")
                + "\r\n"
            ),
            f"--{boundary}--\r\n",
        ]
        payload = "".join(payload_parts).encode("utf-8")
        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(payload)),
        }
        conn = http.client.HTTPConnection("127.0.0.1", port)
        conn.request("POST", "/api/analyze", body=payload, headers=headers)
        response = conn.getresponse()
        api_body = response.read().decode("utf-8")
        assert response.status == 200
        payload_json = json.loads(api_body)
        assert payload_json["subjects"][0]["subject"] in {"sport", "terapii"}
        conn.close()
    finally:
        server.shutdown()
        server.server_close()
