# Live Lyrics Translator

The **Live Lyrics Translator** agent listens to music through your microphone,
fetches the corresponding lyrics, and streams a live translation on screen.
It is built as a console-based Python experience so you can run it locally
without deploying any UI framework.

> ⚠️ This sample requires optional dependencies such as
> [`faster-whisper`](https://github.com/guillaumekln/faster-whisper) and
> [`sounddevice`](https://python-sounddevice.readthedocs.io/).
> These packages are not pre-installed and must be added manually before
> running the agent.

## Features

* **Live transcription** &mdash; captures audio from the system microphone in
  five-second windows and transcribes it with Whisper.
* **Lyric lookup** &mdash; pulls full song lyrics from the public
  [lyrics.ovh](https://lyricsovh.docs.apiary.io/#) API.
* **Streaming translation** &mdash; translates each lyric line on the fly using
  [`googletrans`](https://py-googletrans.readthedocs.io/en/latest/).
* **Console dashboard** &mdash; highlights the currently detected lyric line and
  prints both the original text and its translation.

## Prerequisites

1.  Python 3.10 or newer.
2.  The [Python Agent Development Kit](https://github.com/google/adk-python)
    (used for consistent repository tooling).
3.  OS-level access to a microphone supported by `sounddevice`.
4.  A stable internet connection for the lyrics and translation services.

## Setup

1.  Create and activate a virtual environment.

    ```bash
    cd adk-samples/python/agents/live-lyrics-translator
    python -m venv .venv
    source .venv/bin/activate
    ```

2.  Install dependencies with [`uv`](https://docs.astral.sh/uv/) or `pip`:

    ```bash
    uv pip install -r requirements.txt
    # or
    pip install -r requirements.txt
    ```

3.  (Optional) Download a local Whisper model in advance to avoid the initial
    cold-start delay:

    ```bash
    python -c "from faster_whisper import WhisperModel; WhisperModel('small')"
    ```

## Running the agent

Provide the track metadata (artist and song title) so the agent can fetch the
correct lyrics. Then launch the console application:

```bash
python main.py --artist "Carla's Dreams" --title "Sub Pielea Mea" --target ro
```

* `--target` specifies the translation language (default: `en`).
* `--model-size` controls the Whisper model variant (default: `small`).
* `--chunk-duration` adjusts how frequently the audio is transcribed (default:
  `5` seconds).

While the agent is running you will see the following output stream:

```
🎵 Carla's Dreams – Sub Pielea Mea
[RO] Vers original
[EN] Translated line
```

Press <kbd>Ctrl+C</kbd> to stop listening. The app shuts down the audio stream
and exits gracefully.

## Environment variables

| Variable | Description | Default |
| --- | --- | --- |
| `LYRICS_OVH_BASE_URL` | Override the lyrics API endpoint. | `https://api.lyrics.ovh/v1` |
| `GOOGLETRANS_SERVICE_URLS` | Comma separated list of Google Translate service URLs. | `None` |

## Limitations

* **Lyric matching** &mdash; we rely on fuzzy string matching between the Whisper
  transcripts and lyric lines, so instrumental sections or backing vocals may
  reduce accuracy.
* **Rate limits** &mdash; both lyrics.ovh and googletrans are community services.
  Heavy usage can trigger throttling. Cache responses locally if you need to
  process long playlists.
* **Platform support** &mdash; `sounddevice` requires PortAudio. Refer to their
  documentation for OS-specific installation steps.

## Troubleshooting

| Symptom | Possible fix |
| --- | --- |
| `PortAudioError` on startup | Ensure the PortAudio library is installed and the microphone is connected. |
| `requests.HTTPError` fetching lyrics | Double-check the artist/title spelling or provide `--lyrics-file` with local content. |
| Translation lines stuck in English | Verify that the target language is supported by googletrans. |

## Alternative workflows

If you cannot access the microphone (for example inside a remote container),
you can still demo the alignment pipeline by passing a local audio file:

```bash
python main.py --artist "Carla's Dreams" --title "Sub Pielea Mea" \
  --audio-file path/to/song-snippet.mp3
```

The agent loads the file, streams it to the transcription engine, and prints
lyrics/translation updates as if it were listening live.

Enjoy discovering new music while understanding the words in real time! 🎧
