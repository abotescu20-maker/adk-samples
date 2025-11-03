"""Audio capture and transcription utilities."""

from __future__ import annotations

import queue
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from pydub import AudioSegment


TranscriptCallback = Callable[[str], None]


@dataclass
class TranscriberConfig:
    """Configuration for the live transcription pipeline."""

    model_size: str = "small"
    device: str = "auto"
    compute_type: str = "int8"
    sample_rate: int = 16_000
    chunk_duration: float = 5.0


class LiveTranscriber:
    """Continuously captures audio and emits Whisper transcripts."""

    def __init__(self, config: TranscriberConfig) -> None:
        self._config = config
        self._model = WhisperModel(
            config.model_size,
            device=config.device,
            compute_type=config.compute_type,
        )
        self._audio_queue: queue.Queue[np.ndarray] = queue.Queue()
        self._worker: Optional[threading.Thread] = None
        self._stream: Optional[sd.InputStream] = None
        self._running = threading.Event()
        self._callback: Optional[TranscriptCallback] = None

    def start_microphone(self, callback: TranscriptCallback) -> None:
        """Begin streaming microphone audio."""
        self._callback = callback
        self._running.set()
        self._stream = sd.InputStream(
            channels=1,
            samplerate=self._config.sample_rate,
            dtype="float32",
            callback=self._audio_callback,
        )
        self._stream.start()
        self._worker = threading.Thread(
            target=self._transcription_loop, daemon=True
        )
        self._worker.start()

    def start_file(self, audio_path: str | Path, callback: TranscriptCallback) -> None:
        """Stream an audio file instead of the microphone."""
        segment = AudioSegment.from_file(audio_path)
        segment = segment.set_channels(1).set_frame_rate(self._config.sample_rate)
        samples = np.array(segment.get_array_of_samples()).astype(np.float32)
        max_amplitude = max(segment.max_possible_amplitude, 1)
        samples /= max_amplitude
        chunk_size = int(self._config.sample_rate * self._config.chunk_duration)
        self._callback = callback
        self._running.set()

        def file_worker() -> None:
            index = 0
            while self._running.is_set() and index < len(samples):
                chunk = samples[index : index + chunk_size]
                index += chunk_size
                self._emit_transcript(chunk)
            self._running.clear()

        self._worker = threading.Thread(target=file_worker, daemon=True)
        self._worker.start()

    def stop(self) -> None:
        """Stop the audio stream and transcription worker."""
        self._running.clear()
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        if self._worker is not None:
            self._worker.join(timeout=2.0)
            self._worker = None

    @property
    def is_running(self) -> bool:
        """Return True while audio is still being processed."""
        return self._running.is_set()

    def _audio_callback(
        self, indata: np.ndarray, frames: int, time, status
    ) -> None:  # type: ignore[override]
        del frames, time
        if status:
            print(f"[sounddevice] {status}")
        self._audio_queue.put(indata.copy().reshape(-1))

    def _transcription_loop(self) -> None:
        buffer: list[np.ndarray] = []
        samples_collected = 0
        chunk_threshold = int(self._config.sample_rate * self._config.chunk_duration)
        while self._running.is_set():
            try:
                audio_chunk = self._audio_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            buffer.append(audio_chunk)
            samples_collected += len(audio_chunk)
            if samples_collected >= chunk_threshold:
                chunk = np.concatenate(buffer)
                buffer.clear()
                samples_collected = 0
                self._emit_transcript(chunk)

    def _emit_transcript(self, chunk: np.ndarray) -> None:
        if self._callback is None:
            return
        if not len(chunk):
            return
        segments, _ = self._model.transcribe(
            chunk, language="auto", beam_size=1, temperature=0.0
        )
        text = " ".join(seg.text.strip() for seg in segments).strip()
        if text:
            self._callback(text)
