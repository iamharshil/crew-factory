# AI Software Factory

An autonomous, sequential CrewAI pipeline that turns a product idea into a
project written to disk. The factory creates a product specification, plans an
architecture, writes a runnable project, and produces a QA/security report.

Generated projects are placed in `output/<project-name>/`.

## Requirements

- Python 3.12 or newer
- [`uv`](https://docs.astral.sh/uv/)
- API keys for Anthropic, OpenAI, OpenRouter, and Gemini

## Installation

From the repository root, install the project and its locked dependencies:

```sh
uv sync
```

Create a local environment file from the template:

```sh
cp .env.example .env
```

Edit `.env` and provide credentials for all four providers:

```dotenv
ANTHROPIC_API_KEY=your-anthropic-api-key
OPENAI_API_KEY=your-openai-api-key
OPENROUTER_API_KEY=your-openrouter-api-key
GEMINI_API_KEY=your-gemini-api-key
# Optional; enables live web research
SERPER_API_KEY=your-serper-api-key
```

The factory validates all four model-provider keys before starting. Keep `.env`
private; it is excluded from version control. For live web research, optionally
set `SERPER_API_KEY`; without it, research agents produce clearly labeled
provisional desk research and must not invent citations.

## Run

Pass the product idea with `--idea`:

```sh
uv run python main.py --idea "Build a real-time URL shortener with rate limiting"
```

The project name is derived from the idea by default. To choose a name
explicitly, pass a lowercase slug containing letters, digits, and hyphens:

```sh
uv run python main.py \
  --idea "Build a real-time URL shortener with rate limiting" \
  --project-name url-shortener
```

You can also use the installed project command:

```sh
uv run software-factory --idea "Build a real-time URL shortener with rate limiting"
```

The command creates the target under `output/` and runs a sequential company
pipeline. Each employee has a distinct role and assigned deliverable; related
employees share the configured provider model:

| Department / role | Responsibility |
| --- | --- |
| CEO | Sets product direction, business outcomes, and MVP priorities. |
| Product Research Analyst | Researches user/domain context and records evidence, sources, and gaps. |
| Engineering Research Analyst | Compares technical options and verifies source-backed technical claims when search is enabled. |
| Product Manager | Produces user stories, requirements, API contracts, and data schema. |
| Design Senior / Lead | Defines user journeys, interaction states, and accessibility. |
| Design Junior | Documents design tokens and component guidance. |
| Team Lead / Technology Lead | Owns architecture, exact file tree, and non-overlapping file assignments. |
| Independent Principal Engineer / Code Reviewer | Reviews the architecture and implementation independently. |
| Backend Senior | Implements backend domain behavior and interfaces. |
| Backend Junior | Implements assigned persistence, integration, and supporting tests. |
| Frontend Senior | Implements the application shell and user workflows. |
| Frontend Junior | Implements reusable, accessible UI components and styles. |
| QA Senior / Test Lead | Creates a test plan and performs the final on-disk audit. |
| QA Junior | Writes automated tests from the test plan. |
| DevOps Senior | Provides build, deployment, health-check, and runtime configuration. |
| DevOps Junior / SRE | Documents environment setup and operational procedures. |
| Analytics | Defines product metrics and privacy-conscious instrumentation. |
| Legal / Compliance Analyst | Flags preliminary privacy, licensing, and compliance considerations. |
| Accounting / Cost Analyst | Documents operating cost drivers and assumptions. |
| Engineering Intern | Verifies the project inventory and prepares a handoff. |
| Continuous Improvement Engineer | Remediates prioritized review findings in a bounded follow-up pass. |
| Release Manager / Engineering Director | Checks evidence and issues the final readiness decision. |

The 22 employees work through 37 ordered deliverables. Product research and
engineering research run before planning, with cited sources when live search
is configured. Product and architecture have review-and-revision steps before
implementation. Each junior's work is inspected by its senior, then corrected
from written findings. An independent principal-engineer review is followed by
a bounded remediation pass and a separate QA re-review. A release manager then
checks the reports and required files. The CLI exits unsuccessfully if the
release report is missing, malformed, or `STATUS: BLOCKED`.

The QA agents can inspect files but the factory does not execute generated
source, tests, builds, or deployment commands: executing model-generated code
without an isolated sandbox would be unsafe. The final reports must state this
limitation; the release manager can mark a project
`STATUS: READY_WITH_LIMITATIONS` only when remaining checks are non-blocking.
Review reports use blocker/high findings to block release. This is a
human-supervised quality workflow, not a guarantee of production readiness.
No model-generated status is a substitute for a human review of the generated
code, dependencies, and operational configuration.

When a technical layer is genuinely out of scope, the architecture assigns a
documented scope decision instead of requiring unnecessary infrastructure.
Legal and cost reports are preliminary analyses, not professional advice.

The generated project is written to `output/<project-name>/`. Existing
non-empty output directories are not overwritten; choose a new project name for
each run to avoid mixing generations. Review its source, dependencies,
`REVIEW.md`, and `RELEASE_READINESS.md` before running generated code. A blocked
release exits with status code `3`.

## Project layout

```text
.
├── .env.example
├── main.py
├── output/                    # Generated projects
├── src/software_factory/
│   ├── agents.py
│   ├── cli.py
│   ├── config.py
│   ├── crew.py
│   ├── tasks.py
│   └── tools.py
├── pyproject.toml
└── uv.lock
```

## Troubleshooting

- **Missing API key:** confirm `.env` exists in the repository root and all
  four provider keys are set.
- **Dependency or Python version mismatch:** run `uv sync` to synchronize the
  environment from `uv.lock`. This project requires Python 3.12 or newer.
- **Generated project already exists:** rerunning with the same project name
  targets the same `output/<project-name>/` directory. Inspect existing files
  before rerunning so you do not unintentionally mix generated output.

## Development checks

```sh
uv run python -m compileall -q src/software_factory main.py
uv lock --check
uv run python main.py --help
uv run python -m unittest discover -s tests
```
