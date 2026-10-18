"""Output-scoped file tools provided to the developer and QA agents."""

from __future__ import annotations

import os
from pathlib import Path

from crewai.tools import BaseTool
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    FileWriterTool,
    SerperDevTool,
)


def create_file_tools(output_dir: Path) -> list[BaseTool]:
    """Create file tools whose reads and writes are restricted to output_dir."""
    root = output_dir.resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Project output directory does not exist: {root}")

    return [
        FileWriterTool(
            base_dir=str(root),
            description=(
                "Write a UTF-8 text file inside the assigned project output "
                f"directory ({root}). Use a project-relative filename and "
                "set overwrite=true when updating a file."
            ),
        ),
        FileReadTool(
            base_dir=str(root),
            description=(
                "Read a UTF-8 text file from the assigned project output "
                f"directory ({root}) only."
            ),
        ),
        DirectoryReadTool(directory=str(root)),
    ]


def create_research_tools() -> list[BaseTool]:
    """Enable current web research when an optional Serper key is configured."""
    if not os.getenv("SERPER_API_KEY"):
        return []
    return [SerperDevTool(n_results=5)]
