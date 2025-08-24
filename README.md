# Doctr 🩺

**Automatic Documentation Generation Daemon using AI**

Doctr is an intelligent documentation generation tool that analyzes your Git repository changes and creates comprehensive, AI-enhanced documentation automatically. It combines Git diff analysis, Language Server Protocol (LSP) integration, and Large Language Models to produce high-quality documentation that stays in sync with your code.

## Features

- 🤖 **AI-Powered Documentation**: Uses Claude 3.5 Haiku, GPT-4, and other LLMs to generate intelligent documentation
- 📊 **Git Diff Analysis**: Automatically detects and analyzes code changes from Git diffs
- 🔍 **Semantic Code Understanding**: Leverages LSP for deep code analysis and symbol resolution
- 📚 **Comprehensive Wiki Generation**: Creates complete project documentation including architecture, API reference, and guides
- ⚙️ **Configurable**: Flexible configuration via `.doctr.toml` with sensible defaults
- 🚀 **CLI-First**: Simple command-line interface for easy integration into workflows
- 📝 **Multiple Output Formats**: Generates Markdown and MDX documentation

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/doctr.git
cd doctr

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -e .
```

### Basic Usage

1. **Initialize doctr in your project:**

   ```bash
   uv run doctr init
   ```

2. **Set up your API key:**

   ```bash
   # For Anthropic Claude (default)
   export ANTHROPIC_API_KEY=your_key_here

   # Or for OpenAI
   export OPENAI_API_KEY=your_key_here
   ```

3. **Generate documentation from recent changes:**

   ```bash
   # Generate docs with AI enhancement
   uv run doctr generate --ai

   # Generate basic docs without AI
   uv run doctr generate --no-ai
   ```

4. **Create comprehensive project documentation:**
   ```bash
   # Generate complete wiki documentation
   uv run doctr setup
   ```

## Commands

### `doctr generate`

Generate documentation from Git changes.

```bash
# Basic usage
uv run doctr generate

# With custom options
uv run doctr generate --output ./docs --diff HEAD~3 --model claude-3-5-sonnet-20241022

# Without AI enhancement
uv run doctr generate --no-ai
```

**Options:**

- `--output, -o`: Output directory for documentation
- `--diff, -d`: Git diff target (default: HEAD~1)
- `--ai/--no-ai`: Enable/disable AI enhancement
- `--model, -m`: Specify LLM model to use

### `doctr setup`

Set up comprehensive AI-powered wiki documentation.

```bash
# Generate complete project documentation
uv run doctr setup

# With custom model
uv run doctr setup --model gpt-4o-mini

# Without AI (basic structure only)
uv run doctr setup --no-ai
```

**Options:**

- `--output, -o`: Output directory for wiki (default: ./wiki)
- `--ai/--no-ai`: Enable/disable AI enhancement (default: enabled)
- `--model, -m`: Specify LLM model to use

### `doctr init`

Initialize doctr configuration for a repository.

```bash
uv run doctr init
```

Creates a `.doctr.toml` configuration file with default settings.

## Configuration

Doctr uses a `.doctr.toml` file for configuration:

```toml
default_model = "claude-3-5-haiku-20241022"
output_dir = "docs"
default_diff_target = "HEAD~1"
use_ai = true
include_usage_examples = true
include_migration_guide = true
include_changelog = true
ignore_patterns = [
    "*.pyc", "*.pyo", "__pycache__/*",
    ".git/*", "node_modules/*", "*.log", "*.tmp"
]
```

### Supported Models

**Anthropic Claude:**

- `claude-3-5-haiku-20241022` (default, fast and efficient)
- `claude-3-5-sonnet-20241022` (more capable, slower)

**OpenAI:**

- `gpt-4o-mini` (fast and cost-effective)
- `gpt-4o` (most capable)

## How It Works

1. **Git Analysis**: Doctr analyzes your Git repository to identify recent changes
2. **Code Parsing**: Uses Language Server Protocol to understand code structure and semantics
3. **Change Detection**: Identifies modified functions, classes, and modules
4. **AI Enhancement**: Leverages LLMs to generate intelligent, contextual documentation
5. **Documentation Generation**: Creates structured Markdown/MDX files
6. **Output**: Writes documentation to your specified output directory

## Development

### Project Structure

```
doctr/
├── doctr/doctr/           # Main package (nested structure)
│   ├── cli/               # Command-line interface
│   ├── core/              # Core documentation generation logic
│   ├── integrations/      # External integrations (Git, LSP, LLM)
│   ├── languages/         # Language-specific analyzers
│   └── utils/             # Utilities and configuration
├── tests/                 # Test suite
└── docs/                  # Generated documentation
```

### Running Tests

```bash
# Run all tests
uv run python -m unittest discover -s doctr/tests -v

# Run specific test file
uv run python -m unittest doctr.tests.test_generator -v
```

### Adding Dependencies

```bash
uv add package_name
```

## Requirements

- Python 3.11+
- Git repository
- API key for AI features (Anthropic or OpenAI)

## License

MIT License

Copyright (c) 2025 Pankaj Garkoti

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
