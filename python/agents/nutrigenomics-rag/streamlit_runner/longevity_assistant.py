#!/usr/bin/env python
"""CLI entry point for the Longevity & Wellness Streamlit assistant using OpenAI."""

from __future__ import annotations

import asyncio
import logging
import os
import platform
import subprocess
import sys
import warnings
from pathlib import Path

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR / "src"
ENV_FILE = BASE_DIR.parent / ".env"

REQUIRED_DEPENDENCIES = (
    "streamlit",
    "langchain",
    "langchain_community",
    "sentence_transformers",
    "faiss",
    "pypdf",
    "openai",
    "dotenv",
)


def check_dependencies() -> bool:
    """Verify that the Python dependencies needed by the runner are installed."""

    missing: list[str] = []
    for module_name in REQUIRED_DEPENDENCIES:
        try:
            __import__(module_name)
            logger.debug("Dependency '%s' is available", module_name)
        except ImportError:
            missing.append(module_name)

    if missing:
        logger.error(
            "Missing dependencies detected: %s. Install them with 'poetry install --with streamlit_runner'.",
            ", ".join(missing),
        )
        return False
    return True


def set_memory_optimizations() -> None:
    """Apply runtime optimisations for Streamlit and the embedding pipelines."""

    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
    os.environ.setdefault("STREAMLIT_SERVER_ENABLE_STATIC_SERVING", "true")
    os.environ.setdefault("STREAMLIT_SILENCE_PATH_ERRORS", "true")
    os.environ.setdefault("STREAMLIT_FILE_WATCHER_TYPE", "none")

    warnings.filterwarnings("ignore")
    warnings.filterwarnings("ignore", message=".*torch._classes.*")

    if platform.system() == "Linux":
        try:
            import resource

            gb = 1024 * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (6 * gb, 8 * gb))
        except Exception as err:  # pragma: no cover - best effort safeguard
            logger.warning("Unable to cap memory usage: %s", err)
    elif platform.system() == "Darwin":
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        if loop.is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())


def setup_environment() -> None:
    """Load environment variables and ensure OpenAI credentials are available."""

    if ENV_FILE.exists():
        logger.info("Loading environment variables from %s", ENV_FILE)
        load_dotenv(ENV_FILE, override=True)
    else:
        load_dotenv()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY is not set. Provide it in the .env file or when prompted.")
        try:
            api_key = input("Introdu cheia OpenAI API (lasă gol pentru a anula): ").strip()
        except EOFError:  # pragma: no cover - interactive fallback
            api_key = ""
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            logger.info("OPENAI_API_KEY a fost setată pentru sesiunea curentă.")
        else:
            raise RuntimeError("OPENAI_API_KEY is required to launch the Streamlit assistant.")

    os.environ.setdefault("OPENAI_BASE_URL", "https://api.openai.com/v1")
    os.environ.setdefault("OPENAI_MODEL", "gpt-4o-mini")
    os.environ.setdefault("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


def bootstrap_directories() -> None:
    """Ensure the document and vector store directories exist."""

    documents_dir = PROJECT_ROOT / "data" / "documents"
    vector_store_dir = PROJECT_ROOT / "data" / "vector_store"
    documents_dir.mkdir(parents=True, exist_ok=True)
    vector_store_dir.mkdir(parents=True, exist_ok=True)
    logger.debug("Document directory: %s", documents_dir)
    logger.debug("Vector store directory: %s", vector_store_dir)


def launch_streamlit() -> None:
    """Spawn the Streamlit application."""

    streamlit_cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(PROJECT_ROOT / "app.py"),
        "--server.maxUploadSize=50",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false",
        "--client.showErrorDetails=true",
        "--server.fileWatcherType=none",
        "--server.port=8502",
    ]

    try:
        subprocess.run(streamlit_cmd, check=True)
    except subprocess.CalledProcessError as err:
        logger.error("Streamlit failed to start: %s", err)
        raise


def main() -> None:
    """Entry point invoked from the command line."""

    logger.info("Initializare Longevity & Wellness Assistant cu OpenAI...")

    if not check_dependencies():
        raise SystemExit(1)

    setup_environment()
    set_memory_optimizations()
    bootstrap_directories()
    launch_streamlit()


if __name__ == "__main__":
    main()
