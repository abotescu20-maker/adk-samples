"""Streamlit UI for the Longevity & Wellness assistant backed by the OpenAI API."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence

import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from openai import OpenAI

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data" / "documents"
VECTOR_DIR = APP_DIR / "data" / "vector_store"
DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
DEFAULT_EMBEDDING_MODEL = os.environ.get(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)


@st.cache_resource(show_spinner=False)
def load_embeddings(model_name: str) -> HuggingFaceEmbeddings:
    """Load the HuggingFace embeddings used for document indexing."""

    return HuggingFaceEmbeddings(model_name=model_name)


def _load_documents() -> list:
    """Load PDF documents from the data directory."""

    documents = []
    for file_path in sorted(DATA_DIR.glob("*.pdf")):
        loader = PyPDFLoader(str(file_path))
        documents.extend(loader.load())
    return documents


@st.cache_resource(show_spinner=False)
def get_vector_store(embedding_model: str) -> FAISS | None:
    """Load an existing FAISS index or build a new one from PDF documents."""

    embeddings = load_embeddings(embedding_model)
    if (VECTOR_DIR / "index.faiss").exists():
        return FAISS.load_local(
            str(VECTOR_DIR), embeddings, allow_dangerous_deserialization=True
        )

    docs = _load_documents()
    if not docs:
        return None

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = splitter.split_documents(docs)
    vector_store = FAISS.from_documents(split_docs, embeddings)
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(VECTOR_DIR))
    return vector_store


def retrieve_context(vector_store: FAISS, query: str, k: int = 4) -> Sequence[str]:
    """Retrieve the top chunks relevant to the query."""

    docs = vector_store.similarity_search(query, k=k)
    return [doc.page_content for doc in docs]


def call_openai(model: str, base_url: str, api_key: str, prompt: str) -> str:
    """Call the OpenAI chat completion API with the given prompt."""

    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url
    client = OpenAI(**client_kwargs)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a medical research assistant specialised in longevity, dermatology, "
                    "and wellness. Provide clear, evidence-informed guidance and note when the "
                    "user should consult a medical professional."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content


def main() -> None:
    st.set_page_config(page_title="Longevity & Wellness Assistant", layout="wide")
    st.title("Longevity & Wellness Assistant (OpenAI)")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        st.error(
            "OPENAI_API_KEY nu este setată. Configurează cheia în fișierul .env sau în mediul curent."
        )
        return

    with st.sidebar:
        st.header("Configurație OpenAI")
        model_name = st.text_input("Model", value=DEFAULT_MODEL)
        base_url = st.text_input("Base URL", value=DEFAULT_BASE_URL)
        embedding_model = st.text_input("Model embedare", value=DEFAULT_EMBEDDING_MODEL)
        st.markdown(
            "Încărcați fișiere PDF în folderul `streamlit_runner/src/data/documents` și reîmprospătați aplicația "
            "pentru a reconstrui indexul."
        )

    vector_store = get_vector_store(embedding_model)

    if vector_store is None:
        st.info(
            "Nu au fost găsite documente PDF pentru a construi baza de cunoștințe. Adaugă fișiere în `data/documents` "
            "și reîncarcă pagina."
        )

    query = st.text_area(
        "Introdu întrebarea ta despre mutații, suplimente sau protocoale de longevitate:", height=150
    )

    if st.button("Generează recomandări", type="primary"):
        if not query.strip():
            st.warning("Te rugăm să introduci o întrebare.")
            return

        context_chunks: Sequence[str] = []
        if vector_store is not None:
            context_chunks = retrieve_context(vector_store, query)

        context = "\n\n".join(context_chunks)
        prompt = (
            "Context relevant din biblioteca ta:\n"
            f"{context}\n\n" if context else ""
        ) + (
            "Folosește contextul de mai sus (dacă este disponibil) pentru a răspunde la întrebarea utilizatorului.\n"
            "Structura recomandările pe domenii: nutriție, suplimente, activitate fizică, recuperare, monitorizare și alte terapii relevante.\n"
            f"Întrebare: {query}"
        )

        with st.spinner("Se generează răspunsul..."):
            try:
                answer = call_openai(model_name, base_url, api_key, prompt)
            except Exception as err:  # pragma: no cover - dependent on OpenAI service
                st.error(f"Eroare la apelarea OpenAI: {err}")
                return

        st.markdown("### Răspuns")
        st.write(answer)

        if context_chunks:
            with st.expander("Pasaje utilizate din documente"):
                for idx, chunk in enumerate(context_chunks, start=1):
                    st.markdown(f"**Fragment {idx}:**\n{chunk}")


if __name__ == "__main__":
    main()
