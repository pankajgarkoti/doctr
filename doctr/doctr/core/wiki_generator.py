from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .analyzer import ProjectStructure, ModuleInfo, FileInfo
from .doc_model import GeneratedDoc
from ..integrations.llm import LLMDocumentationGenerator


@dataclass
class WikiPage:
    title: str
    filename: str
    content: str
    category: str  # 'overview', 'api', 'guide', 'reference'


class WikiDocumentationGenerator:
    """Generates comprehensive wiki-style documentation for entire projects."""

    def __init__(
        self,
        use_ai: bool = True,
        model_name: str = "claude-3-5-haiku-20241022",
        api_key: Optional[str] = None,
    ):
        self.use_ai = use_ai
        if use_ai:
            self.llm_generator = LLMDocumentationGenerator(
                model_name=model_name, api_key=api_key
            )

    async def generate_wiki(
        self, project_structure: ProjectStructure
    ) -> List[WikiPage]:
        """Generate a complete wiki documentation for the project."""
        pages = []

        # Generate overview pages
        pages.append(await self._generate_home_page(project_structure))
        pages.append(await self._generate_installation_guide(project_structure))
        pages.append(await self._generate_quickstart_guide(project_structure))

        # Generate API documentation
        for module in project_structure.modules:
            api_page = await self._generate_api_reference(module, project_structure)
            pages.append(api_page)

        # Generate architecture overview
        pages.append(await self._generate_architecture_page(project_structure))

        # Generate development guide
        pages.append(await self._generate_development_guide(project_structure))

        # Generate configuration guide
        if project_structure.config_files:
            pages.append(await self._generate_configuration_guide(project_structure))

        # Generate testing guide
        if project_structure.test_directories:
            pages.append(await self._generate_testing_guide(project_structure))

        return pages

    async def _generate_home_page(
        self, project_structure: ProjectStructure
    ) -> WikiPage:
        """Generate the main README/Home page."""
        if self.use_ai:
            content = await self._generate_ai_content(
                "home_page",
                project_structure,
                """Generate a comprehensive README/Home page for this project. Include:
                - Project overview and purpose
                - Key features and capabilities
                - Quick installation/setup instructions
                - Basic usage examples
                - Links to detailed documentation sections
                - Contributing guidelines
                """,
            )
        else:
            content = self._generate_basic_home_page(project_structure)

        return WikiPage(
            title="Home", filename="Home.md", content=content, category="overview"
        )

    async def _generate_installation_guide(
        self, project_structure: ProjectStructure
    ) -> WikiPage:
        """Generate detailed installation and setup guide."""
        if self.use_ai:
            content = await self._generate_ai_content(
                "installation",
                project_structure,
                """Generate a detailed installation guide including:
                - System requirements
                - Step-by-step installation instructions
                - Development environment setup
                - Troubleshooting common installation issues
                - Dependencies and prerequisites
                """,
            )
        else:
            content = self._generate_basic_installation_guide(project_structure)

        return WikiPage(
            title="Installation Guide",
            filename="Installation.md",
            content=content,
            category="guide",
        )

    async def _generate_quickstart_guide(
        self, project_structure: ProjectStructure
    ) -> WikiPage:
        """Generate a quickstart/getting started guide."""
        if self.use_ai:
            content = await self._generate_ai_content(
                "quickstart",
                project_structure,
                """Generate a quickstart guide with:
                - Basic usage examples
                - Common use cases
                - Step-by-step tutorials for main features
                - Code examples and snippets
                - Expected outputs
                """,
            )
        else:
            content = self._generate_basic_quickstart_guide(project_structure)

        return WikiPage(
            title="Quick Start",
            filename="Quick-Start.md",
            content=content,
            category="guide",
        )

    async def _generate_api_reference(
        self, module: ModuleInfo, project_structure: ProjectStructure
    ) -> WikiPage:
        """Generate API reference for a specific module."""
        if self.use_ai:
            content = await self._generate_ai_content(
                "api_reference",
                project_structure,
                f"""Generate comprehensive API documentation for the '{module.name}' module including:
                - Module overview and purpose
                - All public functions and classes with descriptions
                - Parameter details and return values
                - Usage examples for each API
                - Error handling information
                
                Module details:
                - Path: {module.path}
                - Public API: {module.public_api}
                - Files: {[f.path.name for f in module.files]}
                """,
                module,
            )
        else:
            content = self._generate_basic_api_reference(module)

        return WikiPage(
            title=f"{module.name} API",
            filename=f"{module.name}-API.md",
            content=content,
            category="api",
        )

    async def _generate_architecture_page(
        self, project_structure: ProjectStructure
    ) -> WikiPage:
        """Generate architecture and design overview."""
        if self.use_ai:
            content = await self._generate_ai_content(
                "architecture",
                project_structure,
                """Generate an architecture overview including:
                - Project structure and organization
                - Key components and their relationships
                - Design patterns and principles used
                - Data flow and system interactions
                - Extension points and customization options
                """,
            )
        else:
            content = self._generate_basic_architecture_page(project_structure)

        return WikiPage(
            title="Architecture",
            filename="Architecture.md",
            content=content,
            category="reference",
        )

    async def _generate_development_guide(
        self, project_structure: ProjectStructure
    ) -> WikiPage:
        """Generate development and contributing guide."""
        if self.use_ai:
            content = await self._generate_ai_content(
                "development",
                project_structure,
                """Generate a development guide including:
                - Development environment setup
                - Code organization and standards
                - Building and testing procedures
                - Contributing guidelines
                - Release process
                """,
            )
        else:
            content = self._generate_basic_development_guide(project_structure)

        return WikiPage(
            title="Development Guide",
            filename="Development.md",
            content=content,
            category="guide",
        )

    async def _generate_configuration_guide(
        self, project_structure: ProjectStructure
    ) -> WikiPage:
        """Generate configuration reference."""
        content = f"""# Configuration Guide

This project uses several configuration files:

## Configuration Files

"""

        for config_file in project_structure.config_files:
            content += f"### {config_file.name}\n"
            content += f"Location: `{config_file}`\n\n"

            if config_file.name.endswith(".toml"):
                content += "TOML configuration file.\n\n"
            elif config_file.name.endswith((".yaml", ".yml")):
                content += "YAML configuration file.\n\n"
            elif config_file.name == "requirements.txt":
                content += "Python dependencies.\n\n"

        return WikiPage(
            title="Configuration",
            filename="Configuration.md",
            content=content,
            category="reference",
        )

    async def _generate_testing_guide(
        self, project_structure: ProjectStructure
    ) -> WikiPage:
        """Generate testing guide."""
        content = f"""# Testing Guide

## Test Structure

This project includes tests in the following locations:

"""

        for test_dir in project_structure.test_directories:
            content += f"- `{test_dir}`\n"

        content += """

## Running Tests

"""

        if project_structure.main_language == "python":
            content += """
### Python Tests

```bash
# Run all tests
python -m unittest discover

# Run with pytest (if available)
pytest

# Run specific test file
python -m unittest tests.test_module
```
"""
        elif project_structure.main_language == "go":
            content += """
### Go Tests

```bash
# Run all tests
go test ./...

# Run tests with coverage
go test -cover ./...

# Run specific package tests
go test ./pkg/module
```
"""

        return WikiPage(
            title="Testing Guide",
            filename="Testing.md",
            content=content,
            category="guide",
        )

    async def _generate_ai_content(
        self,
        content_type: str,
        project_structure: ProjectStructure,
        instructions: str,
        module: Optional[ModuleInfo] = None,
    ) -> str:
        """Generate AI-enhanced content for documentation."""
        try:
            # Prepare context about the project
            context = f"""
Project Analysis:
- Type: {project_structure.project_type.value}
- Main Language: {project_structure.main_language}
- Root: {project_structure.root_path.name}
- Modules: {len(project_structure.modules)}
- Entry Points: {[ep.name for ep in project_structure.entry_points]}
- Has Tests: {len(project_structure.test_directories) > 0}
- Dependencies: {project_structure.dependencies}

Project Structure:
"""

            for module_info in project_structure.modules:
                context += f"\n- Module: {module_info.name}"
                context += f"\n  Files: {[f.path.name for f in module_info.files]}"
                context += f"\n  Public API: {module_info.public_api}"

            if module:
                context += f"\n\nFocus Module Details:\n"
                for file_info in module.files:
                    context += f"\n- File: {file_info.path.name}"
                    context += f"\n  Functions: {file_info.functions}"
                    context += f"\n  Classes: {file_info.classes}"
                    if file_info.docstring:
                        context += f"\n  Docstring: {file_info.docstring[:200]}..."

            prompt = f"{instructions}\n\n{context}"

            result = await self.llm_generator.content_agent.run(prompt)
            return result.output

        except Exception as e:
            # Fallback to basic content if AI fails
            return f"# {content_type.title().replace('_', ' ')}\n\nContent generation failed: {e}\n\nPlease update this documentation manually."

    def _generate_basic_home_page(self, project_structure: ProjectStructure) -> str:
        """Generate basic home page without AI."""
        content = f"""# {project_structure.root_path.name}

## Overview

This is a {project_structure.main_language} project with {len(project_structure.modules)} modules.

## Project Structure

"""

        for module in project_structure.modules:
            content += f"- **{module.name}**: {len(module.files)} files\n"

        content += """
## Quick Start

[Installation instructions and basic usage examples would go here]

## Documentation

- [Installation Guide](Installation.md)
- [Quick Start Guide](Quick-Start.md)
- [API Reference](API-Reference.md)
- [Development Guide](Development.md)
"""

        return content

    def _generate_basic_installation_guide(
        self, project_structure: ProjectStructure
    ) -> str:
        """Generate basic installation guide."""
        content = "# Installation Guide\n\n"

        if project_structure.main_language == "python":
            content += (
                """## Python Installation

### Requirements
- Python 3.7+

### Install from source
```bash
git clone [repository-url]
cd """
                + project_structure.root_path.name
                + """
pip install -e .
```
"""
            )
        elif project_structure.main_language == "go":
            content += (
                """## Go Installation

### Requirements
- Go 1.19+

### Install from source
```bash
git clone [repository-url]
cd """
                + project_structure.root_path.name
                + """
go build ./...
```
"""
            )

        return content

    def _generate_basic_quickstart_guide(
        self, project_structure: ProjectStructure
    ) -> str:
        """Generate basic quickstart guide."""
        return f"""# Quick Start Guide

## Basic Usage

[Add basic usage examples for {project_structure.root_path.name}]

## Examples

[Add code examples and tutorials]
"""

    def _generate_basic_api_reference(self, module: ModuleInfo) -> str:
        """Generate basic API reference."""
        content = f"# {module.name} API Reference\n\n"

        content += f"## Overview\n\nModule location: `{module.path}`\n\n"

        if module.public_api:
            content += "## Public API\n\n"
            for api_item in module.public_api:
                content += f"### {api_item}\n\n[Documentation for {api_item}]\n\n"

        content += "## Files\n\n"
        for file_info in module.files:
            content += f"### {file_info.path.name}\n\n"
            if file_info.functions:
                content += "**Functions:**\n"
                for func in file_info.functions:
                    content += f"- `{func}()`\n"
                content += "\n"

            if file_info.classes:
                content += "**Classes:**\n"
                for cls in file_info.classes:
                    content += f"- `{cls}`\n"
                content += "\n"

        return content

    def _generate_basic_architecture_page(
        self, project_structure: ProjectStructure
    ) -> str:
        """Generate basic architecture overview."""
        content = f"""# Architecture

## Project Overview

- **Type**: {project_structure.project_type.value}
- **Language**: {project_structure.main_language}
- **Modules**: {len(project_structure.modules)}

## Module Structure

"""

        for module in project_structure.modules:
            content += f"### {module.name}\n"
            content += f"Location: `{module.path}`\n"
            content += f"Files: {len(module.files)}\n\n"

        return content

    def _generate_basic_development_guide(
        self, project_structure: ProjectStructure
    ) -> str:
        """Generate basic development guide."""
        content = "# Development Guide\n\n## Setup\n\n"

        if project_structure.main_language == "python":
            content += """```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```
"""

        content += "\n## Project Structure\n\n"
        for module in project_structure.modules:
            content += f"- `{module.name}/`: {len(module.files)} files\n"

        return content
