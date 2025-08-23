import typer
from pathlib import Path
from typing import Optional

from ..core.diff_parser import DiffParser
from ..core.generator import DocumentationGenerator
from ..core.writer import DocumentationWriter
from ..core.doc_model import GeneratedDoc

app = typer.Typer(help="Doctr - Automatic Documentation Generation")


@app.command()
def generate_docs(
    repo_path: Optional[Path] = typer.Argument(None, help="Path to Git repository"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory for docs"),
    diff_target: Optional[str] = typer.Option("HEAD~1", "--diff", "-d", help="Git diff target (default: HEAD~1)"),
):
    """Generate documentation from Git changes."""
    if repo_path is None:
        repo_path = Path.cwd()
    
    if output_dir is None:
        output_dir = repo_path / "docs"
    
    typer.echo(f"Generating docs for: {repo_path}")
    typer.echo(f"Output directory: {output_dir}")
    typer.echo(f"Diff target: {diff_target}")
    
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
        
        # Create basic documentation (without LLM expansion for now)
        content = f"{draft.summary}\n\n"
        content += "## Changes\n\n"
        
        for change in draft.changes:
            content += f"- **{change.file_path}**: {change.change_type.value}\n"
            if change.new_content:
                content += f"  ```\n  {change.new_content[:200]}...\n  ```\n"
        
        # Write documentation
        writer = DocumentationWriter(output_dir)
        doc = GeneratedDoc(
            title=draft.title,
            content=content,
            metadata=draft.metadata
        )
        
        output_file = writer.write_doc(doc)
        typer.echo(f"Documentation written to: {output_file}")
        
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


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
        return
    
    # TODO: Create default config
    typer.echo(f"Initializing doctr config at: {config_file}")


if __name__ == "__main__":
    app()