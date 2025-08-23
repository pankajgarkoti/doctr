import unittest
from pathlib import Path
from doctr.doctr.core.doc_model import CodeChange, ChangeType, DocumentationDraft
from doctr.doctr.core.generator import DocumentationGenerator


class TestDocumentationGenerator(unittest.TestCase):
    
    def setUp(self):
        self.generator = DocumentationGenerator()
    
    def test_generate_draft_empty_changes(self):
        draft = self.generator.generate_draft([])
        self.assertEqual(draft.title, "No Changes")
        self.assertEqual(draft.summary, "No code changes detected.")
        self.assertEqual(len(draft.changes), 0)
    
    def test_generate_draft_single_file(self):
        changes = [
            CodeChange(
                file_path="test.py",
                change_type=ChangeType.ADDED,
                line_start=1,
                line_end=5,
                new_content="def hello():\n    print('world')"
            )
        ]
        
        draft = self.generator.generate_draft(changes)
        self.assertEqual(draft.title, "Changes to test.py")
        self.assertIn("1 added change", draft.summary)
        self.assertEqual(len(draft.changes), 1)
    
    def test_generate_draft_multiple_files(self):
        changes = [
            CodeChange(
                file_path="file1.py",
                change_type=ChangeType.ADDED,
                line_start=1,
                line_end=5
            ),
            CodeChange(
                file_path="file2.py",
                change_type=ChangeType.MODIFIED,
                line_start=10,
                line_end=15
            )
        ]
        
        draft = self.generator.generate_draft(changes)
        self.assertEqual(draft.title, "Changes across 2 files")
        self.assertIn("1 added change", draft.summary)
        self.assertIn("1 modified change", draft.summary)


if __name__ == '__main__':
    unittest.main()