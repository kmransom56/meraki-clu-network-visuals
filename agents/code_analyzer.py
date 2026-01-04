"""
Code Analyzer Agent - Analyzes codebase for issues and optimization opportunities
"""

import os
import ast
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime
from collections import defaultdict

from .agent_framework import AgentFramework, AgentBackend

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """
    Analyzes codebase for issues, bugs, and optimization opportunities
    """
    
    def __init__(self, agent_framework: Optional[AgentFramework] = None):
        self.agent = agent_framework or AgentFramework(AgentBackend.AUTOGEN)
        self.codebase_root = Path('.')
        self.issues = []
        self.optimizations = []
    
    def analyze_codebase(self, paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze the codebase for issues
        
        Args:
            paths: Specific paths to analyze (default: all Python files)
            
        Returns:
            Analysis results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'files_analyzed': 0,
            'issues': [],
            'optimizations': [],
            'metrics': {},
            'recommendations': []
        }
        
        python_files = self._get_python_files(paths)
        results['files_analyzed'] = len(python_files)
        
        for file_path in python_files:
            file_results = self._analyze_file(file_path)
            results['issues'].extend(file_results.get('issues', []))
            results['optimizations'].extend(file_results.get('optimizations', []))
        
        # Calculate metrics
        results['metrics'] = self._calculate_metrics(results)
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    def _get_python_files(self, paths: Optional[List[str]]) -> List[Path]:
        """Get list of Python files to analyze"""
        if paths:
            return [Path(p) for p in paths if p.endswith('.py')]
        
        # Get all Python files, excluding venv and __pycache__
        python_files = []
        exclude_dirs = {'venv', '__pycache__', '.git', 'node_modules', '.venv'}
        
        for root, dirs, files in os.walk(self.codebase_root):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def _analyze_file(self, file_path: Path) -> Dict:
        """Analyze a single Python file"""
        results = {
            'file': str(file_path),
            'issues': [],
            'optimizations': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content, filename=str(file_path))
            
            # AST-based analysis
            ast_issues = self._analyze_ast(tree, file_path)
            results['issues'].extend(ast_issues)
            
            # Pattern-based analysis
            pattern_issues = self._analyze_patterns(content, file_path)
            results['issues'].extend(pattern_issues)
            
            # Optimization opportunities
            optimizations = self._find_optimizations(content, file_path)
            results['optimizations'].extend(optimizations)
        
        except SyntaxError as e:
            results['issues'].append({
                'type': 'syntax_error',
                'severity': 'high',
                'message': f"Syntax error: {e}",
                'line': e.lineno
            })
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            results['error'] = str(e)
        
        return results
    
    def _analyze_ast(self, tree: ast.AST, file_path: Path) -> List[Dict]:
        """Analyze AST for issues"""
        issues = []
        visitor = CodeIssueVisitor(file_path)
        visitor.visit(tree)
        return visitor.issues
    
    def _analyze_patterns(self, content: str, file_path: Path) -> List[Dict]:
        """Analyze code patterns for common issues"""
        issues = []
        lines = content.split('\n')
        
        # Check for common anti-patterns
        patterns = {
            'bare_except': (r'except\s*:', 'Use specific exception types'),
            'print_debug': (r'print\s*\(', 'Use logging instead of print'),
            'hardcoded_paths': (r'["\']/[A-Za-z]:|["\']C:\\', 'Avoid hardcoded paths'),
            'todo_comments': (r'#\s*TODO|#\s*FIXME|#\s*XXX', 'Address TODO comments'),
            'long_functions': (self._check_long_functions, 'Functions should be < 50 lines'),
            'duplicate_code': (self._check_duplicates, 'Potential code duplication'),
        }
        
        for i, line in enumerate(lines, 1):
            for pattern_name, (pattern, message) in patterns.items():
                if isinstance(pattern, str):
                    if re.search(pattern, line):
                        issues.append({
                            'type': pattern_name,
                            'severity': 'medium',
                            'message': message,
                            'line': i,
                            'file': str(file_path)
                        })
                else:
                    # Custom check function
                    result = pattern(content, i)
                    if result:
                        issues.append({
                            'type': pattern_name,
                            'severity': 'low',
                            'message': message,
                            'line': i,
                            'file': str(file_path),
                            'details': result
                        })
        
        return issues
    
    def _check_long_functions(self, content: str, line_num: int) -> Optional[str]:
        """Check for long functions"""
        # Simplified check - in production, use AST to get actual function length
        return None
    
    def _check_duplicates(self, content: str, line_num: int) -> Optional[str]:
        """Check for duplicate code patterns"""
        # Simplified check
        return None
    
    def _find_optimizations(self, content: str, file_path: Path) -> List[Dict]:
        """Find optimization opportunities"""
        optimizations = []
        
        # Check for inefficient patterns
        if 'for i in range(len(' in content:
            optimizations.append({
                'type': 'inefficient_iteration',
                'suggestion': 'Use enumerate() instead of range(len())',
                'file': str(file_path)
            })
        
        if re.search(r'\.append\([^)]+\)\s*\n\s*\.append\(', content):
            optimizations.append({
                'type': 'multiple_append',
                'suggestion': 'Use list comprehension or extend()',
                'file': str(file_path)
            })
        
        return optimizations
    
    def _calculate_metrics(self, results: Dict) -> Dict:
        """Calculate codebase metrics"""
        return {
            'total_issues': len(results.get('issues', [])),
            'high_severity': len([i for i in results.get('issues', []) if i.get('severity') == 'high']),
            'medium_severity': len([i for i in results.get('issues', []) if i.get('severity') == 'medium']),
            'low_severity': len([i for i in results.get('issues', []) if i.get('severity') == 'low']),
            'optimization_opportunities': len(results.get('optimizations', []))
        }
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate recommendations using AI agent"""
        context = {
            'issues': results.get('issues', [])[:10],  # Top 10 issues
            'optimizations': results.get('optimizations', [])[:5],
            'metrics': results.get('metrics', {})
        }
        
        prompt = f"""Analyze these code issues and provide specific recommendations:
        
Issues: {json.dumps(context['issues'], indent=2)}
Optimizations: {json.dumps(context['optimizations'], indent=2)}
Metrics: {json.dumps(context['metrics'], indent=2)}

Provide actionable recommendations to improve code quality."""
        
        try:
            analysis = self.agent.analyze(prompt, context)
            if 'response' in analysis:
                return self._parse_recommendations(analysis['response'])
        except Exception as e:
            logger.error(f"Failed to generate AI recommendations: {e}")
        
        return self._generate_fallback_recommendations(results)
    
    def _parse_recommendations(self, response: str) -> List[str]:
        """Parse recommendations from AI response"""
        recommendations = []
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('*') or 
                        re.match(r'^\d+[.)]', line)):
                recommendations.append(line.lstrip('-* ').lstrip('0123456789.) '))
        return recommendations if recommendations else [response]
    
    def _generate_fallback_recommendations(self, results: Dict) -> List[str]:
        """Generate basic recommendations"""
        recommendations = []
        metrics = results.get('metrics', {})
        
        if metrics.get('high_severity', 0) > 0:
            recommendations.append("Address high-severity issues immediately")
        
        if metrics.get('optimization_opportunities', 0) > 0:
            recommendations.append("Review and implement optimization opportunities")
        
        return recommendations


class CodeIssueVisitor(ast.NodeVisitor):
    """AST visitor to find code issues"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.issues = []
    
    def visit_ExceptHandler(self, node):
        """Check for bare except clauses"""
        if node.type is None:
            self.issues.append({
                'type': 'bare_except',
                'severity': 'medium',
                'message': 'Bare except clause - catch specific exceptions',
                'line': node.lineno,
                'file': str(self.file_path)
            })
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Check function complexity"""
        # Count lines in function
        if hasattr(node, 'end_lineno') and node.end_lineno:
            lines = node.end_lineno - node.lineno
            if lines > 50:
                self.issues.append({
                    'type': 'long_function',
                    'severity': 'low',
                    'message': f'Function {node.name} is {lines} lines long',
                    'line': node.lineno,
                    'file': str(self.file_path)
                })
        self.generic_visit(node)
