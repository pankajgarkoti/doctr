from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class ChangeType(Enum):
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


@dataclass
class CodeChange:
    """Represents a semantic code change."""
    file_path: str
    change_type: ChangeType
    line_start: int
    line_end: int
    old_content: Optional[str] = None
    new_content: Optional[str] = None
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    symbol_type: Optional[str] = None  # function, class, variable, etc.


@dataclass
class DocumentationDraft:
    """Structured documentation draft before LLM expansion."""
    title: str
    summary: str
    changes: List[CodeChange]
    affected_symbols: List[str]
    suggested_sections: List[str]
    metadata: Dict[str, Any]


@dataclass
class GeneratedDoc:
    """Final generated documentation."""
    title: str
    content: str
    format: str = "markdown"  # markdown, mdx
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = None