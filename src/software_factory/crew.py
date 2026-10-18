"""Factory for assembling and running the sequential software pipeline."""

from __future__ import annotations

from pathlib import Path

from crewai import Crew, Process

from software_factory.agents import create_agents
from software_factory.config import build_llm_settings
from software_factory.tasks import create_tasks


def create_crew(output_dir: Path, *, verbose: bool = False) -> Crew:
    """Assemble the configured agents and sequential task pipeline."""
    settings = build_llm_settings()
    agents = create_agents(settings, output_dir, verbose=verbose)
    tasks = create_tasks(agents, str(output_dir.resolve()))
    return Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,
        verbose=verbose,
    )
