"""Entry point for the live lyrics translator console app."""

from __future__ import annotations

import argparse

from live_lyrics_translator import LyricsTranslatorApp
from live_lyrics_translator.app import AppConfig
from live_lyrics_translator.audio_listener import TranscriberConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artist", required=True, help="Artist name for lyric lookup")
    parser.add_argument("--title", required=True, help="Song title for lyric lookup")
    parser.add_argument(
        "--target",
        default="en",
        help="Target language for translation (ISO-639-1 code)",
    )
    parser.add_argument(
        "--lyrics-file",
        help="Optional path to a local lyrics file to skip the HTTP lookup",
    )
    parser.add_argument(
        "--audio-file",
        help="Stream transcription from a local audio file instead of the microphone",
    )
    parser.add_argument(
        "--model-size",
        default="small",
        help="Whisper model size (tiny, base, small, medium, large-v2)",
    )
    parser.add_argument(
        "--device",
        default="auto",
        help="faster-whisper device hint (auto, cpu, cuda, etc.)",
    )
    parser.add_argument(
        "--compute-type",
        default="int8",
        help="faster-whisper compute type (int8, int8_float16, float16, float32)",
    )
    parser.add_argument(
        "--chunk-duration",
        type=float,
        default=5.0,
        help="Seconds of audio to accumulate before each transcription",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    app = LyricsTranslatorApp(
        TranscriberConfig(
            model_size=args.model_size,
            device=args.device,
            compute_type=args.compute_type,
            chunk_duration=args.chunk_duration,
        )
    )
    config = AppConfig(
        artist=args.artist,
        title=args.title,
        target_language=args.target,
        lyrics_file=args.lyrics_file,
        audio_file=args.audio_file,
    )
    app.run(config)


if __name__ == "__main__":
    main()
