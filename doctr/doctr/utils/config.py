import os
from pathlib import Path
from typing import Optional, Dict, Any
import toml
from pydantic import BaseModel


class DoctrConfig(BaseModel):
    """Configuration for Doctr."""
    
    # LLM settings
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_model: str = "claude-3-5-haiku-20241022"
    
    # Documentation settings
    output_dir: str = "docs"
    default_diff_target: str = "HEAD~1"
    use_ai: bool = True
    
    # File patterns
    ignore_patterns: list[str] = [
        "*.pyc", "*.pyo", "__pycache__/*", ".git/*", 
        "node_modules/*", "*.log", "*.tmp"
    ]
    
    # Documentation templates
    include_usage_examples: bool = True
    include_migration_guide: bool = True
    include_changelog: bool = True


def load_config(repo_path: Path) -> DoctrConfig:
    """Load configuration from various sources."""
    config_data = {}
    
    # 1. Load from environment variables
    if api_key := os.getenv("ANTHROPIC_API_KEY"):
        config_data["anthropic_api_key"] = api_key
    if api_key := os.getenv("OPENAI_API_KEY"):
        config_data["openai_api_key"] = api_key
    
    # 2. Load from global config file
    global_config_path = Path.home() / ".doctr" / "config.toml"
    if global_config_path.exists():
        global_config = toml.load(global_config_path)
        config_data.update(global_config)
    
    # 3. Load from project-specific config
    project_config_path = repo_path / ".doctr.toml"
    if project_config_path.exists():
        project_config = toml.load(project_config_path)
        config_data.update(project_config)
    
    return DoctrConfig(**config_data)


def create_default_config(repo_path: Path) -> Path:
    """Create a default .doctr.toml configuration file."""
    config_path = repo_path / ".doctr.toml"
    
    default_config = {
        "default_model": "claude-3-5-haiku-20241022",
        "output_dir": "docs",
        "default_diff_target": "HEAD~1",
        "use_ai": True,
        "include_usage_examples": True,
        "include_migration_guide": True,
        "include_changelog": True,
        "ignore_patterns": [
            "*.pyc", "*.pyo", "__pycache__/*", ".git/*",
            "node_modules/*", "*.log", "*.tmp"
        ]
    }
    
    with open(config_path, 'w') as f:
        toml.dump(default_config, f)
    
    return config_path


def get_api_key(config: DoctrConfig, model_name: str) -> Optional[str]:
    """Get the appropriate API key for the given model."""
    if model_name.startswith("gpt") or model_name.startswith("o1"):
        return config.openai_api_key
    elif model_name.startswith("claude"):
        return config.anthropic_api_key
    else:
        # Default to Anthropic for unknown models
        return config.anthropic_api_key