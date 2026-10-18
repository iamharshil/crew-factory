# Change log

## 2026-10-19

### Initial Python environment

- Created `.venv` with `uv venv` using the available CPython 3.15.0 interpreter.
- Added `.venv/`, `__pycache__/`, and Python bytecode files to `.gitignore`.

### Project initialization and dependencies

- Initialized the `software-factory` project in the existing project folder with `uv init --name software-factory`; no `software-factory/` subfolder was created.
- Changed the project Python requirement to `>=3.12` and pinned Python 3.12 with `uv python pin 3.12`.
- The first dependency installation attempt under Python 3.15 failed because the selected `tiktoken` dependency required a Rust compiler to build.
- Recreated `.venv` with CPython 3.12.15 and successfully added `crewai` and `crewai-tools` with `uv add crewai crewai-tools`.
- Generated `uv.lock` and installed the project dependencies.
- Verified the lockfile with `uv sync --locked`, imported both CrewAI packages, and ran the `software-factory` project command.

### Summary

The current folder is now a `uv`-managed Python project named `software-factory` with CrewAI dependencies and a Python 3.12 virtual environment. Use `uv run` to run project commands, or activate the environment with:

```sh
source .venv/bin/activate
```

### AI Software Factory implementation

- Added the required provider keys to `.env.example` and configured `.env` to be ignored by Git.
- Added `python-dotenv` and `litellm` as direct dependencies.
- Implemented environment validation and four role-specific CrewAI LLM configurations using LiteLLM routing.
- Added file writer, file reader, and directory reader tools confined to each generated project directory.
- Implemented the product manager, tech lead, senior developer, and QA/security reviewer agents.
- Added four sequential tasks with explicit expected outputs and upstream task context.
- Added the Crew factory, root `main.py` CLI, project-name slugging, output path validation, and a `REVIEW.md` deliverable.
- Updated the installed `software-factory` entry point to use the CLI.

Validation completed: Python compilation, CLI help, required-key validation, `uv lock --check`, model setup, sequential Crew/task-context assembly, and output-scoped tool setup.

### Summary

Run `uv run python main.py --idea "Build a real-time URL shortener with rate limiting"` to generate a project under `output/<project_name>`. Copy `.env.example` to `.env` and configure all four provider keys before running the factory.

### README and setup documentation

- Replaced the empty README with project overview, requirements, `uv` installation steps, provider-key setup, CLI examples, pipeline description, generated output layout, troubleshooting, and development checks.
- Documented that all four provider keys are required and advised reviewing generated code before running it.

### Summary

Follow [README.md](./README.md) to install, configure, and run the software factory.

### Company departments and seniority

- Expanded the team from four agents to 17 distinct roles, including CEO, Product Manager, Design, Team Lead, Backend, Frontend, QA, DevOps/SRE, Analytics, Legal/Compliance, Accounting, and Engineering Intern.
- Added senior and junior roles for Design, Backend, Frontend, QA, and DevOps, each with distinct file-ownership and task boundaries.
- Expanded the sequential workflow to 18 deliverables, including executive brief, design documentation, architecture ownership matrix, implementation, test planning/tests, deployment and operations, analytics, preliminary legal/cost assessments, handoff, and final QA/security review.
- Updated the README with the company roster and role responsibilities. Technical departments may record a scope decision instead of adding unnecessary layers to a project.
- Verified construction of all 17 roles and 18 tasks, sequential process and tool assignment; also reran compilation, CLI help, lockfile, and whitespace checks.

### Summary

The factory now models the full department roster shown in the supplied team chart and includes explicit senior/junior responsibilities. Related roles reuse the four configured provider LLMs.

### Research, review, remediation, and release gating

- Added Product Research Analyst and Engineering Research Analyst roles. Live web search is available when the optional `SERPER_API_KEY` is configured; research instructions require citations for searched claims and explicit disclosure when search is unavailable.
- Added independent principal engineering review, Continuous Improvement Engineer, and Release Manager roles.
- Added product-spec and architecture review/revision stages before implementation.
- Added senior review and junior follow-up/remediation tasks for design tokens, backend work, frontend components, tests, and DevOps documentation/configuration.
- Added an independent technical review, bounded finding-driven remediation pass, final QA re-review, and release decision with machine-readable status.
- Updated the CLI to fail if readiness output is missing, malformed, or blocked, and made it refuse to mix output into an existing non-empty project directory.
- Updated README workflow, research configuration, quality limitations, and unit-test instructions; added regression tests for pipeline structure, optional research, output collision safety, and release gating.
- Validation records: 22 agents, 37 ordered tasks, explicit upstream context ordering, Python compilation, CLI, locked dependencies, and release-gate unit tests.
- Confirmed all 4 regression tests pass, the optional Serper tool initializes when configured, the CLI help succeeds, and lockfile/whitespace checks pass. Generated application code and model-driven reviews were not executed.
- Optimized ordinary CLI output by disabling verbose agent/task logging by default and exposing `--verbose` when detailed traces are needed.
- Reduced broad task-context fan-in in handoff/review/release stages while keeping required acceptance criteria and review dispositions available through scoped context plus on-disk inspection.
- Hardened the release gate to require valid statuses in both QA `REVIEW.md` and `RELEASE_READINESS.md`, prevent release management from overriding blocked/limited QA outcomes, and report known provider, I/O, runtime, and validation failures with traceback logging.
- Added tests for product/architecture review order, maximum task-context fan-in, QA/release status consistency, and pipeline failure handling.
- All 5 regression tests now pass. Validation also includes compilation, CLI help, `uv lock --check`, and `git diff --check`.

### Summary

The factory now uses a review-correct-release sequence with research and explicit bounded remediation. It does not execute generated code; reports and release status must disclose unexecuted tests/builds and require human review before deployment.
