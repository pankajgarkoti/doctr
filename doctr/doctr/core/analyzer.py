from pathlib import Path
from typing import Dict, List, Optional, Any
import ast
import os
from dataclasses import dataclass
from enum import Enum

from ..languages.python.analyzer import PythonAnalyzer
from ..languages.go.analyzer import GoAnalyzer


class ProjectType(Enum):
    PYTHON = "python"
    GO = "go"
    JAVASCRIPT = "javascript"
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass
class FileInfo:
    path: Path
    language: str
    size: int
    functions: List[str]
    classes: List[str]
    imports: List[str]
    docstring: Optional[str] = None


@dataclass
class ModuleInfo:
    name: str
    path: Path
    files: List[FileInfo]
    public_api: List[str]
    dependencies: List[str]


@dataclass
class ProjectStructure:
    root_path: Path
    project_type: ProjectType
    main_language: str
    modules: List[ModuleInfo]
    entry_points: List[Path]
    config_files: List[Path]
    test_directories: List[Path]
    documentation_files: List[Path]
    dependencies: Dict[str, Any]


class CodebaseAnalyzer:
    """Analyzes entire codebase to understand structure and generate comprehensive documentation."""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.python_analyzer = PythonAnalyzer()
        self.go_analyzer = GoAnalyzer()
    
    def analyze_project(self) -> ProjectStructure:
        """Analyze the entire project structure."""
        project_type = self._detect_project_type()
        main_language = self._detect_main_language()
        
        modules = self._analyze_modules()
        entry_points = self._find_entry_points()
        config_files = self._find_config_files()
        test_directories = self._find_test_directories()
        documentation_files = self._find_documentation_files()
        dependencies = self._analyze_dependencies()
        
        return ProjectStructure(
            root_path=self.root_path,
            project_type=project_type,
            main_language=main_language,
            modules=modules,
            entry_points=entry_points,
            config_files=config_files,
            test_directories=test_directories,
            documentation_files=documentation_files,
            dependencies=dependencies
        )
    
    def _detect_project_type(self) -> ProjectType:
        """Detect the primary project type based on files present."""
        has_python = any(self.root_path.rglob("*.py"))
        has_go = any(self.root_path.rglob("*.go"))
        has_js = any(self.root_path.rglob("*.js")) or any(self.root_path.rglob("*.ts"))
        
        type_count = sum([has_python, has_go, has_js])
        
        if type_count > 1:
            return ProjectType.MIXED
        elif has_python:
            return ProjectType.PYTHON
        elif has_go:
            return ProjectType.GO
        elif has_js:
            return ProjectType.JAVASCRIPT
        else:
            return ProjectType.UNKNOWN
    
    def _detect_main_language(self) -> str:
        """Detect the main programming language."""
        language_counts = {}
        
        for file_path in self.root_path.rglob("*"):
            if file_path.is_file() and file_path.suffix:
                ext = file_path.suffix.lower()
                if ext in ['.py', '.go', '.js', '.ts', '.java', '.cpp', '.c', '.rs']:
                    language_counts[ext] = language_counts.get(ext, 0) + 1
        
        if not language_counts:
            return "unknown"
        
        main_ext = max(language_counts, key=language_counts.get)
        ext_to_lang = {
            '.py': 'python',
            '.go': 'go',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rs': 'rust'
        }
        
        return ext_to_lang.get(main_ext, 'unknown')
    
    def _analyze_modules(self) -> List[ModuleInfo]:
        """Analyze modules/packages in the project."""
        modules = []
        
        if self._detect_main_language() == 'python':
            modules.extend(self._analyze_python_modules())
        elif self._detect_main_language() == 'go':
            modules.extend(self._analyze_go_modules())
        
        return modules
    
    def _analyze_python_modules(self) -> List[ModuleInfo]:
        """Analyze Python modules and packages."""
        modules = []
        
        # Find Python packages (directories with __init__.py)
        for init_file in self.root_path.rglob("__init__.py"):
            package_dir = init_file.parent
            
            # Skip if this is the root directory
            if package_dir == self.root_path:
                continue
            
            # Skip virtual environments and installed packages
            if self._should_skip_directory(package_dir):
                continue
                
            module_name = package_dir.name
            files = []
            
            # Analyze all Python files in this package
            for py_file in package_dir.rglob("*.py"):
                if py_file.name.startswith('.'):
                    continue
                    
                # Skip if the file is in a directory we should skip
                if self._should_skip_directory(py_file.parent):
                    continue
                    
                file_info = self._analyze_python_file(py_file)
                if file_info:
                    files.append(file_info)
            
            if files:
                # Extract public API from __init__.py
                public_api = self._extract_public_api(init_file)
                dependencies = self._extract_dependencies(files)
                
                modules.append(ModuleInfo(
                    name=module_name,
                    path=package_dir,
                    files=files,
                    public_api=public_api,
                    dependencies=dependencies
                ))
        
        return modules
    
    def _should_skip_directory(self, directory: Path) -> bool:
        """Check if a directory should be skipped during analysis."""
        # Convert to string for easier checking
        dir_str = str(directory)
        
        # Skip common virtual environment and package directories
        skip_patterns = [
            '.venv', 'venv', 'env',
            'site-packages', 'dist-packages',
            '__pycache__', '.git', '.pytest_cache',
            'node_modules', '.tox', '.mypy_cache',
            'build', 'dist', '.coverage',
            '.env', '.vscode', '.idea'
        ]
        
        # Check if any part of the path contains skip patterns
        for pattern in skip_patterns:
            if pattern in dir_str:
                return True
        
        # Only analyze directories that are within the project structure
        # Skip if the path goes too deep into dependency directories
        try:
            relative_path = directory.relative_to(self.root_path)
            path_parts = relative_path.parts
            
            # If the path contains more than 4 levels deep, it's likely a dependency
            if len(path_parts) > 4:
                return True
            
            # Skip paths that look like installed packages (contain version numbers)
            for part in path_parts:
                if any(char.isdigit() for char in part) and ('-' in part or '.' in part):
                    return True
        except ValueError:
            # Path is not relative to root, skip it
            return True
        
        return False
    
    def _analyze_go_modules(self) -> List[ModuleInfo]:
        """Analyze Go modules and packages."""
        modules = []
        
        # Find Go packages (directories with .go files)
        go_dirs = set()
        for go_file in self.root_path.rglob("*.go"):
            go_dirs.add(go_file.parent)
        
        for go_dir in go_dirs:
            if go_dir.name.startswith('.'):
                continue
                
            module_name = go_dir.name
            files = []
            
            # Analyze all Go files in this directory
            for go_file in go_dir.glob("*.go"):
                file_info = self._analyze_go_file(go_file)
                if file_info:
                    files.append(file_info)
            
            if files:
                public_api = self._extract_go_public_api(files)
                dependencies = self._extract_dependencies(files)
                
                modules.append(ModuleInfo(
                    name=module_name,
                    path=go_dir,
                    files=files,
                    public_api=public_api,
                    dependencies=dependencies
                ))
        
        return modules
    
    def _analyze_python_file(self, file_path: Path) -> Optional[FileInfo]:
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            functions = []
            classes = []
            imports = []
            docstring = None
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    else:
                        if node.module:
                            imports.append(node.module)
            
            # Get module docstring
            if (tree.body and isinstance(tree.body[0], ast.Expr) and 
                isinstance(tree.body[0].value, ast.Constant) and 
                isinstance(tree.body[0].value.value, str)):
                docstring = tree.body[0].value.value
            
            return FileInfo(
                path=file_path,
                language='python',
                size=len(content),
                functions=functions,
                classes=classes,
                imports=imports,
                docstring=docstring
            )
        
        except Exception:
            # If we can't parse the file, return basic info
            return FileInfo(
                path=file_path,
                language='python',
                size=file_path.stat().st_size if file_path.exists() else 0,
                functions=[],
                classes=[],
                imports=[]
            )
    
    def _analyze_go_file(self, file_path: Path) -> Optional[FileInfo]:
        """Analyze a single Go file (basic implementation)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            functions = []
            imports = []
            
            # Simple regex-based parsing for Go (could be improved with proper parser)
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('func ') and not line.startswith('func ('):
                    # Extract function name
                    func_name = line.split('(')[0].replace('func ', '').strip()
                    functions.append(func_name)
                elif line.startswith('import '):
                    # Extract import
                    import_part = line.replace('import ', '').strip().strip('"')
                    if import_part:
                        imports.append(import_part)
            
            return FileInfo(
                path=file_path,
                language='go',
                size=len(content),
                functions=functions,
                classes=[],  # Go doesn't have classes
                imports=imports
            )
        
        except Exception:
            return FileInfo(
                path=file_path,
                language='go',
                size=file_path.stat().st_size if file_path.exists() else 0,
                functions=[],
                classes=[],
                imports=[]
            )
    
    def _extract_public_api(self, init_file: Path) -> List[str]:
        """Extract public API from __init__.py file."""
        try:
            with open(init_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            public_api = []
            
            # Look for __all__ definition
            for node in ast.walk(tree):
                if (isinstance(node, ast.Assign) and 
                    len(node.targets) == 1 and 
                    isinstance(node.targets[0], ast.Name) and 
                    node.targets[0].id == '__all__'):
                    if isinstance(node.value, ast.List):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                public_api.append(elt.value)
            
            return public_api
        
        except Exception:
            return []
    
    def _extract_go_public_api(self, files: List[FileInfo]) -> List[str]:
        """Extract public API from Go files (functions/types starting with uppercase)."""
        public_api = []
        
        for file_info in files:
            for func_name in file_info.functions:
                if func_name and func_name[0].isupper():
                    public_api.append(func_name)
        
        return public_api
    
    def _extract_dependencies(self, files: List[FileInfo]) -> List[str]:
        """Extract unique dependencies from files."""
        all_imports = []
        for file_info in files:
            all_imports.extend(file_info.imports)
        
        # Filter out standard library and relative imports
        external_deps = []
        for imp in set(all_imports):
            if not imp.startswith('.') and '/' in imp or imp not in ['os', 'sys', 'json', 'time']:
                external_deps.append(imp)
        
        return list(set(external_deps))
    
    def _find_entry_points(self) -> List[Path]:
        """Find potential entry points (main files, scripts, etc.)."""
        entry_points = []
        
        # Look for common entry point files
        common_entries = ['main.py', 'app.py', '__main__.py', 'main.go', 'cmd', 'cli']
        
        for pattern in common_entries:
            matches = list(self.root_path.rglob(pattern))
            entry_points.extend(matches)
        
        # Also check for executable Python files
        for py_file in self.root_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    first_lines = f.read(200)
                    if 'if __name__ == "__main__"' in first_lines:
                        entry_points.append(py_file)
            except Exception:
                continue
        
        return list(set(entry_points))
    
    def _find_config_files(self) -> List[Path]:
        """Find configuration files."""
        config_patterns = [
            '*.toml', '*.yaml', '*.yml', '*.json', '*.ini', '*.cfg',
            'Dockerfile', 'docker-compose*', 'requirements.txt', 'setup.py',
            'pyproject.toml', 'go.mod', 'package.json', 'Cargo.toml'
        ]
        
        config_files = []
        for pattern in config_patterns:
            matches = list(self.root_path.rglob(pattern))
            config_files.extend(matches)
        
        return config_files
    
    def _find_test_directories(self) -> List[Path]:
        """Find test directories and files."""
        test_dirs = set()
        
        # Look for test directories
        for test_dir in self.root_path.rglob("test*"):
            if test_dir.is_dir():
                test_dirs.add(test_dir)
        
        # Look for test files
        for test_file in self.root_path.rglob("test_*.py"):
            test_dirs.add(test_file.parent)
        
        for test_file in self.root_path.rglob("*_test.go"):
            test_dirs.add(test_file.parent)
        
        return list(test_dirs)
    
    def _find_documentation_files(self) -> List[Path]:
        """Find existing documentation files."""
        doc_patterns = ['README*', 'CHANGELOG*', 'LICENSE*', 'CONTRIBUTING*', 'docs/*', '*.md']
        
        doc_files = []
        for pattern in doc_patterns:
            matches = list(self.root_path.rglob(pattern))
            doc_files.extend([f for f in matches if f.is_file()])
        
        return doc_files
    
    def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies from various sources."""
        dependencies = {}
        
        # Python dependencies
        requirements_file = self.root_path / "requirements.txt"
        if requirements_file.exists():
            try:
                with open(requirements_file, 'r') as f:
                    dependencies['python'] = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            except Exception:
                pass
        
        pyproject_file = self.root_path / "pyproject.toml"
        if pyproject_file.exists():
            try:
                import toml
                with open(pyproject_file, 'r') as f:
                    pyproject_data = toml.load(f)
                    if 'project' in pyproject_data and 'dependencies' in pyproject_data['project']:
                        dependencies['python'] = pyproject_data['project']['dependencies']
            except Exception:
                pass
        
        # Go dependencies
        go_mod_file = self.root_path / "go.mod"
        if go_mod_file.exists():
            try:
                with open(go_mod_file, 'r') as f:
                    go_deps = []
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('module') and not line.startswith('go ') and not line.startswith('//'):
                            go_deps.append(line)
                    dependencies['go'] = go_deps
            except Exception:
                pass
        
        return dependencies