from typing import List, Optional
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel

from ..core.doc_model import CodeChange, DocumentationDraft, GeneratedDoc


class DocumentationAnalysis(BaseModel):
    """Structured analysis of code changes for documentation."""
    summary: str
    impact_level: str  # "minor", "moderate", "major"
    affected_components: List[str]
    breaking_changes: List[str]
    new_features: List[str]
    bug_fixes: List[str]
    documentation_sections: List[str]
    usage_examples_needed: bool
    migration_guide_needed: bool


class LLMDocumentationGenerator:
    """Uses LLM to analyze code changes and generate meaningful documentation."""
    
    def __init__(self, model_name: str = "claude-3-5-haiku-20241022", api_key: Optional[str] = None):
        # Set environment variable if api_key is provided
        if api_key:
            import os
            if model_name.startswith("gpt") or model_name.startswith("o1"):
                os.environ["OPENAI_API_KEY"] = api_key
            elif model_name.startswith("claude"):
                os.environ["ANTHROPIC_API_KEY"] = api_key
            else:
                # Default to Anthropic
                os.environ["ANTHROPIC_API_KEY"] = api_key
        
        # Choose the appropriate model based on the model name
        if model_name.startswith("gpt") or model_name.startswith("o1"):
            self.model = OpenAIModel(model_name)
        elif model_name.startswith("claude"):
            self.model = AnthropicModel(model_name)
        else:
            # Default to Anthropic
            self.model = AnthropicModel(model_name)
        
        # Agent for analyzing code changes
        self.analysis_agent = Agent(
            model=self.model,
            output_type=DocumentationAnalysis,
            instructions="""
            You are an expert technical writer and software engineer. Analyze the provided code changes 
            and create a structured analysis for documentation generation.
            
            Focus on:
            - Understanding the semantic meaning of changes, not just syntax
            - Identifying user-facing impacts and breaking changes
            - Determining what documentation sections are needed
            - Assessing whether usage examples or migration guides are required
            
            Be concise but thorough in your analysis.
            """
        )
        
        # Agent for generating documentation content
        self.content_agent = Agent(
            model=self.model,
            output_type=str,
            instructions="""
            You are an expert technical writer. Generate clear, comprehensive documentation 
            based on the code changes and analysis provided.
            
            Write documentation that:
            - Explains the "why" behind changes, not just the "what"
            - Includes practical usage examples when relevant
            - Follows markdown best practices
            - Is accessible to developers at different skill levels
            - Focuses on user impact and practical implications
            
            Structure the documentation with clear headings and sections.
            """
        )
    
    async def analyze_changes(self, changes: List[CodeChange]) -> DocumentationAnalysis:
        """Analyze code changes using LLM to understand their impact."""
        
        # Prepare context for the LLM
        context = self._prepare_changes_context(changes)
        
        prompt = f"""
        Analyze these code changes and provide a structured analysis:
        
        {context}
        
        Consider:
        1. What is the overall purpose of these changes?
        2. What components/modules are affected?
        3. Are there any breaking changes?
        4. What new features or capabilities are introduced?
        5. What bugs or issues are being fixed?
        6. What documentation sections should be created/updated?
        """
        
        result = await self.analysis_agent.run(prompt)
        return result.output
    
    async def generate_documentation(
        self, 
        analysis: DocumentationAnalysis, 
        changes: List[CodeChange],
        existing_content: Optional[str] = None
    ) -> str:
        """Generate comprehensive documentation content based on analysis."""
        
        changes_context = self._prepare_changes_context(changes)
        
        prompt = f"""
        Generate comprehensive documentation based on this analysis and code changes:
        
        ## Analysis:
        {analysis.model_dump_json(indent=2)}
        
        ## Code Changes:
        {changes_context}
        
        ## Existing Documentation:
        {existing_content or "No existing documentation"}
        
        Generate documentation that includes:
        1. Clear overview of what changed and why
        2. Impact on users and developers
        3. Usage examples for new features
        4. Migration guide if breaking changes exist
        5. Technical details where relevant
        
        Use proper markdown formatting with clear sections and headings.
        """
        
        result = await self.content_agent.run(prompt)
        return result.output
    
    def _prepare_changes_context(self, changes: List[CodeChange]) -> str:
        """Prepare a readable context of code changes for the LLM."""
        context_parts = []
        
        for i, change in enumerate(changes, 1):
            context_parts.append(f"## Change {i}: {change.file_path}")
            context_parts.append(f"Type: {change.change_type.value}")
            context_parts.append(f"Lines: {change.line_start}-{change.line_end}")
            
            if change.function_name:
                context_parts.append(f"Function: {change.function_name}")
            if change.class_name:
                context_parts.append(f"Class: {change.class_name}")
            
            if change.old_content:
                context_parts.append("### Old Content:")
                context_parts.append(f"```\n{change.old_content}\n```")
            
            if change.new_content:
                context_parts.append("### New Content:")
                context_parts.append(f"```\n{change.new_content}\n```")
            
            context_parts.append("")  # Empty line between changes
        
        return "\n".join(context_parts)
    
    async def enhance_draft(self, draft: DocumentationDraft) -> GeneratedDoc:
        """Enhance a basic documentation draft with LLM analysis."""
        
        # Analyze the changes
        analysis = await self.analyze_changes(draft.changes)
        
        # Generate enhanced content
        enhanced_content = await self.generate_documentation(analysis, draft.changes)
        
        return GeneratedDoc(
            title=draft.title,
            content=enhanced_content,
            metadata={
                **draft.metadata,
                "llm_analysis": analysis.model_dump(),
                "enhanced": True
            }
        )