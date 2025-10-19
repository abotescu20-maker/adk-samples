"""Main orchestration logic for the live lyrics translator."""

from __future__ import annotations

import queue
from dataclasses import dataclass
from typing import Optional

from .aligner import LyricsAligner
from .audio_listener import LiveTranscriber, TranscriberConfig
from .lyrics_provider import LyricsProvider
from .translation import TranslationService


@dataclass
class AppConfig:
    """High level configuration toggles for the console app."""

    artist: str
    title: str
    target_language: str = "en"
    lyrics_file: Optional[str] = None
    audio_file: Optional[str] = None


class LyricsTranslatorApp:
    """CLI helper that wires together lyrics, translation, and audio streams."""

    def __init__(self, transcriber_config: TranscriberConfig) -> None:
        self._transcriber_config = transcriber_config

    def run(self, config: AppConfig) -> None:
        lyrics_provider = LyricsProvider()
        if config.lyrics_file:
            lyrics = lyrics_provider.load_from_file(config.lyrics_file)
        else:
            lyrics = lyrics_provider.fetch(config.artist, config.title)

        translator = TranslationService(config.target_language)
        translations = translator.translate_lines(lyrics)
        aligner = LyricsAligner(lyrics, translations)
        transcriber = LiveTranscriber(self._transcriber_config)
        updates: queue.Queue[str] = queue.Queue()

        def handle_transcript(text: str) -> None:
            line = aligner.process(text)
            if line is None:
                return
            updates.put(f"[ORIGINAL] {line.original}\n[TRANSLATED] {line.translation}")

        if config.audio_file:
            transcriber.start_file(config.audio_file, handle_transcript)
        else:
            transcriber.start_microphone(handle_transcript)

        print("🎵 {artist} – {title}".format(artist=config.artist, title=config.title))
        print("Listening... Press Ctrl+C to stop.\n")

        try:
            while True:
                try:
                    message = updates.get(timeout=1.0)
                except queue.Empty:
                    if not transcriber.is_running:
                        break
                    continue
                print(message)
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            transcriber.stop()
            print("Goodbye!")
