# Nutrigenomics RAG Agent

## Overview

The Nutrigenomics RAG agent combines Vertex AI Retrieval-Augmented Generation
with a curated corpus of genomic variant annotations, nutritional guidance,
supplement research, exercise protocols, and longevity therapies. It is designed
for health coaches, clinicians, and researchers who want fast access to
actionable, evidence-backed recommendations that map genetic insights to
personalised lifestyle strategies.

## Availability

This agent sample ships with the open-source `adk-samples` repository. After
cloning the repo, you can find the complete project under
`python/agents/nutrigenomics-rag`. Follow the setup instructions below to run it
locally through the ADK CLI or Dev UI, or adapt the configuration for your own
deployment pipeline.

The agent:

- Interprets mutation-level details (e.g., SNP IDs, amino-acid changes,
  metabolic pathways) provided by the user.
- Retrieves supporting literature and protocols from Vertex AI RAG Engine.
- Synthesises the retrieved information into structured recommendations across
  diet, supplementation, movement, recovery, and longevity interventions.
- Surfaces contraindications, dosage ranges, and follow-up testing guidance when
  present in the corpus.
- Encourages users to verify actions with qualified healthcare professionals.

> **Disclaimer:** This agent is for educational purposes only and does not
> provide medical advice. Always consult a licensed professional before making
> health decisions based on genetic information.

## Quickstart Commands

Follow the sequence that matches how you want to experiment with the agent. In
both cases start from a terminal that is already inside the project folder:

```bash
cd adk-samples/python/agents/nutrigenomics-rag
```

### Local ADK run (Vertex AI backend)

```bash
cp .env.example .env               # fill in Vertex AI variables after copying
poetry install                     # set up the virtual environment
poetry run adk run nutrigenomics_rag
```

### Streamlit UI with OpenAI API

```bash
cp .env.example .env               # add OPENAI_API_KEY and related values
poetry install --with streamlit_runner
poetry run python streamlit_runner/longevity_assistant.py
```

### Docker container (Vertex AI backend)

```bash
cp .env.example .env               # include GOOGLE_CLOUD_PROJECT, RAG_CORPUS, etc.
docker build -t nutrigenomics-rag .
docker run -it --env-file .env \
  -v "$PWD/gcloud-key.json:/gcloud/key.json:ro" \
  -e GOOGLE_APPLICATION_CREDENTIALS=/gcloud/key.json \
  nutrigenomics-rag
```

Each block includes every command needed to get to a running assistant for that
workflow. Review the detailed sections below if you need extra context or
troubleshooting tips.

## Export or Download the Agent Bundle

If you want a single archive that you can transfer to another machine (for
example, to upload directly into Google AI Studio or keep as a backup), use the
packaging helper inside this folder:

```bash
cd adk-samples/python/agents/nutrigenomics-rag
python3 tools/export_bundle.py
```

The script creates `nutrigenomics_agent_bundle.zip` alongside the project. Pass
`--output /path/to/name` if you want to place the archive somewhere else. The
zip contains the Dockerfile, README, agent sources, Streamlit runner, tests, and
environment template so you can download or share the entire agent with a
single file.

## Agent Details

| Attribute             | Details |
| :-------------------- | :------ |
| **Interaction Type**  | Conversational |
| **Complexity**        | Intermediate |
| **Agent Type**        | Single agent |
| **Components**        | Vertex AI RAG tool |
| **Vertical**          | Precision health |

## Project Structure

```
python/agents/nutrigenomics-rag/
├── .env.example              # Environment variable template
├── README.md                 # This file
├── nutrigenomics_rag/
│   ├── __init__.py
│   ├── agent.py              # Root agent configuration
│   └── prompts.py            # Instruction prompt for the agent
├── pyproject.toml            # Poetry configuration
└── tests/
    └── __init__.py           # Placeholder for future tests
```

## Setup and Installation

### Prerequisites

- [Python 3.11](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)
- Access to [Vertex AI](https://cloud.google.com/vertex-ai) with the RAG Engine
  API enabled
- A configured RAG corpus that contains your nutrigenomics content

### 1. Clone the repository

```bash
git clone https://github.com/google/adk-samples.git
cd adk-samples
```

Verify that the agent directory exists before entering it:

```bash
ls python/agents
```

You should see `nutrigenomics-rag` in the output. Then move into the agent
folder:

```bash
cd python/agents/nutrigenomics-rag
```

> **macOS Terminal checklist**
>
> If you are following these steps from a fresh terminal session on macOS,
> run the commands exactly as shown below (press `Enter` after each line):
>
> ```bash
> pwd                      # confirm you are inside ~/adk-samples after cloning
> ls python/agents         # verify nutrigenomics-rag is listed
> cd python/agents/nutrigenomics-rag
> pwd                      # should now end with /python/agents/nutrigenomics-rag
> ```
>
> Seeing a different path? Use `cd ~/adk-samples` (or the folder where you
> cloned the repo) before continuing. This prevents `cd` or `docker build`
> from failing because the Dockerfile cannot be located.

### 2. Configure environment variables

Copy the template and fill in the required values.

```bash
cp .env.example .env
```

Required variables for the default Vertex AI setup:

- `GOOGLE_GENAI_USE_VERTEXAI=1` – Forces Vertex AI backend usage.
- `GOOGLE_CLOUD_PROJECT` – Google Cloud project ID that hosts Vertex AI.
- `GOOGLE_CLOUD_LOCATION` – Region for the RAG resources (e.g. `us-central1`).
- `RAG_CORPUS` – Resource name of the Vertex AI RAG corpus containing your
  nutrigenomics documents.

Optional variables for the OpenAI-powered Streamlit runner described later in
this document:

- `OPENAI_API_KEY` – The key for your OpenAI account.
- `OPENAI_BASE_URL` – Override the base URL if you are using a compatible
  OpenAI endpoint (defaults to the public API).
- `OPENAI_MODEL` – Chat model to call (defaults to `gpt-4o-mini`).
- `EMBEDDING_MODEL` – HuggingFace embedding model used to index PDFs (defaults
  to `sentence-transformers/all-MiniLM-L6-v2`).

Optional for deployment: `STAGING_BUCKET`, `AGENT_ENGINE_ID` (if you reuse the
deployment scripts from the base RAG sample).

### 3. Install dependencies

```bash
poetry install
```

This command installs the agent dependencies into an isolated Poetry virtual
environment.

### 4. Activate the virtual environment (optional)

```bash
poetry shell
```

Alternatively, use `poetry run` to execute commands without activating the shell.

### 5. Run the agent locally with ADK

From the project root:

```bash
poetry run adk run nutrigenomics_rag
```

You can also launch the ADK Dev UI:

```bash
poetry run adk web nutrigenomics_rag
```

Select the Nutrigenomics RAG agent from the dropdown and start chatting.

### Optional: Launch the Longevity & Wellness Streamlit UI with OpenAI

If you prefer a Streamlit dashboard that calls the OpenAI API instead of
Vertex AI, the project ships with a standalone runner inspired by the script you
shared. It keeps the local FAISS knowledge base, but removes all Azure-specific
requirements.

1. Install the extra dependencies:

   ```bash
   poetry install --with streamlit_runner
   ```

2. Set the OpenAI credentials in `.env` (copy from `.env.example` if you have
   not already):

   ```bash
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4o-mini
   # Optional overrides:
   # OPENAI_BASE_URL=https://api.openai.com/v1
   # EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   ```

3. Drop your reference PDFs into
   `streamlit_runner/src/data/documents/`.

4. Start the Streamlit assistant:

   ```bash
   poetry run python streamlit_runner/longevity_assistant.py
   ```

The app runs on port `8502` by default. Each time you add new PDFs, rerun the
command so the FAISS index is rebuilt. Responses are generated via the OpenAI
Chat Completions API—no Azure endpoints are required.

## Run the agent with Docker

Docker support is useful when you want to package the agent with its
dependencies and run it in a reproducible environment (for example inside your
own infrastructure or on Cloud Run).

1. Create an `.env` file (see step 2 above) that includes the Vertex AI project
   configuration and any additional variables you use at runtime.
2. Build the image from the project root:

   ```bash
   # Make sure your current directory contains the Dockerfile
   pwd
   # .../adk-samples/python/agents/nutrigenomics-rag

   docker build -t nutrigenomics-rag .
   ```

   On macOS you can run the full sequence in one block after opening Terminal:

   ```bash
   cd ~/adk-samples/python/agents/nutrigenomics-rag
   pwd
   docker build -t nutrigenomics-rag .
   ```

   If the last command fails with `open Dockerfile: no such file or directory`,
   double-check that `pwd` still ends in `/python/agents/nutrigenomics-rag`.

3. Run the container, providing the environment variables and credentials. The
   example below mounts a local service-account key that has access to Vertex
   AI. Replace the path with your credential file or rely on Workload Identity
   if you deploy on Google Cloud:

   ```bash
   docker run -it \
     --env-file .env \
     -v "$PWD/gcloud-key.json:/gcloud/key.json:ro" \
     -e GOOGLE_APPLICATION_CREDENTIALS=/gcloud/key.json \
     nutrigenomics-rag
   ```

The container entrypoint runs `adk run nutrigenomics_rag`, so once the
container starts you can begin chatting with the agent from your terminal. Use
`docker logs` to follow the conversation or override the entrypoint if you would
rather launch the Dev UI, for example:

```bash
docker run -it \
  --env-file .env \
  --entrypoint poetry \
  nutrigenomics-rag \
  run adk web nutrigenomics_rag
```

## Customising the Corpus

Use the helper script from the base RAG sample if you need to create a corpus
programmatically:

```bash
python nutrigenomics_rag/shared_libraries/prepare_corpus_and_data.py
```

Update the script with your dataset URLs, file names, and corpus descriptions to
upload nutrigenomics literature, lab interpretation guides, supplement
protocols, and exercise programming resources.

## Next Steps

- Add evaluation datasets that cover common nutrigenomics scenarios (e.g.
  methylation, detoxification, endurance training adaptations).
- Implement automated testing around tool invocation and response formatting.
- Extend the instructions for multilingual support if you plan to serve users in
  multiple languages.

## Troubleshooting on macOS Terminal

- **`cd: no such file or directory: adk-samples/python/agents/nutrigenomics-rag`** –
  Ensure the repository was cloned successfully and that you are running the
  command from the same folder where the `adk-samples` directory was created.
  Use `ls` to confirm the path exists before changing directories.
- **`failed to read dockerfile: open Dockerfile: no such file or directory`** –
  Run `pwd` to confirm you are inside `adk-samples/python/agents/nutrigenomics-rag`
  (the folder that contains the Dockerfile) before running `docker build`.
- **Docker Desktop not running** – If `docker build` hangs or reports that the
  daemon is unavailable, open Docker Desktop and verify the whale icon shows as
  “Running” before retrying the command.
