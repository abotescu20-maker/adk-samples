"""Create a zip archive of the nutrigenomics agent for easy sharing.

This script collects the core project files (agent config, prompts, README,
Dockerfile, Streamlit runner, etc.) into a single archive that you can hand off
or download from a remote machine.

Example:
    python tools/export_bundle.py
    python tools/export_bundle.py --output /tmp/nutrigenomics-agent.zip
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable
import zipfile

AGENT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARCHIVE_NAME = AGENT_ROOT / "nutrigenomics_agent_bundle"

# Relative paths (from the agent root) that should be bundled.
INCLUDE_PATHS: tuple[str, ...] = (
    ".dockerignore",
    ".env.example",
    "Dockerfile",
    "README.md",
    "nutrigenomics_rag",
    "pyproject.toml",
    "streamlit_runner",
    "tests",
)

# Glob-style patterns that should be skipped even if they fall within an
# included directory. These keep build artefacts and caches out of the bundle.
EXCLUDE_SUFFIXES: tuple[str, ...] = (
    "__pycache__",
    ".pyc",
    ".pyo",
    ".DS_Store",
)


def iter_files(paths: Iterable[Path]) -> Iterable[Path]:
    """Yield all files under the given paths, skipping excluded suffixes."""

    for source_path in paths:
        if source_path.name in EXCLUDE_SUFFIXES or source_path.suffix in EXCLUDE_SUFFIXES:
            continue

        if source_path.is_dir():
            for child in source_path.rglob("*"):
                if not child.is_file():
                    continue
                if _should_skip(child):
                    continue
                yield child
        elif source_path.is_file():
            if _should_skip(source_path):
                continue
            yield source_path


def _should_skip(path: Path) -> bool:
    return any(part in EXCLUDE_SUFFIXES for part in path.parts) or path.suffix in EXCLUDE_SUFFIXES


def create_archive(output_path: Path) -> Path:
    files_to_archive = list(iter_files(AGENT_ROOT / rel_path for rel_path in INCLUDE_PATHS))

    if not files_to_archive:
        raise RuntimeError("No files found to archive. Check INCLUDE_PATHS configuration.")

    archive_path = output_path.with_suffix(".zip")
    with zipfile.ZipFile(archive_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_archive:
            arcname = file_path.relative_to(AGENT_ROOT)
            zipf.write(file_path, arcname)

    return archive_path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package the nutrigenomics agent into a zip archive")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_ARCHIVE_NAME,
        help="Path (without extension) for the generated archive. Defaults to nutrigenomics_agent_bundle.zip in the agent directory.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    try:
        archive_path = create_archive(args.output)
    except Exception as exc:  # noqa: BLE001 - surface helpful message for CLI usage
        print(f"Error while creating archive: {exc}")
        return 1

    print(f"Created archive: {archive_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
