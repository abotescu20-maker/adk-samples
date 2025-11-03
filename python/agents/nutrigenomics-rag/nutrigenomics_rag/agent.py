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
"""Root agent configuration for the Nutrigenomics RAG assistant."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag

from .prompts import return_instructions_root

load_dotenv()

nutrigenomics_retrieval = VertexAiRagRetrieval(
    name="retrieve_nutrigenomics_evidence",
    description=(
        "Use this tool to retrieve genomics, nutraceutical, fitness, and longevity guidance "
        "from the configured Vertex AI RAG corpus when formulating a response."
    ),
    rag_resources=[
        rag.RagResource(
            rag_corpus=os.environ.get("RAG_CORPUS"),
        )
    ],
    similarity_top_k=12,
    vector_distance_threshold=0.55,
)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="nutrigenomics_rag_agent",
    instruction=return_instructions_root(),
    tools=[nutrigenomics_retrieval],
)

__all__ = ["root_agent"]
