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
cd adk-samples/python/agents/nutrigenomics-rag
```

### 2. Configure environment variables

Copy the template and fill in the required values.

```bash
cp .env.example .env
```

Required variables:

- `GOOGLE_GENAI_USE_VERTEXAI=1` – Forces Vertex AI backend usage.
- `GOOGLE_CLOUD_PROJECT` – Google Cloud project ID that hosts Vertex AI.
- `GOOGLE_CLOUD_LOCATION` – Region for the RAG resources (e.g. `us-central1`).
- `RAG_CORPUS` – Resource name of the Vertex AI RAG corpus containing your
  nutrigenomics documents.
- Optional for deployment: `STAGING_BUCKET`, `AGENT_ENGINE_ID` (if you reuse the
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
