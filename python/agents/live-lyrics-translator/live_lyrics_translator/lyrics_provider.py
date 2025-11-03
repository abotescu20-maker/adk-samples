"""Utilities for fetching song lyrics."""

from __future__ import annotations

import os
import pathlib
import re
from typing import Iterable, List

import requests
from requests.utils import quote


class LyricsProvider:
    """Fetches and normalizes song lyrics."""

    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self._base_url = base_url or os.getenv(
            "LYRICS_OVH_BASE_URL", "https://api.lyrics.ovh/v1"
        )
        self._timeout = timeout

    def fetch(self, artist: str, title: str) -> List[str]:
        """Fetch lyrics from the lyrics.ovh API."""
        endpoint = "{base}/{artist}/{title}".format(
            base=self._base_url.rstrip("/"),
            artist=quote(artist, safe=""),
            title=quote(title, safe=""),
        )
        response = requests.get(endpoint, timeout=self._timeout)
        response.raise_for_status()
        data = response.json()
        raw_text = data.get("lyrics")
        if not raw_text:
            raise ValueError("Lyrics API returned empty text.")
        return self._normalize(raw_text.splitlines())

    def load_from_file(self, path: str | os.PathLike[str]) -> List[str]:
        """Load lyrics from a plain text file."""
        content = pathlib.Path(path).read_text(encoding="utf-8")
        return self._normalize(content.splitlines())

    @staticmethod
    def _normalize(lines: Iterable[str]) -> List[str]:
        normalized: List[str] = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            stripped = re.sub(r"\s+", " ", stripped)
            normalized.append(stripped)
        if not normalized:
            raise ValueError("No lyric lines available after normalization.")
        return normalized
