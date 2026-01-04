"""
Repair Agent - Automatically fixes issues found by analyzers
"""

import os
import re
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from .agent_framework import AgentFramework, AgentBackend
from .log_analyzer import LogAnalyzer
from .code_analyzer import CodeAnalyzer

logger = logging.getLogger(__name__)


class RepairAgent:
    """
    Automatically repairs issues found in logs and code
    """
    
    def __init__(self, agent_framework: Optional[AgentFramework] = None):
        self.agent = agent_framework or AgentFramework(AgentBackend.AUTOGEN)
        self.log_analyzer = LogAnalyzer(agent_framework)
        self.code_analyzer = CodeAnalyzer(agent_framework)
        self.repair_history = []
        self.backup_dir = Path('agent_backups')
        self.backup_dir.mkdir(exist_ok=True)
    
    def auto_repair(self, repair_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Automatically repair issues
        
        Args:
            repair_types: Types of repairs to perform (default: all)
            
        Returns:
            Repair results
        """
        repair_types = repair_types or ['logs', 'code', 'dependencies']
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'repairs': [],
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
        
        # Analyze first
        log_analysis = self.log_analyzer.analyze_logs(hours=24)
        code_analysis = self.code_analyzer.analyze_codebase()
        
        # Perform repairs
        if 'logs' in repair_types:
            log_repairs = self._repair_log_issues(log_analysis)
            results['repairs'].extend(log_repairs)
        
        if 'code' in repair_types:
            code_repairs = self._repair_code_issues(code_analysis)
            results['repairs'].extend(code_repairs)
        
        if 'dependencies' in repair_types:
            dep_repairs = self._repair_dependencies()
            results['repairs'].extend(dep_repairs)
        
        # Count results
        for repair in results['repairs']:
            if repair.get('status') == 'success':
                results['success'] += 1
            elif repair.get('status') == 'failed':
                results['failed'] += 1
            else:
                results['skipped'] += 1
        
        return results
    
    def _repair_log_issues(self, analysis: Dict) -> List[Dict]:
        """Repair issues found in logs"""
        repairs = []
        
        for error in analysis.get('errors', [])[:5]:  # Limit to 5 repairs
            error_type = error.get('type', 'unknown')
            
            if error_type == 'import_errors':
                repair = self._repair_import_error(error)
                repairs.append(repair)
            elif error_type == 'api_errors':
                repair = self._repair_api_error(error)
                repairs.append(repair)
            elif error_type == 'attribute_errors':
                repair = self._repair_attribute_error(error)
                repairs.append(repair)
        
        return repairs
    
    def _repair_code_issues(self, analysis: Dict) -> List[Dict]:
        """Repair issues found in code"""
        repairs = []
        
        for issue in analysis.get('issues', []):
            if issue.get('severity') == 'high':
                repair = self._repair_code_issue(issue)
                repairs.append(repair)
        
        return repairs
    
    def _repair_import_error(self, error: Dict) -> Dict:
        """Repair import errors"""
        error_line = error.get('line', '')
        
        # Extract module name from error
        match = re.search(r'No module named [\'"]([^\'"]+)[\'"]', error_line)
        if match:
            module_name = match.group(1)
            
            # Try to add to requirements.txt
            try:
                self._add_to_requirements(module_name)
                return {
                    'type': 'import_error',
                    'status': 'success',
                    'action': f'Added {module_name} to requirements.txt',
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                return {
                    'type': 'import_error',
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        return {
            'type': 'import_error',
            'status': 'skipped',
            'reason': 'Could not extract module name',
            'timestamp': datetime.now().isoformat()
        }
    
    def _repair_api_error(self, error: Dict) -> Dict:
        """Repair API errors"""
        # API errors typically need manual intervention
        return {
            'type': 'api_error',
            'status': 'skipped',
            'reason': 'API errors require manual verification',
            'recommendation': 'Check API key and network connectivity',
            'timestamp': datetime.now().isoformat()
        }
    
    def _repair_attribute_error(self, error: Dict) -> Dict:
        """Repair attribute errors using AI"""
        error_line = error.get('line', '')
        
        # Use AI to suggest fix
        prompt = f"""Fix this Python AttributeError:
        
{error_line}

Provide the corrected code."""
        
        try:
            analysis = self.agent.analyze(prompt, {'error': error})
            if 'response' in analysis:
                return {
                    'type': 'attribute_error',
                    'status': 'suggested',
                    'suggestion': analysis['response'],
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Failed to repair attribute error: {e}")
        
        return {
            'type': 'attribute_error',
            'status': 'skipped',
            'reason': 'Could not generate fix',
            'timestamp': datetime.now().isoformat()
        }
    
    def _repair_code_issue(self, issue: Dict) -> Dict:
        """Repair a code issue"""
        issue_type = issue.get('type')
        file_path = issue.get('file')
        
        if not file_path or not os.path.exists(file_path):
            return {
                'type': issue_type,
                'status': 'skipped',
                'reason': 'File not found',
                'timestamp': datetime.now().isoformat()
            }
        
        # Create backup
        backup_path = self._create_backup(file_path)
        
        try:
            if issue_type == 'bare_except':
                return self._fix_bare_except(file_path, issue, backup_path)
            elif issue_type == 'syntax_error':
                return self._fix_syntax_error(file_path, issue, backup_path)
            else:
                return {
                    'type': issue_type,
                    'status': 'skipped',
                    'reason': f'No auto-fix available for {issue_type}',
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            # Restore backup on error
            self._restore_backup(file_path, backup_path)
            return {
                'type': issue_type,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _fix_bare_except(self, file_path: str, issue: Dict, backup_path: Path) -> Dict:
        """Fix bare except clauses"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace bare except with Exception
        fixed_content = re.sub(
            r'except\s*:',
            'except Exception:',
            content
        )
        
        if fixed_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            return {
                'type': 'bare_except',
                'status': 'success',
                'action': f'Fixed bare except in {file_path}',
                'backup': str(backup_path),
                'timestamp': datetime.now().isoformat()
            }
        
        return {
            'type': 'bare_except',
            'status': 'skipped',
            'reason': 'No changes needed',
            'timestamp': datetime.now().isoformat()
        }
    
    def _fix_syntax_error(self, file_path: str, issue: Dict, backup_path: Path) -> Dict:
        """Fix syntax errors using AI"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        prompt = f"""Fix the syntax error in this Python code:
        
{content}

Error: {issue.get('message', '')}
Line: {issue.get('line', '')}

Provide the corrected code."""
        
        try:
            analysis = self.agent.analyze(prompt, {'issue': issue})
            if 'response' in analysis:
                # Extract code from response
                fixed_code = self._extract_code_from_response(analysis['response'])
                if fixed_code:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_code)
                    
                    return {
                        'type': 'syntax_error',
                        'status': 'success',
                        'action': f'Fixed syntax error in {file_path}',
                        'backup': str(backup_path),
                        'timestamp': datetime.now().isoformat()
                    }
        except Exception as e:
            logger.error(f"Failed to fix syntax error: {e}")
        
        return {
            'type': 'syntax_error',
            'status': 'failed',
            'reason': 'Could not generate fix',
            'timestamp': datetime.now().isoformat()
        }
    
    def _repair_dependencies(self) -> List[Dict]:
        """Repair dependency issues"""
        repairs = []
        
        # Check requirements.txt
        if os.path.exists('requirements.txt'):
            try:
                # Run pipreqs to update requirements
                import subprocess
                result = subprocess.run(
                    ['pipreqs', '.', '--force', '--encoding=utf-8', '--ignore', '.venv,scripts,tests'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    repairs.append({
                        'type': 'dependencies',
                        'status': 'success',
                        'action': 'Updated requirements.txt',
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    repairs.append({
                        'type': 'dependencies',
                        'status': 'failed',
                        'error': result.stderr,
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                repairs.append({
                    'type': 'dependencies',
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        return repairs
    
    def _add_to_requirements(self, module_name: str):
        """Add module to requirements.txt"""
        # Map common module names to package names
        package_map = {
            'PIL': 'Pillow',
            'yaml': 'PyYAML',
            'dotenv': 'python-dotenv'
        }
        
        package_name = package_map.get(module_name, module_name)
        
        if os.path.exists('requirements.txt'):
            with open('requirements.txt', 'r') as f:
                content = f.read()
            
            # Check if already present
            if package_name.lower() in content.lower():
                return
            
            # Add to requirements
            with open('requirements.txt', 'a') as f:
                f.write(f'\n{package_name}\n')
    
    def _create_backup(self, file_path: str) -> Path:
        """Create backup of file before modification"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{Path(file_path).stem}_{timestamp}{Path(file_path).suffix}"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def _restore_backup(self, file_path: str, backup_path: Path):
        """Restore file from backup"""
        if backup_path.exists():
            shutil.copy2(backup_path, file_path)
    
    def _extract_code_from_response(self, response: str) -> Optional[str]:
        """Extract Python code from AI response"""
        # Look for code blocks
        code_match = re.search(r'```(?:python)?\n(.*?)\n```', response, re.DOTALL)
        if code_match:
            return code_match.group(1)
        
        # If no code block, return response as-is (might be just code)
        if 'def ' in response or 'import ' in response:
            return response
        
        return None
