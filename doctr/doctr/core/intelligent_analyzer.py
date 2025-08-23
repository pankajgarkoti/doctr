from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pydantic import BaseModel

from ..integrations.llm import LLMDocumentationGenerator


class ExplorationPlan(BaseModel):
    """AI-generated plan for exploring and documenting a codebase."""

    project_overview: str
    key_entry_points: List[str]
    core_modules: List[str]
    documentation_structure: List[str]
    exploration_priorities: List[str]


class ProjectInsight(BaseModel):
    """AI analysis of project structure and purpose."""

    project_purpose: str
    main_functionality: str
    target_audience: str
    key_features: List[str]
    architecture_style: str


@dataclass
class ProjectFile:
    path: Path
    content_preview: str
    file_type: str
    importance_score: int  # 1-10


class IntelligentCodebaseAnalyzer:
    """AI-powered codebase analyzer that focuses on project code, not dependencies."""

    def __init__(
        self,
        root_path: Path,
        model_name: str = "claude-3-5-haiku-20241022",
        api_key: Optional[str] = None,
    ):
        self.root_path = root_path
        self.llm_generator = LLMDocumentationGenerator(
            model_name=model_name, api_key=api_key
        )

        # Agent specifically for exploration planning
        from pydantic_ai import Agent
        from pydantic_ai.models.anthropic import AnthropicModel

        if model_name.startswith("gpt"):
            from pydantic_ai.models.openai import OpenAIModel

            model = OpenAIModel(model_name)
        else:
            model = AnthropicModel(model_name)

        self.exploration_agent = Agent(
            model=model,
            output_type=ExplorationPlan,
            instructions="""
            You are an expert code archaeologist. Your job is to intelligently explore a codebase 
            and create a comprehensive documentation plan.
            
            Focus on:
            - Understanding the project's core purpose and functionality
            - Identifying the most important files and modules
            - Creating a logical documentation structure
            - Prioritizing what users need to know first
            
            Ignore dependencies, third-party libraries, and development tooling.
            Focus on the actual project code that implements the main functionality.
            """,
        )

        self.insight_agent = Agent(
            model=model,
            output_type=ProjectInsight,
            instructions="""
            You are a technical writer analyzing a software project. Provide insights about:
            - What problem this project solves
            - Who the target users are
            - What the main functionality is
            - How the architecture is organized
            
            Be concise but comprehensive in your analysis.
            """,
        )

    async def create_exploration_plan(self) -> ExplorationPlan:
        """Create an AI-powered exploration plan for the codebase."""

        # Step 1: Read key project files
        project_context = await self._gather_project_context()

        # Step 2: Get AI exploration plan
        prompt = f"""
        Analyze this software project and create a comprehensive exploration plan:
        
        {project_context}
        
        Create a plan that covers:
        1. Project overview based on available information
        2. Key entry points (main files, CLI commands, APIs)
        3. Core modules that implement the main functionality
        4. Recommended documentation structure (wiki pages to create)
        5. Exploration priorities (what to analyze first)
        """

        result = await self.exploration_agent.run(prompt)
        return result.output

    async def analyze_project_insights(self) -> ProjectInsight:
        """Get AI insights about the project's purpose and architecture."""

        project_context = await self._gather_project_context()

        prompt = f"""
        Analyze this software project and provide insights:
        
        {project_context}
        
        Focus on understanding:
        - What problem does this solve?
        - Who are the users?
        - What are the key features?
        - How is it architected?
        """

        result = await self.insight_agent.run(prompt)
        return result.output

    async def _gather_project_context(self) -> str:
        """Gather key information about the project for AI analysis."""
        context_parts = []

        # Check for README files
        readme_content = self._read_readme()
        if readme_content:
            context_parts.append(f"README Content:\n{readme_content[:2000]}...")

        # Check for existing documentation
        docs_content = self._read_existing_docs()
        if docs_content:
            context_parts.append(f"Existing Documentation:\n{docs_content[:1000]}...")

        # Analyze directory structure
        structure = self._analyze_directory_structure()
        context_parts.append(f"Directory Structure:\n{structure}")

        # Check for entry points
        entry_points = self._find_entry_points()
        if entry_points:
            context_parts.append(
                f"Entry Points:\n{chr(10).join([str(ep) for ep in entry_points])}"
            )

        # Check configuration files
        config_info = self._analyze_config_files()
        if config_info:
            context_parts.append(f"Configuration:\n{config_info}")

        return "\n\n".join(context_parts)

    def _read_readme(self) -> Optional[str]:
        """Read README file if it exists."""
        readme_patterns = ["README.md", "README.rst", "README.txt", "README"]

        for pattern in readme_patterns:
            readme_path = self.root_path / pattern
            if readme_path.exists():
                try:
                    with open(readme_path, "r", encoding="utf-8") as f:
                        return f.read()
                except Exception:
                    continue
        return None

    def _read_existing_docs(self) -> Optional[str]:
        """Read existing documentation files."""
        docs_content = []

        # Look for docs directory
        docs_dir = self.root_path / "docs"
        if docs_dir.exists():
            for doc_file in docs_dir.rglob("*.md"):
                try:
                    with open(doc_file, "r", encoding="utf-8") as f:
                        content = f.read()[:500]  # First 500 chars
                        docs_content.append(f"{doc_file.name}: {content}")
                except Exception:
                    continue

        # Look for other documentation files
        for doc_file in self.root_path.glob("*.md"):
            if doc_file.name.upper().startswith("README"):
                continue  # Already handled
            try:
                with open(doc_file, "r", encoding="utf-8") as f:
                    content = f.read()[:300]
                    docs_content.append(f"{doc_file.name}: {content}")
            except Exception:
                continue

        return "\n".join(docs_content) if docs_content else None

    def _analyze_directory_structure(self) -> str:
        """Analyze the project directory structure, focusing on project files."""
        structure_lines = []

        def is_project_directory(path: Path) -> bool:
            """Check if a directory contains project code."""
            path_str = str(path)

            # Skip common non-project directories
            skip_dirs = {
                ".venv",
                "venv",
                "env",
                "__pycache__",
                ".git",
                ".pytest_cache",
                "node_modules",
                ".tox",
                ".mypy_cache",
                "build",
                "dist",
                ".coverage",
                ".env",
                ".vscode",
                ".idea",
                ".DS_Store",
                "site-packages",
                "dist-packages",
            }

            # Check if any part of the path is a skip directory
            for part in path.parts:
                if part in skip_dirs:
                    return False

            # Skip paths that look like installed packages
            try:
                relative_path = path.relative_to(self.root_path)
                if len(relative_path.parts) > 3:  # Too deep, likely dependencies
                    return False

                # Skip if path contains version numbers (likely installed packages)
                for part in relative_path.parts:
                    if any(char.isdigit() for char in part) and (
                        "-" in part or "." in part
                    ):
                        if not any(
                            keyword in part.lower()
                            for keyword in ["test", "src", "lib"]
                        ):
                            return False
            except ValueError:
                return False

            return True

        def add_directory(path: Path, level: int = 0):
            if level > 3:  # Limit depth
                return

            if not is_project_directory(path):
                return

            indent = "  " * level
            structure_lines.append(f"{indent}{path.name}/")

            # Add important files in this directory
            important_files = []
            for file_path in path.iterdir():
                if file_path.is_file():
                    if self._is_important_file(file_path):
                        important_files.append(file_path.name)

            for file_name in sorted(important_files)[:5]:  # Max 5 files per directory
                structure_lines.append(f"{indent}  {file_name}")

            # Recurse into subdirectories
            for subdir in sorted([d for d in path.iterdir() if d.is_dir()]):
                add_directory(subdir, level + 1)

        add_directory(self.root_path)
        return "\n".join(structure_lines)

    def _is_important_file(self, file_path: Path) -> bool:
        """Check if a file is important for understanding the project."""
        name = file_path.name.lower()

        # Important file patterns
        important_patterns = [
            # Python files
            "main.py",
            "__main__.py",
            "__init__.py",
            "cli.py",
            "app.py",
            # Configuration
            "setup.py",
            "pyproject.toml",
            "requirements.txt",
            "Pipfile",
            "package.json",
            "go.mod",
            "Cargo.toml",
            # Documentation
            "readme",
            "changelog",
            "license",
            "contributing",
            # Other important files
            "dockerfile",
            "makefile",
            ".gitignore",
        ]

        # Check exact matches or startswith
        for pattern in important_patterns:
            if name == pattern or name.startswith(pattern):
                return True

        # Check extensions
        important_extensions = {
            ".py",
            ".go",
            ".js",
            ".ts",
            ".rs",
            ".java",
            ".cpp",
            ".c",
        }
        if file_path.suffix.lower() in important_extensions:
            # Only include if it's likely project code (not in deep nested dirs)
            try:
                relative_path = file_path.relative_to(self.root_path)
                return len(relative_path.parts) <= 3
            except ValueError:
                return False

        return False

    def _find_entry_points(self) -> List[Path]:
        """Find potential entry points to the application."""
        entry_points = []

        # Common entry point files
        entry_patterns = [
            "main.py",
            "app.py",
            "__main__.py",
            "cli.py",
            "server.py",
            "run.py",
            "start.py",
        ]

        for pattern in entry_patterns:
            for match in self.root_path.rglob(pattern):
                # Only include if it's in a reasonable location (not too deep)
                try:
                    relative_path = match.relative_to(self.root_path)
                    if len(relative_path.parts) <= 3:
                        entry_points.append(match)
                except ValueError:
                    continue

        # Look for files with if __name__ == "__main__"
        for py_file in self.root_path.rglob("*.py"):
            try:
                relative_path = py_file.relative_to(self.root_path)
                if len(relative_path.parts) > 3:
                    continue

                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read(1000)  # First 1000 chars
                    if 'if __name__ == "__main__"' in content:
                        entry_points.append(py_file)
            except Exception:
                continue

        return list(set(entry_points))  # Remove duplicates

    def _analyze_config_files(self) -> Optional[str]:
        """Analyze configuration files to understand the project."""
        config_info = []

        config_files = [
            "pyproject.toml",
            "setup.py",
            "requirements.txt",
            "package.json",
            "go.mod",
            "Cargo.toml",
            ".doctr.toml",
        ]

        for config_file in config_files:
            config_path = self.root_path / config_file
            if config_path.exists():
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        content = f.read(500)  # First 500 chars
                        config_info.append(f"{config_file}:\n{content}")
                except Exception:
                    continue

        return "\n\n".join(config_info) if config_info else None

    async def get_project_files(self) -> List[ProjectFile]:
        """Get a curated list of important project files with AI scoring."""
        files = []

        for file_path in self.root_path.rglob("*"):
            if not file_path.is_file():
                continue

            if not self._is_important_file(file_path):
                continue

            # Skip files in directories we should ignore
            if not self._is_project_directory_for_file(file_path):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content_preview = f.read(500)

                # AI would score importance here, for now use simple heuristic
                importance = self._score_file_importance(file_path, content_preview)

                files.append(
                    ProjectFile(
                        path=file_path,
                        content_preview=content_preview,
                        file_type=file_path.suffix,
                        importance_score=importance,
                    )
                )

            except Exception:
                continue

        # Sort by importance and return top files
        return sorted(files, key=lambda x: x.importance_score, reverse=True)[:50]

    def _is_project_directory_for_file(self, file_path: Path) -> bool:
        """Check if file is in a project directory."""
        try:
            relative_path = file_path.relative_to(self.root_path)
            path_parts = relative_path.parts[:-1]  # Exclude filename

            # Check each directory component
            for part in path_parts:
                skip_dirs = {
                    ".venv",
                    "venv",
                    "env",
                    "__pycache__",
                    ".git",
                    ".pytest_cache",
                    "node_modules",
                    ".tox",
                    ".mypy_cache",
                    "build",
                    "dist",
                    ".coverage",
                    ".env",
                    ".vscode",
                    ".idea",
                    "site-packages",
                    "dist-packages",
                }

                if part in skip_dirs:
                    return False

            # Don't go too deep
            if len(path_parts) > 4:
                return False

            return True

        except ValueError:
            return False

    def _score_file_importance(self, file_path: Path, content_preview: str) -> int:
        """Score file importance (1-10)."""
        score = 5  # Base score

        name = file_path.name.lower()

        # High importance files
        if name in ["main.py", "__main__.py", "app.py", "cli.py"]:
            score += 3
        elif name in ["__init__.py", "setup.py", "pyproject.toml"]:
            score += 2
        elif "readme" in name or "license" in name:
            score += 2

        # Content-based scoring
        if "class" in content_preview and "def" in content_preview:
            score += 1
        if 'if __name__ == "__main__"' in content_preview:
            score += 2

        # File type scoring
        if file_path.suffix == ".py":
            score += 1

        return min(score, 10)
