import typer
import asyncio
from pathlib import Path
from typing import Optional

from ..core.diff_parser import DiffParser
from ..core.generator import DocumentationGenerator
from ..core.writer import DocumentationWriter
from ..core.doc_model import GeneratedDoc
from ..core.ai_wiki_generator import AIWikiGenerator
from ..integrations.llm import LLMDocumentationGenerator
from ..utils.config import load_config, create_default_config, get_api_key

app = typer.Typer(help="Doctr - Automatic Documentation Generation")


async def _generate_docs(
    repo_path: Optional[Path],
    output_dir: Optional[Path],
    diff_target: Optional[str],
    use_ai: Optional[bool],
    model: Optional[str],
):
    """Async implementation of documentation generation."""
    if repo_path is None:
        repo_path = Path.cwd()

    # Load configuration
    config = load_config(repo_path)

    # Apply CLI overrides
    if output_dir is None:
        output_dir = repo_path / config.output_dir
    if diff_target is None:
        diff_target = config.default_diff_target
    if use_ai is None:
        use_ai = config.use_ai
    if model is None:
        model = config.default_model

    typer.echo(f"Generating docs for: {repo_path}")
    typer.echo(f"Output directory: {output_dir}")
    typer.echo(f"Diff target: {diff_target}")
    typer.echo(f"AI enhancement: {'enabled' if use_ai else 'disabled'}")
    if use_ai:
        typer.echo(f"Model: {model}")

    try:
        # Parse Git diff
        parser = DiffParser(repo_path)
        changes = parser.parse_diff(diff_target)

        if not changes:
            typer.echo("No changes detected.")
            return

        typer.echo(f"Found {len(changes)} code changes")

        # Generate documentation draft
        generator = DocumentationGenerator()
        draft = generator.generate_draft(changes)

        if use_ai:
            # Check for API key
            api_key = get_api_key(config, model)
            if not api_key:
                if model.startswith("claude"):
                    typer.echo(
                        f"Warning: No API key found for model {model}. Set ANTHROPIC_API_KEY environment variable or configure in .doctr.toml",
                        err=True,
                    )
                else:
                    typer.echo(
                        f"Warning: No API key found for model {model}. Set OPENAI_API_KEY environment variable or configure in .doctr.toml",
                        err=True,
                    )
                typer.echo("Falling back to basic documentation generation...")
                use_ai = False

        if use_ai:
            # Use AI to enhance the documentation
            typer.echo("Analyzing changes with AI...")
            llm_generator = LLMDocumentationGenerator(model_name=model, api_key=api_key)
            doc = await llm_generator.enhance_draft(draft)
        else:
            # Create basic documentation without AI
            content = f"{draft.summary}\n\n"
            content += "## Changes\n\n"

            for change in draft.changes:
                content += f"- **{change.file_path}**: {change.change_type.value}\n"
                if change.new_content:
                    content += f"  ```\n  {change.new_content[:200]}...\n  ```\n"

            doc = GeneratedDoc(
                title=draft.title, content=content, metadata=draft.metadata
            )

        # Write documentation
        writer = DocumentationWriter(output_dir)
        output_file = writer.write_doc(doc)
        typer.echo(f"Documentation written to: {output_file}")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


async def _setup_wiki(
    repo_path: Optional[Path],
    output_dir: Optional[Path],
    use_ai: Optional[bool],
    model: Optional[str],
):
    """Async implementation of wiki documentation setup."""
    if repo_path is None:
        repo_path = Path.cwd()

    # Load configuration
    config = load_config(repo_path)

    # Apply CLI overrides - AI is now DEFAULT
    if output_dir is None:
        output_dir = repo_path / "wiki"
    if use_ai is None:
        use_ai = True  # AI-first approach
    if model is None:
        model = config.default_model

    typer.echo(f"Setting up AI-powered wiki documentation for: {repo_path}")
    typer.echo(f"Output directory: {output_dir}")
    typer.echo(f"AI enhancement: {'enabled' if use_ai else 'disabled'}")
    if use_ai:
        typer.echo(f"Model: {model}")

    try:
        if not use_ai:
            typer.echo("⚠️  AI disabled. Basic documentation structure will be created.")
            # Fall back to basic structure (you could implement a simple non-AI version)
            typer.echo(
                "❌ Non-AI mode not yet implemented. Please use --ai for full functionality."
            )
            raise typer.Exit(1)

        # Check for API key FIRST before doing any AI operations
        api_key = get_api_key(config, model)
        if not api_key:
            if model.startswith("claude"):
                typer.echo(
                    f"❌ No API key found for model {model}.",
                    err=True,
                )
                typer.echo(
                    "   Set ANTHROPIC_API_KEY environment variable or configure in .doctr.toml"
                )
            else:
                typer.echo(
                    f"❌ No API key found for model {model}.",
                    err=True,
                )
                typer.echo(
                    "   Set OPENAI_API_KEY environment variable or configure in .doctr.toml"
                )
            typer.echo(
                "\n💡 Get your API key and try again for AI-powered documentation."
            )
            raise typer.Exit(1)

        # Use AI-first wiki generator
        typer.echo("🚀 Starting AI-powered documentation generation...")
        wiki_generator = AIWikiGenerator(model_name=model, api_key=api_key)

        wiki_pages = await wiki_generator.generate_comprehensive_wiki(repo_path)

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write all wiki pages
        typer.echo(f"\n📝 Writing {len(wiki_pages)} documentation pages...")
        for page in wiki_pages:
            page_path = output_dir / page.filename
            with open(page_path, "w", encoding="utf-8") as f:
                f.write(page.content)
            typer.echo(f"  ✅ {page.title} -> {page_path}")

        # Create a navigation index
        nav_content = "# Documentation Index\n\n"

        # Group by category
        categories = {}
        for page in wiki_pages:
            if page.category not in categories:
                categories[page.category] = []
            categories[page.category].append(page)

        for category, pages in categories.items():
            nav_content += f"## {category.title()}\n\n"
            for page in pages:
                nav_content += f"- [{page.title}]({page.filename})\n"
            nav_content += "\n"

        nav_path = output_dir / "_Navigation.md"
        with open(nav_path, "w", encoding="utf-8") as f:
            f.write(nav_content)
        typer.echo(f"  ✅ Navigation Index -> {nav_path}")

        typer.echo(f"\n🎉 AI-powered wiki documentation created successfully!")
        typer.echo(f"📁 Documentation available at: {output_dir}")
        typer.echo(
            "\n🧠 AI analyzed your codebase and created comprehensive documentation."
        )
        typer.echo("💡 Review and customize the generated content as needed.")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def generate(
    repo_path: Optional[Path] = typer.Argument(None, help="Path to Git repository"),
    output_dir: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output directory for docs"
    ),
    diff_target: Optional[str] = typer.Option(
        None, "--diff", "-d", help="Git diff target"
    ),
    use_ai: Optional[bool] = typer.Option(
        None, "--ai/--no-ai", help="Use AI to enhance documentation"
    ),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="LLM model to use"),
):
    """Generate documentation from Git changes."""
    asyncio.run(_generate_docs(repo_path, output_dir, diff_target, use_ai, model))


@app.command()
def init(
    repo_path: Optional[Path] = typer.Argument(None, help="Path to repository"),
):
    """Initialize doctr configuration for a repository."""
    if repo_path is None:
        repo_path = Path.cwd()

    config_file = repo_path / ".doctr.toml"

    if config_file.exists():
        typer.echo(f"Configuration already exists: {config_file}")
        if not typer.confirm("Overwrite existing configuration?"):
            return

    # Create default config
    created_config = create_default_config(repo_path)
    typer.echo(f"Created doctr configuration: {created_config}")
    typer.echo("\nNext steps:")
    typer.echo("1. Set your Anthropic API key: export ANTHROPIC_API_KEY=your_key_here")
    typer.echo("   Or for OpenAI: export OPENAI_API_KEY=your_key_here")
    typer.echo("2. Run: uv run doctr generate --ai")
    typer.echo("3. Customize .doctr.toml as needed")


@app.command()
def setup(
    repo_path: Optional[Path] = typer.Argument(None, help="Path to repository"),
    output_dir: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output directory for wiki documentation"
    ),
    use_ai: Optional[bool] = typer.Option(
        True,
        "--ai/--no-ai",
        help="Use AI to generate comprehensive documentation (default: enabled)",
    ),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="LLM model to use"),
):
    """Set up AI-powered comprehensive wiki documentation for your project.

    This command uses AI to intelligently explore your codebase and generate
    comprehensive documentation including:

    - Project overview and quickstart guide
    - Architecture and design documentation
    - API reference for core modules
    - Installation and development guides

    AI is enabled by default for the best experience.
    """
    asyncio.run(_setup_wiki(repo_path, output_dir, use_ai, model))


if __name__ == "__main__":
    app()
