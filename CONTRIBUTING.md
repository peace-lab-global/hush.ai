# Contributing to hush.ai

Thank you for your interest in contributing. This document describes environment setup, repository layout, quality checks, and how we review changes.

## Code of conduct

All participants must follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Repository layout

```
hush.ai/
├── hushai/           # Installable package (CLI, settings, LLM, postprocess)
├── tests/            # Pytest suite (mocked network)
├── docs/             # User-facing documentation (Chinese-first, see docs/README.md)
├── .github/          # CI, Dependabot, issue/PR templates, release workflow
├── pyproject.toml    # Project metadata, Ruff/Mypy/pytest settings
├── Makefile          # Common dev commands (calls python3 -m …)
├── LICENSE / NOTICE  # Apache-2.0 + attribution
└── README.md         # Project entry and quick links
```

## Development setup

**Requirements:** Python 3.9+, `git`.

```bash
git clone <your-fork-url>
cd hush.ai
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
pre-commit install          # optional, aligns with .pre-commit-config.yaml
```

Use `python3` / `python -m` on all platforms so tools do not rely on PATH scripts.

## Making changes

1. Branch from `main` (or the default branch).
2. Keep commits focused; write messages that explain **intent**, not only diffs.
3. Run **`make check`** (or the equivalent commands below) before opening a PR.
4. Open a PR using the template; describe **what** changed, **why**, and how you tested.

### Developer Certificate of Origin (optional)

If this repository enables DCO checks, sign commits:

```bash
git commit -s
```

## Quality checks

Recommended (matches CI intent):

```bash
make check
```

Equivalent manual steps:

```bash
python3 -m ruff check hushai tests
python3 -m ruff format --check hushai tests
python3 -m mypy hushai
python3 -m pytest --cov=hushai --cov-report=term-missing --cov-fail-under=70
```

- **Ruff:** lint + format (`ruff format .` to apply).
- **Mypy:** `hushai` package only (`py.typed` included).
- **Pytest:** coverage threshold **70%** on `hushai` (see `pyproject.toml`).

## Continuous integration

On pull requests and pushes to `main` / `master`:

- **Ubuntu:** Python **3.9–3.13** — Ruff, Ruff format check, Mypy, Pytest with coverage, informational `pip-audit`.
- **Windows / macOS:** smoke job — install editable package and run `pytest -q`.
- **Build:** sdist/wheel build + `twine check` on Ubuntu.

Contributors should keep CI green; if a job is flaky, open an issue with logs.

## Tests

- Add or update tests under `tests/` for behavior changes.
- **Do not** call live APIs in unit tests; mock `OpenAI` / `chat_once` as existing tests do.
- Reset global config state is handled by `tests/conftest.py` (`reset_for_tests()`).

## Documentation

- **User-visible** behavior or configuration → update [README.md](README.md) and the relevant file under [docs/](docs/README.md).
- When changing **dialogue modes** (`VALID_MODES` in `hushai/settings.py`): update the mode table and alias list in [docs/configuration.md](docs/configuration.md), and any README / architecture / CLI references so they stay consistent.
- Notable changes → [CHANGELOG.md](CHANGELOG.md) (Keep a Changelog style).
- Security-sensitive usage → [SECURITY.md](SECURITY.md) when appropriate.

## Releases

Maintainers: see [MAINTAINERS.md](MAINTAINERS.md) for tagging and GitHub Releases. Contributors do not need to publish releases; focus on tests and changelog entries.

## Security

See [SECURITY.md](SECURITY.md) for private vulnerability reporting.

## Questions

Open an issue (use a template when available) before investing large effort in uncertain directions.
