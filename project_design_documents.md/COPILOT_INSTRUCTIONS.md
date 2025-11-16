# GitHub Copilot / Assistant Instructions

Project coding style
- Language and versions: e.g., "Python 3.11" or "Node 18" — replace accordingly.
- Formatting: use the project formatter (e.g., `black`, `prettier`) and follow linter rules.
- Naming: follow idiomatic patterns for the chosen language, include type hints where appropriate.

Tests
- Provide unit tests for new behavior (use `pytest`, `jest`, etc.).
- Aim for clear, deterministic tests and small, focused fixtures.

What Copilot should do automatically
- Suggest small, focused implementations with clear docstrings.
- Include unit tests and basic input validation for new functions.
- Add minimal README or docs updates when adding features.

What Copilot must avoid
- Never generate or commit secrets, credentials, or private keys.
- Avoid using deprecated or unmaintained libraries without justification.

Preferred prompts/examples
- "Implement feature X: keep functions small, add type hints, and include pytest unit tests." 
- "Write a unit test for function Y that covers normal and error cases." 

Commit & PR guidance for the assistant
- Suggest commit message: short summary line + one-sentence body.
- Include a checklist: tests added, lint passes, README updated if needed.

Example assistant persona
- Concise, pragmatic, and conservative: prefer readability and maintainability.
