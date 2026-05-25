import os
from typing import List
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource

# ==========================================
# 🛡️ SYSTEM CONFIGURATION: NVIDIA NIM PIPELINE
# ==========================================

# 1. The Brain (LLM reasoning model with gateway timeout protections)
NIM_LLM = LLM(
    model="openai/meta/llama-3.1-70b-instruct",
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ.get("NVIDIA_API_KEY"),
    timeout=600.0,
    max_tokens=4000,
    config=dict(
        connect_timeout=600.0,
        read_timeout=600.0
    )
)

# 2. Canonical Configuration for Native Knowledge Embedding
# This exact dictionary matches CrewAI's modern system specifications perfectly
knowledge_embedder_config = {
    "provider": "openai",
    "config": {
        "model": "nvidia/llama-nemotron-embed-1b-v2",
        "api_key": os.environ.get("NVIDIA_API_KEY"),
        "base_url": "https://integrate.api.nvidia.com/v1"
    }
}

# 3. Mount the PDF Target inside your native root context layout
pdf_source = PDFKnowledgeSource(
    file_paths=["in_context_learning.pdf"],  # Framework automatically looks inside your root knowledge/ folder
    chunk_size=1500,
    chunk_overlap=250,
)

# ==========================================
# 🤖 CREW ORCHESTRATION PIPELINE
# ==========================================

@CrewBase
class KnowledgeCrew():
    """KnowledgeCrew team for processing research data"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def researcher_summarization(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher_summarization"],
            verbose=True,
            llm=NIM_LLM  # Automatically inherits access to the global crew knowledge sources
        )

    @task
    def summarization_task(self) -> Task:
        return Task(
            config=self.tasks_config["summarization_task"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the KnowledgeCrew pipeline"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            knowledge_sources=[pdf_source],
            embedder=knowledge_embedder_config  # Direct, compliant parameter key mapping
        )