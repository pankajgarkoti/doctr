from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

from .intelligent_analyzer import IntelligentCodebaseAnalyzer, ExplorationPlan, ProjectInsight
from .doc_model import GeneratedDoc
from ..integrations.llm import LLMDocumentationGenerator


@dataclass
class WikiPage:
    title: str
    filename: str
    content: str
    category: str  # 'overview', 'api', 'guide', 'reference'


class AIWikiGenerator:
    """AI-first wiki documentation generator that follows an intelligent exploration plan."""
    
    def __init__(self, model_name: str = "claude-3-5-haiku-20241022", api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key
        self.llm_generator = LLMDocumentationGenerator(model_name=model_name, api_key=api_key)
    
    async def generate_comprehensive_wiki(self, project_path: Path) -> List[WikiPage]:
        """Generate comprehensive wiki following AI exploration plan."""
        
        # Step 1: Create intelligent analyzer
        analyzer = IntelligentCodebaseAnalyzer(
            root_path=project_path, 
            model_name=self.model_name, 
            api_key=self.api_key
        )
        
        # Step 2: Get AI exploration plan
        print("🧠 Creating exploration plan...")
        exploration_plan = await analyzer.create_exploration_plan()
        
        # Step 3: Get project insights  
        print("🔍 Analyzing project insights...")
        project_insights = await analyzer.analyze_project_insights()
        
        # Step 4: Get important project files
        print("📁 Identifying key project files...")
        project_files = await analyzer.get_project_files()
        
        # Step 5: Generate wiki pages based on exploration plan
        print("📖 Generating wiki pages...")
        pages = []
        
        # Generate core pages based on AI plan
        pages.append(await self._generate_home_page(exploration_plan, project_insights))
        pages.append(await self._generate_installation_guide(exploration_plan, project_files))
        pages.append(await self._generate_quickstart_guide(exploration_plan, project_insights, project_files))
        pages.append(await self._generate_architecture_guide(exploration_plan, project_insights, project_files))
        
        # Generate API documentation for core modules
        for module_name in exploration_plan.core_modules:
            api_page = await self._generate_module_api_docs(module_name, project_files, exploration_plan)
            if api_page:
                pages.append(api_page)
        
        # Generate additional pages based on exploration plan
        for doc_type in exploration_plan.documentation_structure:
            if doc_type.lower() not in ['home', 'installation', 'quickstart', 'architecture', 'api']:
                additional_page = await self._generate_additional_page(doc_type, exploration_plan, project_insights, project_files)
                if additional_page:
                    pages.append(additional_page)
        
        return pages
    
    async def _generate_home_page(self, plan: ExplorationPlan, insights: ProjectInsight) -> WikiPage:
        """Generate AI-powered home page."""
        
        prompt = f"""
        Generate a comprehensive README/Home page for this project:
        
        PROJECT OVERVIEW:
        {plan.project_overview}
        
        PROJECT INSIGHTS:
        - Purpose: {insights.project_purpose}
        - Main Functionality: {insights.main_functionality}
        - Target Audience: {insights.target_audience}
        - Key Features: {', '.join(insights.key_features)}
        - Architecture: {insights.architecture_style}
        
        KEY ENTRY POINTS:
        {chr(10).join([f'- {ep}' for ep in plan.key_entry_points])}
        
        Create a compelling home page that includes:
        1. Clear project description and value proposition
        2. Key features and benefits
        3. Quick installation snippet
        4. Basic usage example
        5. Links to detailed documentation
        6. Getting help/contributing information
        
        Make it welcoming and informative for new users.
        """
        
        result = await self.llm_generator.content_agent.run(prompt)
        
        return WikiPage(
            title="Home",
            filename="Home.md",
            content=result.output,
            category="overview"
        )
    
    async def _generate_installation_guide(self, plan: ExplorationPlan, files: List) -> WikiPage:
        """Generate AI-powered installation guide."""
        
        # Find configuration files
        config_files = [f for f in files if f.file_type in ['.toml', '.txt', '.json'] or 'setup' in f.path.name]
        config_context = "\n".join([f"{f.path.name}: {f.content_preview[:200]}" for f in config_files[:3]])
        
        prompt = f"""
        Generate a comprehensive installation guide for this project:
        
        PROJECT OVERVIEW:
        {plan.project_overview}
        
        CONFIGURATION FILES:
        {config_context}
        
        KEY ENTRY POINTS:
        {chr(10).join([f'- {ep}' for ep in plan.key_entry_points])}
        
        Create a detailed installation guide that includes:
        1. System requirements and prerequisites
        2. Step-by-step installation instructions
        3. Different installation methods (pip, source, etc.)
        4. Verification steps to confirm installation
        5. Development environment setup
        6. Troubleshooting common issues
        7. Environment variables and configuration
        
        Be thorough but clear and easy to follow.
        """
        
        result = await self.llm_generator.content_agent.run(prompt)
        
        return WikiPage(
            title="Installation Guide",
            filename="Installation.md",
            content=result.output,
            category="guide"
        )
    
    async def _generate_quickstart_guide(self, plan: ExplorationPlan, insights: ProjectInsight, files: List) -> WikiPage:
        """Generate AI-powered quickstart guide."""
        
        # Find main/entry files
        entry_files = [f for f in files if any(ep in str(f.path) for ep in plan.key_entry_points)]
        entry_context = "\n".join([f"{f.path.name}: {f.content_preview[:300]}" for f in entry_files[:3]])
        
        prompt = f"""
        Generate an engaging quickstart guide for this project:
        
        PROJECT PURPOSE: {insights.project_purpose}
        MAIN FUNCTIONALITY: {insights.main_functionality}
        KEY FEATURES: {', '.join(insights.key_features)}
        
        ENTRY POINTS:
        {chr(10).join([f'- {ep}' for ep in plan.key_entry_points])}
        
        ENTRY FILE EXAMPLES:
        {entry_context}
        
        Create a quickstart guide that includes:
        1. What you'll accomplish in 5 minutes
        2. Basic usage examples with actual code
        3. Step-by-step tutorial for common use cases
        4. Expected outputs and results
        5. Next steps and where to learn more
        
        Focus on getting users up and running quickly with practical examples.
        Make the examples realistic and immediately useful.
        """
        
        result = await self.llm_generator.content_agent.run(prompt)
        
        return WikiPage(
            title="Quick Start",
            filename="Quick-Start.md",
            content=result.output,
            category="guide"
        )
    
    async def _generate_architecture_guide(self, plan: ExplorationPlan, insights: ProjectInsight, files: List) -> WikiPage:
        """Generate AI-powered architecture guide."""
        
        # Get core module files
        core_files = [f for f in files if any(module in str(f.path) for module in plan.core_modules)]
        core_context = "\n".join([f"{f.path}: {f.content_preview[:200]}" for f in core_files[:5]])
        
        prompt = f"""
        Generate a comprehensive architecture guide for this project:
        
        ARCHITECTURE STYLE: {insights.architecture_style}
        PROJECT PURPOSE: {insights.project_purpose}
        
        CORE MODULES:
        {chr(10).join([f'- {module}' for module in plan.core_modules])}
        
        CORE FILES ANALYSIS:
        {core_context}
        
        Create an architecture guide that includes:
        1. High-level architecture overview and design philosophy
        2. Core components and their responsibilities
        3. Data flow and interaction patterns
        4. Key design decisions and trade-offs
        5. Extension points and customization options
        6. Directory structure explanation
        7. How the pieces fit together
        
        Make it technical but accessible, focusing on helping developers understand
        how to work with and extend the codebase.
        """
        
        result = await self.llm_generator.content_agent.run(prompt)
        
        return WikiPage(
            title="Architecture",
            filename="Architecture.md",
            content=result.output,
            category="reference"
        )
    
    async def _generate_module_api_docs(self, module_name: str, files: List, plan: ExplorationPlan) -> Optional[WikiPage]:
        """Generate API documentation for a specific module."""
        
        # Find files related to this module
        module_files = [f for f in files if module_name in str(f.path)]
        
        if not module_files:
            return None
        
        # Get top files by importance
        module_files = sorted(module_files, key=lambda x: x.importance_score, reverse=True)[:5]
        
        files_context = "\n\n".join([
            f"FILE: {f.path}\n{f.content_preview}" 
            for f in module_files
        ])
        
        prompt = f"""
        Generate comprehensive API documentation for the '{module_name}' module:
        
        MODULE CONTEXT IN PROJECT:
        {plan.project_overview}
        
        MODULE FILES:
        {files_context}
        
        Create detailed API documentation that includes:
        1. Module overview and purpose
        2. Main classes and functions with descriptions
        3. Parameter details and return values
        4. Usage examples for each major API
        5. Common patterns and best practices
        6. Error handling information
        7. Integration with other modules
        
        Focus on being practical and example-driven. Show real usage patterns.
        Make it easy for developers to understand and use the API.
        """
        
        result = await self.llm_generator.content_agent.run(prompt)
        
        return WikiPage(
            title=f"{module_name} API",
            filename=f"{module_name.replace('/', '-')}-API.md",
            content=result.output,
            category="api"
        )
    
    async def _generate_additional_page(self, doc_type: str, plan: ExplorationPlan, insights: ProjectInsight, files: List) -> Optional[WikiPage]:
        """Generate additional documentation pages based on exploration plan."""
        
        prompt = f"""
        Generate a '{doc_type}' documentation page for this project:
        
        PROJECT OVERVIEW: {plan.project_overview}
        PROJECT PURPOSE: {insights.project_purpose}
        KEY FEATURES: {', '.join(insights.key_features)}
        
        Create a comprehensive '{doc_type}' page that provides:
        - Relevant information for this documentation type
        - Practical guidance and examples
        - Clear explanations suitable for the target audience
        - Actionable content that helps users
        
        Tailor the content specifically to what users would expect in a '{doc_type}' page.
        """
        
        result = await self.llm_generator.content_agent.run(prompt)
        
        return WikiPage(
            title=doc_type,
            filename=f"{doc_type.replace(' ', '-')}.md",
            content=result.output,
            category="guide"
        )