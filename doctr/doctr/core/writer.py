from pathlib import Path
from typing import Optional

from ..core.doc_model import GeneratedDoc


class DocumentationWriter:
    """Writes generated documentation to files."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def write_doc(self, doc: GeneratedDoc, filename: Optional[str] = None) -> Path:
        """Write documentation to a file."""
        if filename is None:
            # Generate filename from title
            safe_title = "".join(c for c in doc.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_').lower()
            filename = f"{safe_title}.md"
        
        file_path = self.output_dir / filename
        
        # Write content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {doc.title}\n\n")
            f.write(doc.content)
            
            # Add metadata as comments if present
            if doc.metadata:
                f.write("\n\n<!-- Metadata:\n")
                for key, value in doc.metadata.items():
                    f.write(f"{key}: {value}\n")
                f.write("-->\n")
        
        return file_path
    
    def write_changelog(self, content: str, filename: str = "CHANGELOG.md") -> Path:
        """Write or append to changelog."""
        file_path = self.output_dir / filename
        
        if file_path.exists():
            # Prepend to existing changelog
            existing_content = file_path.read_text(encoding='utf-8')
            content = content + "\n\n" + existing_content
        
        file_path.write_text(content, encoding='utf-8')
        return file_path