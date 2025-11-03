# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utility script for bootstrapping a nutrigenomics RAG corpus."""

from __future__ import annotations

import os
import tempfile

import requests
import vertexai
from dotenv import load_dotenv, set_key
from google.api_core.exceptions import ResourceExhausted
from google.auth import default
from vertexai.preview import rag

# Load environment variables from .env file
load_dotenv()

# --- Please fill in your configurations ---
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID:
    raise ValueError(
        "GOOGLE_CLOUD_PROJECT environment variable not set. Please set it in your .env file."
    )

LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
if not LOCATION:
    raise ValueError(
        "GOOGLE_CLOUD_LOCATION environment variable not set. Please set it in your .env file."
    )

CORPUS_DISPLAY_NAME = "Nutrigenomics_Primer_Corpus"
CORPUS_DESCRIPTION = "Reference material covering nutrigenomics principles and lifestyle interventions."
PDF_URL = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3257702/pdf/nihms353847.pdf"
PDF_FILENAME = "nutrigenomics_primer.pdf"
ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


# --- Start of the script ---
def initialize_vertex_ai() -> None:
    """Initialise Vertex AI with Application Default Credentials."""

    credentials, _ = default()
    vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)


def create_or_get_corpus() -> rag.Corpus:
    """Create a new corpus or reuse one with the same display name."""

    embedding_model_config = rag.EmbeddingModelConfig(
        publisher_model="publishers/google/models/text-embedding-004"
    )
    existing_corpora = rag.list_corpora()
    for existing_corpus in existing_corpora:
        if existing_corpus.display_name == CORPUS_DISPLAY_NAME:
            print(f"Found existing corpus with display name '{CORPUS_DISPLAY_NAME}'")
            return existing_corpus

    corpus = rag.create_corpus(
        display_name=CORPUS_DISPLAY_NAME,
        description=CORPUS_DESCRIPTION,
        embedding_model_config=embedding_model_config,
    )
    print(f"Created new corpus with display name '{CORPUS_DISPLAY_NAME}'")
    return corpus


def download_pdf_from_url(url: str, output_path: str) -> str:
    """Download a PDF file from the specified URL."""

    print(f"Downloading PDF from {url}...")
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()

    with open(output_path, "wb") as file_handle:
        for chunk in response.iter_content(chunk_size=8192):
            file_handle.write(chunk)

    print(f"PDF downloaded successfully to {output_path}")
    return output_path


def upload_pdf_to_corpus(
    corpus_name: str, pdf_path: str, display_name: str, description: str
) -> rag.File | None:
    """Upload a PDF file to the specified corpus."""

    print(f"Uploading {display_name} to corpus...")
    try:
        rag_file = rag.upload_file(
            corpus_name=corpus_name,
            path=pdf_path,
            display_name=display_name,
            description=description,
        )
        print(f"Successfully uploaded {display_name} to corpus")
        return rag_file
    except ResourceExhausted as exc:
        print(f"Error uploading file {display_name}: {exc}")
        print(
            "\nThis error suggests that you have exceeded the API quota for the embedding model."
        )
        print("This is common for new Google Cloud projects.")
        print(
            "Please review the Vertex AI quotas documentation and request an increase if needed."
        )
        return None
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error uploading file {display_name}: {exc}")
        return None


def update_env_file(corpus_name: str, env_file_path: str) -> None:
    """Update the .env file with the generated corpus resource name."""

    try:
        set_key(env_file_path, "RAG_CORPUS", corpus_name)
        print(f"Updated RAG_CORPUS in {env_file_path} to {corpus_name}")
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error updating .env file: {exc}")


def list_corpus_files(corpus_name: str) -> None:
    """List files already present in the specified corpus."""

    files = list(rag.list_files(corpus_name=corpus_name))
    print(f"Total files in corpus: {len(files)}")
    for file in files:
        print(f"File: {file.display_name} - {file.name}")


def main() -> None:
    """Entry point for preparing the nutrigenomics corpus."""

    initialize_vertex_ai()
    corpus = create_or_get_corpus()

    update_env_file(corpus.name, ENV_FILE_PATH)

    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_path = os.path.join(temp_dir, PDF_FILENAME)
        download_pdf_from_url(PDF_URL, pdf_path)

        upload_pdf_to_corpus(
            corpus_name=corpus.name,
            pdf_path=pdf_path,
            display_name=PDF_FILENAME,
            description="Review article on nutrigenomics and personalised nutrition.",
        )

    list_corpus_files(corpus_name=corpus.name)


if __name__ == "__main__":
    main()
