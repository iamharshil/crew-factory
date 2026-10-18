"""Company-wide sequential tasks for building, operating, and reviewing a project."""

from __future__ import annotations

from crewai import Agent, Task


def create_tasks(
    agents: dict[str, Agent],
    output_dir: str,
) -> list[Task]:
    """Build the research, implementation, review, and release pipeline."""
    product_research_task = Task(
        description=(
            "Research the market and user context for this idea: {idea}. "
            "Use live web search if available. Prefer primary sources, "
            "official documentation, and dated evidence. Record each source "
            "URL and the claim it supports in PRODUCT_RESEARCH.md inside "
            f"{output_dir}. Separate sourced facts, interpretation, and "
            "unknowns; do not invent user interviews, market sizes, competitor "
            "features, or citations. If search is unavailable, label the "
            "report as provisional desk research and state that current "
            "external facts were not verified."
        ),
        expected_output=(
            "PRODUCT_RESEARCH.md on disk with user/domain findings, attributable "
            "sources or a clear no-live-research limitation, assumptions, and "
            "open research questions."
        ),
        agent=agents["product_researcher"],
    )
    engineering_research_task = Task(
        description=(
            "Research technical options for the product idea: {idea}. Use "
            "live search if available; prioritize official project and "
            "security documentation, current stable versions, and primary "
            "sources. Compare relevant languages, frameworks, storage, "
            "authentication, deployment, and testing choices against likely "
            "requirements. Write TECHNICAL_RESEARCH.md inside "
            f"{output_dir}, with source URLs and retrieval context for "
            "externally verified claims, trade-offs, recommendations, and "
            "unknowns. If no search tool is available, label conclusions as "
            "provisional and do not fabricate citations or claim current "
            "version verification."
        ),
        expected_output=(
            "TECHNICAL_RESEARCH.md on disk with option comparisons, evidence "
            "and source URLs when searched, explicit assumptions, and a "
            "provisional recommendation."
        ),
        agent=agents["engineering_researcher"],
    )
    ceo_task = Task(
        description=(
            "Set an executive brief for this product idea: {idea}\n\n"
            "State the customer problem, target users, value proposition, "
            "business outcomes, measurable success indicators, MVP priorities, "
            "constraints, and major business risks. Consider product research; "
            "distinguish sourced evidence, inference, and assumptions. Do not "
            "invent market research or promise outcomes."
        ),
        expected_output=(
            "An executive brief with target customers, value proposition, "
            "business outcomes, measurable success indicators, MVP priorities, "
            "constraints, and clearly labeled assumptions."
        ),
        agent=agents["ceo"],
        context=[product_research_task],
    )
    product_task = Task(
        description=(
            "Using the original idea and CEO brief, write the product "
            f"specification to PRODUCT_SPEC.md inside {output_dir}. Include "
            "purpose and scope, user personas, "
            "numbered stories with acceptance criteria, functional and "
            "non-functional requirements, API contracts with request, response "
            "and error shapes, database entities and relationships, and "
            "explicit assumptions. Resolve reasonable ambiguities without "
            "adding unsupported facts, and map requirements to research or "
            "assumptions that justify them."
        ),
        expected_output=(
            "PRODUCT_SPEC.md on disk with a testable specification covering scope, personas, user "
            "stories, acceptance criteria, functional and non-functional "
            "requirements, API contracts, data schema, and assumptions."
        ),
        agent=agents["product_manager"],
        context=[product_research_task, ceo_task],
    )
    product_review_task = Task(
        description=(
            "Read PRODUCT_SPEC.md and review it against the idea, executive "
            "brief, and PRODUCT_RESEARCH.md. Check requirement traceability, "
            "scope, contradictions, testable acceptance criteria, API errors, "
            "data lifecycle/privacy, non-functional requirements, and "
            "unsupported market assertions. Write PRODUCT_REVIEW.md with "
            "section references, BLOCKER/HIGH/MEDIUM/LOW findings, and ACCEPT "
            "or REVISE."
        ),
        expected_output=(
            "PRODUCT_REVIEW.md on disk with requirements coverage, concrete "
            "findings, severity, and ACCEPT or REVISE."
        ),
        agent=agents["product_researcher"],
        context=[product_research_task, ceo_task, product_task],
    )
    product_revision_task = Task(
        description=(
            "Read PRODUCT_REVIEW.md and PRODUCT_SPEC.md. If the verdict is "
            "REVISE, update PRODUCT_SPEC.md to address all BLOCKER and HIGH "
            "findings and in-scope MEDIUM findings. Preserve traceability to "
            "sourced research or explicit assumptions. If ACCEPT, preserve "
            "the file. Reread the updated file and append a finding-by-finding "
            "disposition to PRODUCT_REVIEW.md. List unresolved decisions."
        ),
        expected_output=(
            "PRODUCT_SPEC.md containing the accepted/revised complete "
            "specification and PRODUCT_REVIEW.md with every finding's "
            "disposition and unresolved decisions."
        ),
        agent=agents["product_manager"],
        context=[product_task, product_review_task],
    )
    design_senior_task = Task(
        description=(
            "Translate the product specification and executive priorities into "
            "a UX design brief. Describe target-user journeys, information "
            "architecture, screen or interaction states, responsive behavior, "
            "accessibility requirements, and a cohesive visual direction. "
            f"Write the complete deliverable as DESIGN_SPEC.md inside {output_dir}. "
            "If the project has no user interface, explain why and define the "
            "appropriate non-visual user experience instead."
        ),
        expected_output=(
            "An on-disk DESIGN_SPEC.md describing UX journeys, interaction "
            "states, accessibility and responsive requirements, or a clear "
            "reasoned decision that a graphical interface is out of scope."
        ),
        agent=agents["design_senior"],
        context=[ceo_task, product_revision_task],
    )
    design_junior_task = Task(
        description=(
            "Use the approved UX brief to create practical design tokens and "
            "component guidance: typography, color, spacing, layout, component "
            "states, accessibility conventions, and responsive rules. Write "
            f"the result as DESIGN_TOKENS.md inside {output_dir}. If the "
            "project has no graphical interface, document that decision and "
            "any applicable terminal/API presentation conventions."
        ),
        expected_output=(
            "An on-disk DESIGN_TOKENS.md with implementation-ready design "
            "tokens and component guidance, or an explicit rationale and "
            "applicable presentation conventions for a non-UI project."
        ),
        agent=agents["design_junior"],
        context=[design_senior_task, product_revision_task],
    )
    design_review_task = Task(
        description=(
            "Act as Design Senior and review the actual DESIGN_TOKENS.md "
            f"inside {output_dir} against DESIGN_SPEC.md and product "
            "acceptance criteria. Use the read tool. Write DESIGN_REVIEW.md "
            "with findings classified BLOCKER/HIGH/MEDIUM/LOW, exact file "
            "references, and a clear ACCEPT or REVISE verdict. Check "
            "consistency, accessibility, responsive behavior, completeness, "
            "and whether every requirement is implementable."
        ),
        expected_output=(
            "DESIGN_REVIEW.md on disk with evidence-based findings, severity, "
            "file references, and ACCEPT or REVISE."
        ),
        agent=agents["design_senior"],
        context=[
            product_revision_task,
            design_senior_task,
            design_junior_task,
        ],
    )
    design_revision_task = Task(
        description=(
            "Read DESIGN_REVIEW.md and revise only the design junior-owned "
            "deliverable DESIGN_TOKENS.md if the verdict is REVISE. Address "
            "every BLOCKER and HIGH finding, then MEDIUM findings where "
            "consistent with scope. If the review is ACCEPT, preserve the "
            "approved file. Do not claim a finding was fixed without updating "
            f"and rereading the file in {output_dir}. Append a concise "
            "resolution record to DESIGN_REVIEW.md."
        ),
        expected_output=(
            "Revised DESIGN_TOKENS.md when required, or preserved accepted "
            "design, plus a finding-by-finding resolution record."
        ),
        agent=agents["design_junior"],
        context=[design_review_task],
    )
    architecture_task = Task(
        description=(
            "As Team Lead and system architect, convert the CEO brief, product "
            "specification, and design deliverables into an implementation "
            "plan for the project at "
            f"{output_dir}. Choose the stack and provide an exact directory "
            "tree, complete dependency manifest, environment variable list, "
            "run/test commands, security and reliability decisions, and a "
            "file-ownership matrix assigning exact non-overlapping paths to "
            "Backend Senior, Backend Junior, Frontend Senior, Frontend Junior, "
            "QA Junior, DevOps Senior, and DevOps Junior. Include expected "
            "paths for research, all review reports, DESIGN_SPEC.md, "
            "DESIGN_TOKENS.md, ANALYTICS.md, LEGAL_REVIEW.md, "
            "COST_ESTIMATE.md, IMPROVEMENTS.md, HANDOFF.md, REVIEW.md, and "
            "RELEASE_READINESS.md. "
            "For a department or technical layer that is genuinely out of "
            "scope, assign a short scope-decision document rather than "
            "inventing unnecessary infrastructure. Plan a runnable, testable "
            "project and do not leave file ownership ambiguous. Incorporate "
            "research only when supported by evidence; otherwise make "
            "version-sensitive choices explicit assumptions. Write the "
            "complete architecture and ownership matrix to ARCHITECTURE.md "
            f"inside {output_dir}."
        ),
        expected_output=(
            "A complete architecture and file-ownership plan with exact "
            "directory tree, manifest, setup and run instructions, environment "
            "configuration, risks, and explicit files for every department."
        ),
        agent=agents["team_lead"],
        context=[
            product_research_task,
            engineering_research_task,
            ceo_task,
            product_revision_task,
            design_senior_task,
            design_revision_task,
        ],
    )
    architecture_review_task = Task(
        description=(
            "Independently review the actual ARCHITECTURE.md inside "
            f"{output_dir} against product acceptance criteria, research, "
            "and design deliverables. Verify non-overlapping file ownership, "
            "justified stack decisions, complete manifests and run/test "
            "commands, and proportionate security/reliability decisions. "
            "Write ARCHITECTURE_REVIEW.md with severity-ranked findings "
            "and ACCEPT or REVISE."
        ),
        expected_output=(
            "ARCHITECTURE_REVIEW.md on disk with file references, prioritized "
            "findings, and ACCEPT or REVISE."
        ),
        agent=agents["technical_reviewer"],
        context=[
            product_revision_task,
            engineering_research_task,
            design_revision_task,
            architecture_task,
        ],
    )
    architecture_revision_task = Task(
        description=(
            "Resolve architecture-review feedback before implementation. Read "
            "ARCHITECTURE_REVIEW.md and ARCHITECTURE.md. If the verdict is "
            "REVISE, update the architecture and ownership matrix to address "
            "every BLOCKER and HIGH finding and resolve ownership overlaps. "
            "If ACCEPT, preserve it. Write ARCHITECTURE_DECISIONS.md with "
            "finding-by-finding disposition and a final ACCEPT or BLOCKED "
            f"decision in {output_dir}. Record unresolved risks. Downstream "
            "implementers must use the revised ARCHITECTURE.md."
        ),
        expected_output=(
            "Updated ARCHITECTURE.md when required, plus "
            "ARCHITECTURE_DECISIONS.md with findings disposition and "
            "ACCEPT or BLOCKED."
        ),
        agent=agents["team_lead"],
        context=[architecture_task, architecture_review_task],
    )
    backend_senior_task = Task(
        description=(
            "Implement only the Backend Senior paths assigned by the Team "
            "Lead. Build the core backend/domain behavior and interfaces "
            "required by the product specification. Write every assigned file "
            f"under {output_dir} using project-relative filenames. Include "
            "input validation, safe data handling, typed interfaces where "
            "supported, and explicit failure behavior. Do not edit paths "
            "assigned to other employees or invent extra files outside the "
            "architecture; if this project has no backend, write the assigned "
            "scope-decision document."
        ),
        expected_output=(
            "Complete backend senior-owned files on disk, or the assigned "
            "scope-decision document if a backend is not applicable, with a "
            "concise file inventory."
        ),
        agent=agents["backend_senior"],
        context=[product_revision_task, architecture_revision_task],
    )
    backend_junior_task = Task(
        description=(
            "Implement only the Backend Junior paths assigned in the Team "
            "Lead's file-ownership matrix. Complete the assigned persistence, "
            "integration, schema, and supporting backend test work while "
            "respecting the senior engineer's interfaces. Write complete "
            f"files under {output_dir}; do not overwrite senior- or other "
            "department-owned files. If there is no backend, write the "
            "assigned scope-decision document."
        ),
        expected_output=(
            "Complete backend junior-owned files on disk, or the assigned "
            "scope-decision document, with a concise file inventory and any "
            "unverified assumptions."
        ),
        agent=agents["backend_junior"],
        context=[architecture_revision_task, backend_senior_task],
    )
    backend_review_task = Task(
        description=(
            "Review the actual backend junior-owned files from the Team "
            "Lead's ownership matrix against the backend senior interfaces, "
            f"requirements, and architecture under {output_dir}. Inspect "
            "actual files with your tools. Write BACKEND_REVIEW.md with "
            "file-specific findings, severity, acceptance-criteria coverage, "
            "compatibility and security checks, and ACCEPT or REVISE. Check "
            "that no assigned file is missing or unexpectedly owned."
        ),
        expected_output=(
            "BACKEND_REVIEW.md with evidence-based findings, file references, "
            "severity-ranked acceptance checks, and ACCEPT or REVISE."
        ),
        agent=agents["backend_senior"],
        context=[product_task, architecture_revision_task, backend_junior_task],
    )
    backend_revision_task = Task(
        description=(
            "Read BACKEND_REVIEW.md and fix the junior-owned backend files "
            "only. Resolve all BLOCKER and HIGH findings and all in-scope "
            "MEDIUM findings; maintain the senior-defined interfaces. Reread "
            "changed files and append a finding-by-finding disposition to "
            f"BACKEND_REVIEW.md. If review is ACCEPT, make no unnecessary "
            f"changes. Do not claim a fix without updating files in {output_dir}."
        ),
        expected_output=(
            "Reviewed backend junior files corrected as needed and an updated "
            "BACKEND_REVIEW.md disposition for every finding."
        ),
        agent=agents["backend_junior"],
        context=[backend_review_task],
    )
    frontend_senior_task = Task(
        description=(
            "Implement only the Frontend Senior paths listed in the "
            "architecture's file-ownership matrix. Build the application "
            "shell, navigation or interaction flow, state handling, and "
            "integration points, following the design brief and product "
            f"contracts. Write complete files under {output_dir}. Do not "
            "overwrite junior-owned components or other departments' files. "
            "If there is no graphical or client frontend, write the assigned "
            "scope-decision document and implement the appropriate interface "
            "layer specified by the Team Lead."
        ),
        expected_output=(
            "Complete frontend senior-owned files on disk, or an appropriate "
            "assigned scope-decision deliverable, with a concise file inventory."
        ),
        agent=agents["frontend_senior"],
        context=[
            product_revision_task,
            design_revision_task,
            architecture_revision_task,
        ],
    )
    frontend_junior_task = Task(
        description=(
            "Implement only Frontend Junior paths in the Team Lead's "
            "file-ownership matrix. Create reusable, accessible components "
            "and styles that follow DESIGN_SPEC.md and DESIGN_TOKENS.md. "
            f"Write complete files under {output_dir}; do not edit senior-"
            "owned application files. If a graphical frontend is out of scope, "
            "write the assigned scope-decision deliverable."
        ),
        expected_output=(
            "Complete frontend junior-owned files on disk, or the assigned "
            "scope-decision deliverable, with a concise file inventory."
        ),
        agent=agents["frontend_junior"],
        context=[
            architecture_revision_task,
            design_revision_task,
            frontend_senior_task,
        ],
    )
    frontend_review_task = Task(
        description=(
            "Inspect actual junior-owned frontend components/styles in "
            f"{output_dir}. Review them against the senior frontend "
            "interfaces, DESIGN_SPEC.md, DESIGN_TOKENS.md, accessibility, "
            "responsive states, and product acceptance criteria. Write "
            "FRONTEND_REVIEW.md with concrete file-referenced findings, "
            "severity, and ACCEPT or REVISE. Do not approve work merely "
            "because files exist."
        ),
        expected_output=(
            "FRONTEND_REVIEW.md with evidence-based file findings, severity, "
            "design/accessibility coverage, and ACCEPT or REVISE."
        ),
        agent=agents["frontend_senior"],
        context=[
            product_task,
            design_revision_task,
            frontend_senior_task,
            frontend_junior_task,
        ],
    )
    frontend_revision_task = Task(
        description=(
            "Read FRONTEND_REVIEW.md and revise only junior-owned "
            "frontend components/styles. Resolve BLOCKER and HIGH findings "
            "and in-scope MEDIUM findings, preserve the senior-owned shell "
            "interfaces, and reread every changed file. Append disposition "
            "for every finding. If the review is ACCEPT, do not make unrelated "
            f"changes. Keep all writes in {output_dir}."
        ),
        expected_output=(
            "Junior frontend deliverables corrected as needed, with a "
            "finding-by-finding update to FRONTEND_REVIEW.md."
        ),
        agent=agents["frontend_junior"],
        context=[frontend_review_task],
    )
    qa_plan_task = Task(
        description=(
            "Create a risk-based QA plan from the acceptance criteria and "
            "architecture. Identify critical user journeys, unit/integration/"
            "end-to-end boundaries, negative cases, security checks, and "
            "test data needs. Write it as TEST_PLAN.md in the project root "
            f"({output_dir}). Distinguish planned checks from checks that can "
            "actually be executed with the available tools."
        ),
        expected_output=(
            "An on-disk TEST_PLAN.md mapping requirements to test cases, "
            "priorities, expected results, and execution limitations."
        ),
        agent=agents["qa_senior"],
        context=[
            product_task,
            architecture_revision_task,
            backend_senior_task,
            backend_revision_task,
            frontend_senior_task,
            frontend_revision_task,
        ],
    )
    qa_implementation_task = Task(
        description=(
            "Write only QA Junior-owned automated test files from the "
            "architecture matrix and TEST_PLAN.md. Cover core acceptance "
            "criteria, failure paths, input validation, and security-sensitive "
            "behavior as appropriate to the chosen stack. Save complete tests "
            f"under {output_dir}; do not change application source or claim "
            "that tests passed because you wrote them. If tests are not "
            "applicable, write the assigned scope-decision document."
        ),
        expected_output=(
            "Complete QA junior-owned test files on disk, or an assigned "
            "scope-decision document, with a list of coverage implemented "
            "and any tests not executed."
        ),
        agent=agents["qa_junior"],
        context=[architecture_revision_task, qa_plan_task],
    )
    qa_test_review_task = Task(
        description=(
            "As QA Senior, inspect every actual junior-owned automated test "
            f"file under {output_dir} and compare them with TEST_PLAN.md, "
            "product acceptance criteria, and the implementation. Check "
            "whether tests assert outcomes rather than implementation details, "
            "include negative/failure cases, and can plausibly run under the "
            "documented test command. You do not have a shell execution tool: "
            "do not say tests passed. Write TEST_REVIEW.md with file-specific "
            "findings and ACCEPT or REVISE."
        ),
        expected_output=(
            "TEST_REVIEW.md with specific test coverage findings, execution "
            "limitations, and ACCEPT or REVISE."
        ),
        agent=agents["qa_senior"],
        context=[qa_plan_task, qa_implementation_task],
    )
    qa_test_revision_task = Task(
        description=(
            "Read TEST_REVIEW.md and revise only QA Junior-owned test files. "
            "Address all BLOCKER and HIGH findings, improve in-scope coverage, "
            "and ensure every test uses the documented stack and public "
            "behavior. Reread changed files and append disposition for each "
            "finding. Never claim the tests passed; they have not been "
            f"executed. Keep writes within {output_dir}."
        ),
        expected_output=(
            "Reviewed tests corrected as needed and a finding-by-finding "
            "disposition in TEST_REVIEW.md, with execution status stated."
        ),
        agent=agents["qa_junior"],
        context=[qa_test_review_task],
    )
    devops_senior_task = Task(
        description=(
            "Implement only DevOps Senior-owned files from the file-ownership "
            "matrix: reproducible build/deployment configuration, runtime "
            "health checks, and secure operational defaults suitable for the "
            "selected stack. Write complete files under "
            f"{output_dir}. Never embed credentials, grant unnecessary "
            "privileges, or claim deployment verification without executing "
            "it. If deployment infrastructure is inappropriate for the MVP, "
            "write the assigned scope-decision document."
        ),
        expected_output=(
            "Complete DevOps senior-owned configuration on disk, or the "
            "assigned scope-decision document, with safe setup and deployment "
            "assumptions."
        ),
        agent=agents["devops_senior"],
        context=[
            architecture_revision_task,
            backend_revision_task,
            frontend_revision_task,
        ],
    )
    devops_junior_task = Task(
        description=(
            "Implement DevOps Junior-owned environment example and operations "
            "documentation paths from the architecture. Document required "
            "configuration without real secrets, local startup, health "
            "checks, troubleshooting, and recovery steps. Write complete "
            f"files under {output_dir}; keep commands consistent with the "
            "selected stack and do not claim to have executed them. If the "
            "architecture excludes DevOps infrastructure, write the assigned "
            "scope-decision document."
        ),
        expected_output=(
            "Complete DevOps junior-owned environment and operations files on "
            "disk, or the assigned scope-decision document."
        ),
        agent=agents["devops_junior"],
        context=[architecture_revision_task, devops_senior_task],
    )
    devops_review_task = Task(
        description=(
            "As DevOps Senior, inspect the actual DevOps Junior-owned "
            f"configuration and operational documents in {output_dir}. "
            "Compare required environment values, setup/run/health checks, "
            "and recovery steps with the architecture and senior-owned "
            "configuration. Check for accidental secrets and unsafe "
            "privileges. Write DEVOPS_REVIEW.md with evidence-based findings "
            "and ACCEPT or REVISE. Do not claim commands were executed."
        ),
        expected_output=(
            "DEVOPS_REVIEW.md with file-specific operational and security "
            "findings and ACCEPT or REVISE."
        ),
        agent=agents["devops_senior"],
        context=[architecture_revision_task, devops_senior_task, devops_junior_task],
    )
    devops_revision_task = Task(
        description=(
            "Read DEVOPS_REVIEW.md and correct the DevOps Junior-owned "
            "environment and operations files only. Resolve BLOCKER and HIGH "
            "findings, keep documentation aligned with current project files, "
            "and append disposition for every review finding. Do not claim "
            f"commands have been run. Keep writes under {output_dir}."
        ),
        expected_output=(
            "DevOps junior-owned deliverables corrected as needed with "
            "finding-by-finding disposition in DEVOPS_REVIEW.md."
        ),
        agent=agents["devops_junior"],
        context=[devops_review_task],
    )
    analytics_task = Task(
        description=(
            "Define product measurement for the idea without collecting "
            "unnecessary personal data. Specify actionable success metrics, "
            "event names and properties where events are appropriate, funnel "
            "definitions, dashboard questions, retention/privacy constraints, "
            "and known measurement assumptions. Write ANALYTICS.md in "
            f"{output_dir}. If analytics instrumentation is out of scope, "
            "explain what should be measured manually for the MVP."
        ),
        expected_output=(
            "An on-disk ANALYTICS.md with outcome metrics, event conventions, "
            "privacy-conscious measurement guidance, and assumptions."
        ),
        agent=agents["analytics"],
        context=[ceo_task, product_revision_task, architecture_revision_task],
    )
    legal_task = Task(
        description=(
            "Perform a preliminary product compliance and privacy issue spot "
            "based on the actual product requirements and chosen architecture. "
            "Document data sensitivity, consent/transparency, retention, "
            "third-party license, jurisdiction-dependent questions, and "
            "security/compliance concerns with concrete recommendations. "
            f"Write LEGAL_REVIEW.md in {output_dir}; state clearly that this "
            "is not legal advice and that qualified counsel must resolve "
            "jurisdiction-dependent matters. Do not claim compliance "
            "certification."
        ),
        expected_output=(
            "An on-disk LEGAL_REVIEW.md with risk-ranked preliminary issue "
            "spotting, mitigations, unresolved questions, and a clear "
            "not-legal-advice limitation."
        ),
        agent=agents["legal"],
        context=[product_revision_task, architecture_revision_task, analytics_task],
    )
    accounting_task = Task(
        description=(
            "Prepare a transparent, assumption-based cost estimate for "
            "building and operating this project. Identify infrastructure, "
            "storage, third-party API/service, and maintenance cost drivers; "
            "give ranges only when defensible; state usage assumptions and "
            "unknowns; distinguish one-time development effort from recurring "
            f"operating expenses. Write COST_ESTIMATE.md in {output_dir}. "
            "Do not invent vendor prices or present the result as financial "
            "advice."
        ),
        expected_output=(
            "An on-disk COST_ESTIMATE.md listing cost categories, assumptions, "
            "known unknowns, and practical cost-control recommendations."
        ),
        agent=agents["accounting"],
        context=[ceo_task, architecture_revision_task, devops_senior_task],
    )
    intern_task = Task(
        description=(
            "Prepare a concise implementation handoff. Use the directory and "
            "read tools to compare actual files at "
            f"{output_dir} with the architecture and department deliverables. "
            "List project entry points, setup/run/test commands, required "
            "environment variables by name, the file inventory, known gaps, "
            "and next steps. Write HANDOFF.md in the project root. Do not "
            "claim tests or commands were executed."
        ),
        expected_output=(
            "An on-disk HANDOFF.md with verified file inventory, setup "
            "instructions, configuration names, known gaps, and next steps."
        ),
        agent=agents["intern"],
        context=[
            architecture_revision_task,
            product_research_task,
            engineering_research_task,
            design_revision_task,
            backend_revision_task,
            frontend_revision_task,
            qa_plan_task,
            qa_test_revision_task,
            devops_senior_task,
            devops_revision_task,
            analytics_task,
            legal_task,
            accounting_task,
        ],
    )
    final_review_task = Task(
        description=(
            "Audit the actual generated files under "
            f"{output_dir} with the directory and read tools. Inspect source, "
            "tests, dependency manifests, setup and deployment configuration, "
            "environment examples, product/design/business reports, and the "
            "intern handoff. Check requirement coverage, missing files, "
            "interfaces, error handling, unsafe behavior, secret handling, "
            "privacy and licensing concerns, manifest consistency, and whether "
            "documented commands match available files. Do not claim tests or "
            "builds were run unless you actually ran them (you do not have a "
            "shell execution tool). Write TECHNICAL_REVIEW.md in the project "
            "root with "
            "an executive summary, checks performed, severity-ranked findings "
            "with file references, verification limitations, and actionable "
            "recommendations. Distinguish verified defects from follow-up "
            "questions; identify legal/accounting notes as preliminary "
            "assessments. Include BLOCKER/HIGH/MEDIUM/LOW severity and an "
            "ACCEPT or REVISE verdict."
        ),
        expected_output=(
            "An evidence-based TECHNICAL_REVIEW.md written on disk, covering engineering, "
            "quality, security, operations, and business handoff, with severity-"
            "ranked findings and explicit verification limitations."
        ),
        agent=agents["technical_reviewer"],
        context=[
            architecture_revision_task,
            qa_plan_task,
            qa_test_revision_task,
            devops_senior_task,
            devops_revision_task,
            analytics_task,
            legal_task,
            accounting_task,
            intern_task,
        ],
    )
    improvement_task = Task(
        description=(
            "Read TECHNICAL_REVIEW.md and inspect referenced files. Fix every "
            "BLOCKER and HIGH finding and in-scope MEDIUM findings without "
            "expanding scope or making unrelated refactors. Update relevant "
            "tests/docs. If verdict is ACCEPT, make no code changes. Write "
            "IMPROVEMENTS.md listing each finding, file changes, disposition, "
            "and items remaining for a human. Never claim tests passed; no "
            f"shell tool is available. Confine changes to {output_dir}."
        ),
        expected_output=(
            "A bounded remediation pass and IMPROVEMENTS.md with finding-by-"
            "finding resolution and unexecuted checks."
        ),
        agent=agents["improvement_engineer"],
        context=[final_review_task],
    )
    quality_gate_task = Task(
        description=(
            "Independently re-review actual final files at "
            f"{output_dir} after remediation. Verify whether review findings "
            "were fixed; inspect changed code, tests, manifests, environment "
            "examples, operations, and reports. Do not claim tests, builds, "
            "or deployments were executed. Write REVIEW.md with dispositions, "
            "findings, file references, and verification limits. Its first "
            "line must be exactly one of `STATUS: READY`, "
            "`STATUS: READY_WITH_LIMITATIONS`, or `STATUS: BLOCKED`. Use "
            "BLOCKED for an unresolved blocker/high issue; use "
            "READY_WITH_LIMITATIONS when only non-blocking checks remain "
            "unexecuted."
        ),
        expected_output=(
            "Final on-disk REVIEW.md with independent re-review and exactly "
            "one machine-readable status line."
        ),
        agent=agents["qa_senior"],
        context=[final_review_task, improvement_task],
    )
    release_task = Task(
        description=(
            "Inspect REVIEW.md, ARCHITECTURE_DECISIONS.md, IMPROVEMENTS.md, "
            f"and actual deliverables at {output_dir}. Confirm required files "
            "exist, junior review findings have dispositions, no blocker/high "
            "issue remains unresolved, and verification is not misrepresented. "
            "Write RELEASE_READINESS.md with first line exactly `STATUS: READY`, "
            "`STATUS: READY_WITH_LIMITATIONS`, or `STATUS: BLOCKED`. Use "
            "BLOCKED if architecture or final QA is blocked, a blocker/high "
            "finding remains, or a required deliverable is missing. State "
            "evidence, remaining risks, and required human actions."
        ),
        expected_output=(
            "RELEASE_READINESS.md with machine-readable status, evidence, "
            "remaining risks, and required human actions."
        ),
        agent=agents["release_manager"],
        context=[
            architecture_revision_task,
            design_review_task,
            backend_review_task,
            frontend_review_task,
            qa_test_review_task,
            devops_review_task,
            final_review_task,
            improvement_task,
            quality_gate_task,
            intern_task,
        ],
    )
    return [
        product_research_task,
        engineering_research_task,
        ceo_task,
        product_task,
        product_review_task,
        product_revision_task,
        design_senior_task,
        design_junior_task,
        design_review_task,
        design_revision_task,
        architecture_task,
        architecture_review_task,
        architecture_revision_task,
        backend_senior_task,
        backend_junior_task,
        backend_review_task,
        backend_revision_task,
        frontend_senior_task,
        frontend_junior_task,
        frontend_review_task,
        frontend_revision_task,
        qa_plan_task,
        qa_implementation_task,
        qa_test_review_task,
        qa_test_revision_task,
        devops_senior_task,
        devops_junior_task,
        devops_review_task,
        devops_revision_task,
        analytics_task,
        legal_task,
        accounting_task,
        intern_task,
        final_review_task,
        improvement_task,
        quality_gate_task,
        release_task,
    ]
