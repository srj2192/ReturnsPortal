# Decisions

Document your key decisions, tradeoffs, and any test changes.

## 1. Decorator-based condition registry

- **Decision:** Conditions are registered via a `@condition("name")` decorator instead of a hardcoded dict in `engine.py`.
- **Rationale:** Adding a new condition no longer requires editing the engine. Write a function anywhere, decorate it, and it's available to rules.
- **Alternatives considered:** Class-based conditions — rejected because the handlers are simple functions; 

## 2. Cached rule loading

- **Decision:** Rules are loaded from disk once and cached using `@lru_cache`. The eligibility service reuses a single `RuleEngine` instance.
- **Rationale:** The rules file only changes at deploy time. Re-reading it on every request was unnecessary I/O.
- **Alternatives considered:** Django cache framework — heavier dependency.

## 3. Rule validation on load

- **Decision:** Rules are validated when loaded. Missing `id`, `description`, or `condition`/`conditions` raises an error at startup.
- **Rationale:** Catches config mistakes early instead of failing at runtime during evaluation.
- **Alternatives considered:** JSON Schema validation — can be implemented but not needed at this scale.
