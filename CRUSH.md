# CRUSH.md - Doctr Development Guide

## Build/Test Commands

```bash
# Install dependencies
uv sync

# Run doctr (basic mode without AI)
uv run doctr generate --no-ai

# Run doctr with AI using Anthropic (default)
export ANTHROPIC_API_KEY=your_key_here
uv run doctr generate --ai

# Run doctr with OpenAI models
export OPENAI_API_KEY=your_key_here
uv run doctr generate --ai --model gpt-4o-mini

# Run doctr with custom options
uv run doctr generate --output ./documentation --diff HEAD~3 --model claude-3-5-sonnet-20241022

# Initialize doctr config (creates .doctr.toml)
uv run doctr init

# Run all tests
uv run python -m unittest discover -s doctr/tests -v

# Run single test file
uv run python -m unittest doctr.tests.test_generator -v

# Add new dependency
uv add package_name
```

## Code Style Guidelines

### Project Structure

- Main package: `doctr/doctr/` (nested structure)
- Tests: `doctr/tests/` with `test_*.py` naming
- Core modules: `core/`, `cli/`, `integrations/`, `languages/`, `utils/`

### Python Standards

- Python 3.11+ required (see `.python-version` and `uv.lock`)
- Use uv for dependency management
- Use standard library unittest for testing
- Follow PEP 8 naming conventions
- Use type hints where possible
- Keep imports organized: stdlib, third-party, local

### Error Handling

- Use specific exception types
- Provide meaningful error messages
- Handle edge cases gracefully

### Documentation Tool Context

- This is an automated documentation generation tool
- Focuses on Git diffs, LSP integration, and LLM-powered doc generation
- Target output: Markdown/MDX documentation files
