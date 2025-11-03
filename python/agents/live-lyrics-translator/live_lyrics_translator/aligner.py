"""Match Whisper transcripts to lyric lines."""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple


@dataclass
class LyricLine:
    original: str
    translation: str


class LyricsAligner:
    """Stateful fuzzy matcher between transcripts and lyric lines."""

    def __init__(self, lyrics: Iterable[str], translations: Iterable[str]) -> None:
        self._lines: List[LyricLine] = [
            LyricLine(original=line, translation=translation)
            for line, translation in zip(lyrics, translations)
        ]
        self._cursor = -1

    def process(self, transcript: str, min_ratio: float = 0.45) -> Optional[LyricLine]:
        """Return the best matching lyric line for the transcript."""
        start_index = max(self._cursor, 0)
        best: Tuple[int, float] | None = None
        normalized_transcript = transcript.lower().strip()
        if not normalized_transcript:
            return None
        search_range = range(start_index, len(self._lines))
        for idx in search_range:
            candidate = self._lines[idx].original.lower()
            ratio = difflib.SequenceMatcher(None, candidate, normalized_transcript).ratio()
            if best is None or ratio > best[1]:
                best = (idx, ratio)
        if best is None or best[1] < min_ratio:
            return None
        index, _ = best
        if index <= self._cursor:
            return None
        self._cursor = index
        return self._lines[index]
