"""Translation utilities."""

from __future__ import annotations

import os
from typing import Iterable, List

from googletrans import Translator


class TranslationService:
    """Wraps the googletrans client with repo-specific defaults."""

    def __init__(self, target_language: str = "en") -> None:
        self._target_language = target_language
        service_urls_env = os.getenv("GOOGLETRANS_SERVICE_URLS")
        service_urls = (
            [url.strip() for url in service_urls_env.split(",") if url.strip()]
            if service_urls_env
            else None
        )
        self._translator = Translator(service_urls=service_urls)

    def translate_lines(self, lines: Iterable[str]) -> List[str]:
        """Translate a sequence of lyric lines."""
        translations = self._translator.translate(
            list(lines), dest=self._target_language
        )
        return [result.text for result in translations]
