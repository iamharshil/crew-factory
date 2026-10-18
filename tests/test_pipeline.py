from __future__ import annotations

import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from crewai import Process

from software_factory import cli
from software_factory.crew import create_crew
from software_factory.tools import create_research_tools


class PipelineTests(unittest.TestCase):
    def test_company_pipeline_has_ordered_review_and_release_gates(self) -> None:
        credentials = {
            "ANTHROPIC_API_KEY": "test-anthropic",
            "OPENAI_API_KEY": "test-openai",
            "OPENROUTER_API_KEY": "test-openrouter",
            "GEMINI_API_KEY": "test-gemini",
        }
        with tempfile.TemporaryDirectory() as temporary:
            with patch.dict(os.environ, credentials, clear=True):
                crew = create_crew(Path(temporary))

        self.assertEqual(crew.process, Process.sequential)
        self.assertEqual(len(crew.agents), 22)
        self.assertEqual(len(crew.tasks), 37)
        self.assertFalse(crew.verbose)
        self.assertTrue(all(not agent.verbose for agent in crew.agents))

        task_positions = {id(task): index for index, task in enumerate(crew.tasks)}
        context_sizes = []
        for index, task in enumerate(crew.tasks):
            self.assertTrue(task.expected_output.strip())
            if isinstance(task.context, list):
                context_sizes.append(len(task.context))
                for prerequisite in task.context:
                    self.assertIn(id(prerequisite), task_positions)
                    self.assertLess(task_positions[id(prerequisite)], index)
        self.assertLessEqual(max(context_sizes), 6)

        task_descriptions = [task.description for task in crew.tasks]
        product_spec_index = next(
            i for i, description in enumerate(task_descriptions)
            if "write the product" in description.lower()
        )
        product_review_index = next(
            i for i, description in enumerate(task_descriptions)
            if "read product_spec.md and review it" in description.lower()
        )
        product_revision_index = next(
            i for i, description in enumerate(task_descriptions)
            if "read product_review.md and product_spec.md" in description.lower()
        )
        architecture_index = next(
            i for i, description in enumerate(task_descriptions)
            if "write the complete architecture" in description.lower()
        )
        architecture_review_index = next(
            i for i, description in enumerate(task_descriptions)
            if "write architecture_review.md" in description.lower()
        )
        architecture_revision_index = next(
            i for i, description in enumerate(task_descriptions)
            if "write architecture_decisions.md" in description.lower()
        )
        self.assertLess(product_spec_index, product_review_index)
        self.assertLess(product_review_index, product_revision_index)
        self.assertLess(architecture_index, architecture_review_index)
        self.assertLess(architecture_review_index, architecture_revision_index)

        role_names = {agent.role for agent in crew.agents}
        self.assertIn("Product Research Analyst", role_names)
        self.assertIn("Engineering Research Analyst", role_names)
        self.assertIn("Continuous Improvement Engineer", role_names)
        self.assertIn("Release Manager / Engineering Director", role_names)

        task_agents = [task.agent.role for task in crew.tasks]
        self.assertIn("Backend Engineering Senior", task_agents)
        self.assertIn("Backend Engineering Junior", task_agents)
        self.assertIn("Independent Principal Engineer / Code Reviewer", task_agents)
        self.assertEqual(
            task_agents[-3:],
            [
                "Continuous Improvement Engineer",
                "QA Department Senior / Test Lead",
                "Release Manager / Engineering Director",
            ],
        )
        self.assertEqual(
            task_agents[-1],
            "Release Manager / Engineering Director",
        )

    def test_live_research_tool_is_optional(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(create_research_tools(), [])
        with patch.dict(os.environ, {"SERPER_API_KEY": "test-serper"}, clear=True):
            self.assertEqual(
                [tool.name for tool in create_research_tools()],
                ["Search the internet with Serper"],
            )

    def test_cli_blocks_release_without_valid_readiness_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output_dir = Path(temporary)
            for name in cli.REQUIRED_DELIVERABLES:
                (output_dir / name).write_text("Required deliverable.\n", encoding="utf-8")
            (output_dir / "ARCHITECTURE_DECISIONS.md").write_text(
                "STATUS: ACCEPT\nNo unresolved blockers.\n",
                encoding="utf-8",
            )
            mocked_crew = SimpleNamespace(kickoff=Mock(return_value="completed"))
            with (
                patch.object(cli, "_project_output_dir", return_value=output_dir),
                patch.object(cli, "create_crew", return_value=mocked_crew),
                redirect_stdout(StringIO()),
                redirect_stderr(StringIO()),
            ):
                self.assertEqual(cli.main(["--idea", "example"]), 3)

            (output_dir / "REVIEW.md").write_text(
                "STATUS: BLOCKED\nUnresolved blocker.\n",
                encoding="utf-8",
            )
            (output_dir / "RELEASE_READINESS.md").write_text(
                "STATUS: BLOCKED\nUnresolved high severity finding.\n",
                encoding="utf-8",
            )
            with (
                patch.object(cli, "_project_output_dir", return_value=output_dir),
                patch.object(cli, "create_crew", return_value=mocked_crew),
                redirect_stdout(StringIO()),
                redirect_stderr(StringIO()),
            ):
                self.assertEqual(cli.main(["--idea", "example"]), 3)

            (output_dir / "REVIEW.md").write_text(
                "STATUS: READY_WITH_LIMITATIONS\nTests not executed.\n",
                encoding="utf-8",
            )
            (output_dir / "RELEASE_READINESS.md").write_text(
                "STATUS: READY\n",
                encoding="utf-8",
            )
            with (
                patch.object(cli, "_project_output_dir", return_value=output_dir),
                patch.object(cli, "create_crew", return_value=mocked_crew),
                redirect_stdout(StringIO()),
                redirect_stderr(StringIO()),
            ):
                self.assertEqual(cli.main(["--idea", "example"]), 3)

            (output_dir / "REVIEW.md").write_text(
                "STATUS: BLOCKED\nUnresolved blocker.\n",
                encoding="utf-8",
            )
            (output_dir / "RELEASE_READINESS.md").write_text(
                "STATUS: READY\n",
                encoding="utf-8",
            )
            with (
                patch.object(cli, "_project_output_dir", return_value=output_dir),
                patch.object(cli, "create_crew", return_value=mocked_crew),
                redirect_stdout(StringIO()),
                redirect_stderr(StringIO()),
            ):
                self.assertEqual(cli.main(["--idea", "example"]), 3)

            (output_dir / "REVIEW.md").write_text(
                "STATUS: READY_WITH_LIMITATIONS\nTests not executed.\n",
                encoding="utf-8",
            )
            (output_dir / "RELEASE_READINESS.md").write_text(
                "STATUS: READY_WITH_LIMITATIONS\nTests not executed.\n",
                encoding="utf-8",
            )
            with (
                patch.object(cli, "_project_output_dir", return_value=output_dir),
                patch.object(cli, "create_crew", return_value=mocked_crew),
                redirect_stdout(StringIO()),
                redirect_stderr(StringIO()),
            ):
                self.assertEqual(cli.main(["--idea", "example"]), 0)

    def test_release_gate_rejects_missing_deliverables_and_blocked_architecture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output_dir = Path(temporary)
            for name in cli.REQUIRED_DELIVERABLES:
                (output_dir / name).write_text("Required deliverable.\n", encoding="utf-8")
            (output_dir / "REVIEW.md").write_text(
                "STATUS: READY\nReview complete.\n",
                encoding="utf-8",
            )
            (output_dir / "RELEASE_READINESS.md").write_text(
                "STATUS: READY\nRelease approved.\n",
                encoding="utf-8",
            )
            (output_dir / "ARCHITECTURE_DECISIONS.md").write_text(
                "STATUS: ACCEPT\nNo unresolved blockers.\n",
                encoding="utf-8",
            )
            self.assertEqual(
                cli._validate_release_artifacts(output_dir),
                "STATUS: READY",
            )

            (output_dir / "ARCHITECTURE_DECISIONS.md").write_text(
                "STATUS: BLOCKED\nUnresolved high-severity finding.\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "blocked architecture"):
                cli._validate_release_artifacts(output_dir)

            (output_dir / "ARCHITECTURE_DECISIONS.md").write_text(
                "STATUS: ACCEPT\nNo unresolved blockers.\n",
                encoding="utf-8",
            )
            (output_dir / "HANDOFF.md").write_text("", encoding="utf-8")
            with self.assertRaisesRegex(FileNotFoundError, "HANDOFF.md"):
                cli._validate_release_artifacts(output_dir)

    def test_cli_reports_pipeline_failures_without_releasing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output_dir = Path(temporary)
            mocked_crew = SimpleNamespace(
                kickoff=Mock(side_effect=RuntimeError("provider request failed"))
            )
            with (
                patch.object(cli, "_project_output_dir", return_value=output_dir),
                patch.object(cli, "create_crew", return_value=mocked_crew),
                redirect_stdout(StringIO()),
                redirect_stderr(StringIO()),
            ):
                self.assertEqual(cli.main(["--idea", "example"]), 1)

    def test_existing_project_output_is_never_mixed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output_root = root / "output"
            existing_project = output_root / "existing-project"
            existing_project.mkdir(parents=True)
            (existing_project / "keep.txt").write_text("preserve", encoding="utf-8")

            with (
                patch.object(cli, "PROJECT_ROOT", root),
                patch.object(cli, "OUTPUT_ROOT", output_root),
            ):
                with self.assertRaises(FileExistsError):
                    cli._project_output_dir("existing-project")

            self.assertEqual(
                (existing_project / "keep.txt").read_text(encoding="utf-8"),
                "preserve",
            )


if __name__ == "__main__":
    unittest.main()
