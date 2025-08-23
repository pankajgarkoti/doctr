import typer
import asyncio
from pathlib import Path
from typing import Optional

from ..core.diff_parser import DiffParser
from ..core.generator import DocumentationGenerator
from ..core.writer import DocumentationWriter
from ..core.doc_model import GeneratedDoc
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


if __name__ == "__main__":
    app()
