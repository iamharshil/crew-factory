"""Command-line interface for the AI software factory."""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

from litellm.exceptions import APIError

from software_factory.config import ConfigurationError, PROJECT_ROOT
from software_factory.crew import create_crew

OUTPUT_ROOT = PROJECT_ROOT / "output"
PROJECT_NAME_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
RELEASE_STATUSES = {
    "STATUS: READY",
    "STATUS: READY_WITH_LIMITATIONS",
    "STATUS: BLOCKED",
}
logger = logging.getLogger(__name__)


def _slugify_idea(idea: str) -> str:
    """Derive a filesystem-safe project name from the idea."""
    slug = re.sub(r"[^a-z0-9]+", "-", idea.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)[:48].strip("-")
    return slug or "generated-project"


def _project_output_dir(project_name: str) -> Path:
    """Create and validate a project directory under the repository output."""
    if not PROJECT_NAME_PATTERN.fullmatch(project_name):
        raise ValueError(
            "Project name must contain lowercase letters, digits, and "
            "single hyphens only."
        )

    repository_root = PROJECT_ROOT.resolve()
    output_root = OUTPUT_ROOT.resolve()
    try:
        output_root.relative_to(repository_root)
    except ValueError as error:
        raise ValueError("The output directory must remain inside the repository.") from error

    output_root.mkdir(parents=True, exist_ok=True)
    project_dir = (output_root / project_name).resolve()
    try:
        project_dir.relative_to(output_root)
    except ValueError as error:
        raise ValueError("The project output path escapes the output directory.") from error

    if project_dir.exists() and any(project_dir.iterdir()):
        raise FileExistsError(
            f"Output directory is not empty: {project_dir}. "
            "Choose a new --project-name rather than mixing with prior output."
        )
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Generate a runnable software project from a product idea."
    )
    parser.add_argument(
        "--idea",
        required=True,
        help="Raw product idea for the software factory to implement.",
    )
    parser.add_argument(
        "--project-name",
        help="Optional lowercase project slug; defaults to a slug of the idea.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed CrewAI agent and task logs.",
    )
    return parser


def _read_release_status(report_path: Path) -> str:
    """Read and validate a release report's machine-readable status line."""
    if not report_path.is_file():
        raise FileNotFoundError(f"Required release report is missing: {report_path}")
    lines = report_path.read_text(encoding="utf-8").splitlines()
    status = lines[0].strip() if lines else ""
    if status not in RELEASE_STATUSES:
        raise ValueError(
            f"{report_path.name} must begin with a recognized STATUS line."
        )
    return status


def _validate_release_artifacts(output_dir: Path) -> str:
    """Ensure release management cannot override QA's blocked status."""
    qa_status = _read_release_status(output_dir / "REVIEW.md")
    release_status = _read_release_status(output_dir / "RELEASE_READINESS.md")
    if qa_status == "STATUS: BLOCKED" and release_status != "STATUS: BLOCKED":
        raise ValueError(
            "Release readiness cannot override a blocked QA review."
        )
    if (
        qa_status == "STATUS: READY_WITH_LIMITATIONS"
        and release_status == "STATUS: READY"
    ):
        raise ValueError(
            "Release readiness cannot claim READY while QA reports limitations."
        )
    return release_status


def main(argv: list[str] | None = None) -> int:
    """Run the factory, returning a process status code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    idea = args.idea.strip()
    if not idea:
        parser.error("--idea must not be empty or whitespace.")

    project_name = args.project_name or _slugify_idea(idea)
    try:
        output_dir = _project_output_dir(project_name)
        crew = create_crew(output_dir, verbose=args.verbose)
    except (ConfigurationError, OSError, ValueError) as error:
        print(f"Unable to prepare project output: {error}", file=sys.stderr)
        return 2

    try:
        result = crew.kickoff(
            inputs={
                "idea": idea,
                "project_name": project_name,
                "output_dir": str(output_dir),
            }
        )
    except (APIError, OSError, RuntimeError, ValueError):
        logger.exception("Software factory pipeline execution failed.")
        print(
            f"Pipeline execution failed. Inspect logs and partial output in {output_dir}.",
            file=sys.stderr,
        )
        return 1

    print(f"\nGenerated project: {output_dir}")
    print(result)
    try:
        status = _validate_release_artifacts(output_dir)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Release gate failed: {error}", file=sys.stderr)
        return 3
    if status == "STATUS: BLOCKED":
        print(
            f"Release blocked. Review {output_dir / 'RELEASE_READINESS.md'} "
            "and address the listed "
            "findings before using the generated project.",
            file=sys.stderr,
        )
        return 3

    if status == "STATUS: READY_WITH_LIMITATIONS":
        print(
            f"Generated project is ready with disclosed limitations. "
            f"Review {output_dir / 'RELEASE_READINESS.md'} before use."
        )
    else:
        print(f"Release gate passed: {output_dir / 'RELEASE_READINESS.md'}")
    return 0
