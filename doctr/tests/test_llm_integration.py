import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from doctr.doctr.integrations.llm import LLMDocumentationGenerator, DocumentationAnalysis
from doctr.doctr.core.doc_model import CodeChange, ChangeType, DocumentationDraft


class TestLLMIntegration(unittest.TestCase):
    
    @patch('doctr.doctr.integrations.llm.AnthropicModel')
    @patch('doctr.doctr.integrations.llm.Agent')
    async def test_analyze_changes(self, mock_agent_class, mock_anthropic_model):
        """Test that LLM integration correctly processes code changes."""
        
        # Mock the agent and its result
        mock_result = MagicMock()
        mock_result.output = DocumentationAnalysis(
            summary="Test summary",
            impact_level="moderate",
            affected_components=["test_component"],
            breaking_changes=[],
            new_features=["test_feature"],
            bug_fixes=[],
            documentation_sections=["API Changes"],
            usage_examples_needed=True,
            migration_guide_needed=False
        )
        
        mock_agent_instance = AsyncMock()
        mock_agent_instance.run.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance
        
        # Create test data
        changes = [
            CodeChange(
                file_path="test.py",
                change_type=ChangeType.MODIFIED,
                line_start=1,
                line_end=10,
                new_content="def test_function():\n    return 'hello'"
            )
        ]
        
        # Test the LLM generator
        generator = LLMDocumentationGenerator(api_key="test-key")
        result = await generator.analyze_changes(changes)
        
        # Verify the result
        self.assertIsInstance(result, DocumentationAnalysis)
        self.assertEqual(result.summary, "Test summary")
        self.assertEqual(result.impact_level, "moderate")
        self.assertTrue(result.usage_examples_needed)


if __name__ == '__main__':
    import asyncio
    
    async def run_test():
        test = TestLLMIntegration()
        await test.test_analyze_changes()
        print("✅ LLM integration test passed!")
    
    asyncio.run(run_test())