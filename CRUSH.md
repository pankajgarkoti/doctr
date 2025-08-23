# CRUSH.md - Doctr Development Guide

## Build/Test Commands
```bash
# Install dependencies
uv sync

# Run all tests
uv run python -m unittest discover -s doctr/tests -v

# Run single test file
uv run python -m unittest doctr.tests.test_cli -v

# Run specific test method
uv run python -m unittest doctr.tests.test_cli.TestClassName.test_method_name -v

# Run main application
uv run python main.py

# Add new dependency
uv add package_name

# Add dev dependency
uv add --dev package_name
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