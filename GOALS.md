# Doctr - Automatic Documentation Daemon

This document outlines our implementation plan for this automated documentation generation and maintainence tool.

## Full Implementation

- Init Python package + CLI (typer/click)
- Parse Git repos + diffs (GitPython)
- Connect to LSP (pylsp / JSON-RPC)
- Analyze semantic code changes (AST, symbols)
- Define doc model (dataclasses)
- Generate structured doc drafts from analysis
- Expand drafts with LLM (OpenAI/Anthropic/HF)
- Add caching for LLM outputs
- Write/update docs in Markdown/MDX
- Expose CLI command (`generate-docs`)
- Add GitHub Actions for PR/merge runs
- Implement doc-test runner (execukjjjte snippets)
- Auto-generate changelogs from diffs
- Post draft docs as PR comments (GitHub API)
- Add post-merge refinement pass
- Add logging + telemetry hooks
- Package + publish to PyPI

## MVP Implementation

- Init Python package + CLI (typer/click)
- Parse Git repos + diffs (GitPython)
- Connect to LSP (pylsp / JSON-RPC)
- Analyze semantic code changes (AST, symbols)
- Generate structured doc drafts from analysis
- Expand drafts with LLM (OpenAI/Anthropic/HF)
- Write/update docs in Markdown
