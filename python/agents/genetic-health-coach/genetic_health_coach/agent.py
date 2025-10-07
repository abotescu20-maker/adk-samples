"""Main agent definition for the genetic health coach."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .prompt import genetic_health_coach_instruction
from .tools import build_subject_report, extract_gene_variants

root_agent = Agent(
    model="gemini-2.5-flash",
    name="genetic_health_coach_agent",
    instruction=genetic_health_coach_instruction,
    tools=[
        FunctionTool(func=extract_gene_variants),
        FunctionTool(func=build_subject_report),
    ],
)
