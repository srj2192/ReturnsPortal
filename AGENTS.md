# Repository Guidelines

## Project Structure & Module Organization
This repository is a Django challenge app focused on returns logic.

- `manage.py`: local entrypoint for Django commands.
- `returns_portal/`: project configuration (`settings.py`, `urls.py`, `wsgi.py`).
- `portal/`: main app code.
- `portal/services/mapper.py`: raw order payload -> domain model mapping.
- `portal/services/eligibility.py`: return eligibility rules loading and evaluation.
- `portal/templates/returns/`: Django + HTMX templates.
- `portal/data/`: sample input data and rule config files.
- `portal/tests/`: pytest suite (`test_mapper.py`, `test_eligibility.py`, `test_views.py`).

## Build, Test, and Development Commands
- `uv venv && uv pip install -e ".[dev]"`: create environment and install runtime/dev dependencies.
- `python manage.py runserver`: start local server at `http://localhost:8000/returns/`.
- `pytest`: run all tests (configured to use `portal/tests`).
- `ruff check .`: run lint checks.
- `mypy portal returns_portal`: run strict type checks.

## Coding Style & Naming Conventions
- Target Python `3.12` with 4-space indentation.
- Follow Ruff defaults with line length `88`.
- Keep type hints complete; mypy is configured in strict mode.
- Use `snake_case` for modules/functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants.
- Keep business logic in services, not templates/views.

## Testing Guidelines
- Frameworks: `pytest` + `pytest-django`.
- Place tests in `portal/tests/` and name files `test_<feature>.py`.
- Name test functions `test_<behavior>`.
- Cover both happy paths and edge cases (return window expiry, digital/final-sale items, already-returned quantities).
- Run `pytest` locally before opening a PR.

## Commit & Pull Request Guidelines
This scaffold currently has no commit history, so use clear, imperative commit messages.

- Example: `feat(eligibility): add final-sale and digital-item rules`
- Example: `test(mapper): cover category and flags mapping`

Keep commits small and focused. PRs should include:
- what changed and why,
- test evidence (commands run),
- screenshots/GIFs for template/HTMX UI updates,
- updates to `DECISIONS.md` and `AI_LOG.md` when applicable.

## Security & Configuration Tips
- Do not commit secrets or local environment files.
- Keep only synthetic/demo data in `portal/data/`.
- Ensure `DJANGO_SETTINGS_MODULE=returns_portal.settings` when running tools outside pytest.
