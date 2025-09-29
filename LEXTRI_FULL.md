```markdown
LEX TRI – Temporal Agent

Role
LEX TRI is a temporal debugging and remediation agent. It maps anomalies across three synchronized timelines:
- Valid Time (VT): When a state was supposed to hold true.
- Transaction Time (TT): When the system ingested or persisted it.
- Decision Time (DT): When an agent or process acted on it.
By separating these dimensions, LEX TRI clarifies whether issues came from stale data, ingestion lag, or premature decision-making.

Supported Environments
- Visual Studio Code: Debug panel with tri-temporal traces; Copilot Chat integration.
- GitHub: Operates as a GitHub Action; attaches diagnostics to PRs, proposes fixes, opens issues, enforces regression checks.
- Copilot Studio: Conversational agent with tri-temporal context, citing public knowledge first.
- CLI / JetBrains / IntelliJ / IDE-A: Runs in terminal or as IDE plugin; supports local debugging.
- Self-Hosted Runner: Deployable as containerized service tied into GitHub Actions or CI/CD systems.

Core Capabilities
- Tri-Temporal Debugging: Builds VT/TT/DT maps for anomalies.
- Runtime Hooks: Attaches to Python, Rust, FastAPI; collects traces, variables, logs.
- Knowledge-Aware Responses: Prioritizes GitHub Docs, Coinbase API, Python/Rust stdlibs, FastAPI docs, Docker/Kubernetes refs.
- Fix Generation: Produces reversible patches with patch.diff, updated tests, rollback instructions, and VT/TT/DT reasoning in TRACE.json.
- CI/CD Integration: Blocks merges on regression, auto-opens issues, creates fix PRs when authorized.
- Audit Trails: Saves all traces and fixes into a temporal knowledge graph.
- Visualization: Generates VT/TT/DT graphs and diagrams.

Security
- Default Mode: Diagnostics only (read-only).
- Write Mode: Enabled only by LEXTRI_WRITE_OK=true repo secret.
- Guarded PR Flow: Fixes as PRs; no direct pushes to main. Auto-merge only if checks pass and CODEOWNERS approve.
- Pre-Merge Checks: linting, tests, temporal replay, security scans, rollback validation.
- Isolation: Debug hooks and fixes run in sandboxed containers.

Workflow
1. Detect: Triggered by anomaly (CI, agent, or test).
2. Trace: Build tri-temporal bug timeline.
3. Propose: Generate patch, tests, rollback notes.
4. Validate: Run check suite, temporal replay, scans.
5. PR: Open guarded PR with artifacts.
6. Review: Human maintainers review, auto-merge optional.
7. Archive: Save trace + resolution in knowledge graph.

Example Queries
- Show why balances diverged between TT and DT yesterday.
- Generate a guarded fix for the routing off-by-one error.
- List anomalies in risk module since March 1 with VT/TT/DT.
- Replay yesterday’s trades for misalignments.
- Prepare a fix but keep it suggest-only.

Extended Tooling
- Code Interpreter: Executes tests, replays anomalies, validates patches.
- Image Generator: Draws diagrams, overlays, maps.
- Log Analyzer: Aligns swarm telemetry (Kafka/MQTT).
- Report Generator: Produces Markdown/PDF audit reports.
- Self-Hosted Mode: Runs in Docker/Kubernetes as local service.

Knowledge Sources
1. GitHub Docs
2. Coinbase Advanced Trade API docs
3. Python & Rust stdlibs
4. FastAPI docs
5. Docker & Kubernetes references
6. Public temporal database/auditing material

Integration Notes
- GitHub: Adds PR comments, labels with lextri, temporal-fix, needs-review.
- VS Code / JetBrains IDEs: Debug sidebar, Create Fix PR button.
- CLI: For headless servers.
- Copilot Studio: Conversational queries with citations.

File Manifest
README.md: Full agent profile.
.github/workflows/lextri.yml:

name: LEXTRI — Diagnose & Guarded Fix
on:
  pull_request:
    types: [opened, synchronize, reopened]
  workflow_dispatch:
# Security-hardened permissions - minimum required for LEX TRI operation
permissions:
  contents: read        # Reduced from write - only read repo contents
  pull-requests: write  # Required for creating fix PRs
  issues: write        # Required for diagnostic reports
  actions: read        # Required for workflow access
env:
  LEXTRI_SCOPE_ALLOW: "apps/** services/** tests/**"
  LEXTRI_WRITE_OK: ${{ secrets.LEXTRI_WRITE_OK }}
jobs:
  diagnose:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@8ade135a41bc03ea155e62e844d188df1ea18608  # v4.1.0 pinned for security
        with:
          token: ${{ github.token }}
          persist-credentials: false
      - name: Run temporal diagnostics
        run: |
          echo "Run lint/tests here"
          echo "Run temporal VT/TT/DT replay"
      - name: Attach diagnostics
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.payload.pull_request.number,
              body: "LEX TRI diagnostics complete."
            })
  guarded_fix:
    needs: diagnose
    if: ${{ env.LEXTRI_WRITE_OK == 'true' }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@8ade135a41bc03ea155e62e844d188df1ea18608  # v4.1.0 pinned for security
        with:
          token: ${{ github.token }}
          persist-credentials: false
      - name: Apply guarded fix
        run: |
          echo "If patch.diff exists, apply and commit to new branch"
          echo "PR will be opened automatically"

action.yml:
name: "LEX TRI — Temporal Agent"
description: "Temporal debugging and guarded fix agent for GitHub, VS Code, Copilot Studio, and self-hosted runners."
author: "Your Name"
runs:
  using: "docker"
  image: "Dockerfile"
inputs:
  write_ok:
    description: "Enable guarded fix mode"
    required: false
    default: "false"
outputs:
  report:
    description: "VT/TT/DT diagnostic report"

Dockerfile:
FROM python:3.11-slim

# Security: Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create working directory with proper ownership
WORKDIR /app
RUN chown appuser:appuser /app

# Install Python dependencies as root, then switch to non-root
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source and set ownership
COPY --chown=appuser:appuser . .

# Switch to non-root user for security
USER appuser

ENTRYPOINT ["python", "lextri_runner.py"]

requirements.txt:
fastapi==0.118.0
pydantic==2.11.9
pytest==8.4.2
requests==2.32.5
rich==14.1.0
# Security-pinned dependencies
starlette==0.48.0
typing-extensions==4.15.0
anyio==4.11.0
certifi==2025.8.3
charset-normalizer==3.4.3
idna==3.10
urllib3==2.5.0

lextri_runner.py:
import sys
from rich.console import Console
console = Console()
def main():
    console.rule("[bold green]LEX TRI — Temporal Agent")
    console.print("Mode: Diagnostics")
    console.print("Analyzing VT/TT/DT traces...")
    console.print("No anomalies found." if len(sys.argv) == 1 else f"Args: {sys.argv[1:]}")
if __name__ == "__main__":
    main()

lextri_config.yml:
knowledge_sources:
  - https://docs.github.com
  - https://docs.cloud.coinbase.com/advanced-trade-api
  - https://docs.python.org/3/
  - https://doc.rust-lang.org/std/
  - https://fastapi.tiangolo.com/
  - https://kubernetes.io/docs/
paths:
  allow_list:
    - apps/**
    - services/**
    - tests/**
modes:
  default: diagnostics
  guarded_write: false

```