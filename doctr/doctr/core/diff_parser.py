from pathlib import Path
from typing import List, Optional
import git
from git import Repo, Diff

from ..core.doc_model import CodeChange, ChangeType


class DiffParser:
    """Parses Git diffs to extract code changes."""
    
    def __init__(self, repo_path: Path):
        self.repo = Repo(repo_path)
    
    def parse_diff(self, target: str = "HEAD~1") -> List[CodeChange]:
        """Parse Git diff and extract code changes."""
        try:
            # Get diff between target and current HEAD
            diffs = self.repo.git.diff(target, name_only=True).split('\n')
            changes = []
            
            for file_path in diffs:
                if not file_path.strip():
                    continue
                    
                # Get detailed diff for this file
                file_diff = self.repo.git.diff(target, file_path)
                change = self._parse_file_diff(file_path, file_diff)
                if change:
                    changes.append(change)
            
            return changes
            
        except Exception as e:
            print(f"Error parsing diff: {e}")
            return []
    
    def _parse_file_diff(self, file_path: str, diff_content: str) -> Optional[CodeChange]:
        """Parse individual file diff."""
        if not diff_content.strip():
            return None
        
        # Basic parsing - extract added/removed lines
        lines = diff_content.split('\n')
        added_lines = []
        removed_lines = []
        line_num = 0
        
        for line in lines:
            if line.startswith('@@'):
                # Extract line number from hunk header
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        line_num = int(parts[2].split(',')[0].lstrip('+'))
                    except (ValueError, IndexError):
                        line_num = 0
            elif line.startswith('+') and not line.startswith('+++'):
                added_lines.append((line_num, line[1:]))
                line_num += 1
            elif line.startswith('-') and not line.startswith('---'):
                removed_lines.append((line_num, line[1:]))
            elif not line.startswith('-'):
                line_num += 1
        
        # Determine change type
        if added_lines and not removed_lines:
            change_type = ChangeType.ADDED
        elif removed_lines and not added_lines:
            change_type = ChangeType.DELETED
        else:
            change_type = ChangeType.MODIFIED
        
        # Create CodeChange object
        start_line = min([ln for ln, _ in added_lines + removed_lines]) if added_lines or removed_lines else 0
        end_line = max([ln for ln, _ in added_lines + removed_lines]) if added_lines or removed_lines else 0
        
        return CodeChange(
            file_path=file_path,
            change_type=change_type,
            line_start=start_line,
            line_end=end_line,
            old_content='\n'.join([content for _, content in removed_lines]) if removed_lines else None,
            new_content='\n'.join([content for _, content in added_lines]) if added_lines else None
        )