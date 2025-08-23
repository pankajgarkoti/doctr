from typing import List
from pathlib import Path

from ..core.doc_model import CodeChange, DocumentationDraft, GeneratedDoc


class DocumentationGenerator:
    """Generates structured documentation drafts from code changes."""
    
    def generate_draft(self, changes: List[CodeChange]) -> DocumentationDraft:
        """Generate a structured documentation draft from code changes."""
        if not changes:
            return DocumentationDraft(
                title="No Changes",
                summary="No code changes detected.",
                changes=[],
                affected_symbols=[],
                suggested_sections=[],
                metadata={}
            )
        
        # Analyze changes to create draft
        affected_files = list(set(change.file_path for change in changes))
        affected_symbols = []
        
        # Extract symbols from changes
        for change in changes:
            if change.function_name:
                affected_symbols.append(f"{change.file_path}::{change.function_name}")
            if change.class_name:
                affected_symbols.append(f"{change.file_path}::{change.class_name}")
        
        # Generate title and summary
        if len(affected_files) == 1:
            title = f"Changes to {Path(affected_files[0]).name}"
        else:
            title = f"Changes across {len(affected_files)} files"
        
        summary = self._generate_summary(changes)
        suggested_sections = self._suggest_sections(changes)
        
        return DocumentationDraft(
            title=title,
            summary=summary,
            changes=changes,
            affected_symbols=affected_symbols,
            suggested_sections=suggested_sections,
            metadata={
                "files_changed": len(affected_files),
                "total_changes": len(changes),
                "change_types": [change.change_type.value for change in changes]
            }
        )
    
    def _generate_summary(self, changes: List[CodeChange]) -> str:
        """Generate a summary of the changes."""
        change_counts = {}
        for change in changes:
            change_type = change.change_type.value
            change_counts[change_type] = change_counts.get(change_type, 0) + 1
        
        summary_parts = []
        for change_type, count in change_counts.items():
            if count == 1:
                summary_parts.append(f"1 {change_type} change")
            else:
                summary_parts.append(f"{count} {change_type} changes")
        
        return "This update includes " + ", ".join(summary_parts) + "."
    
    def _suggest_sections(self, changes: List[CodeChange]) -> List[str]:
        """Suggest documentation sections based on changes."""
        sections = ["Overview"]
        
        # Add sections based on change types
        change_types = set(change.change_type for change in changes)
        
        if any(ct.value in ["added", "modified"] for ct in change_types):
            sections.append("New Features")
        
        if any(change.function_name for change in changes):
            sections.append("API Changes")
        
        sections.extend(["Usage Examples", "Migration Guide"])
        
        return sections