"""
Log Analyzer Agent - Analyzes application logs to identify issues
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from collections import defaultdict

from .agent_framework import AgentFramework, AgentBackend

logger = logging.getLogger(__name__)


class LogAnalyzer:
    """
    Analyzes application logs to identify patterns, errors, and issues
    """
    
    def __init__(self, agent_framework: Optional[AgentFramework] = None):
        self.agent = agent_framework or AgentFramework(AgentBackend.AUTOGEN)
        self.log_files = {
            'debug': 'meraki_clu_debug.log',
            'error': 'log/error.log'
        }
        self.error_patterns = self._load_error_patterns()
    
    def _load_error_patterns(self) -> Dict[str, List[str]]:
        """Load known error patterns"""
        return {
            'import_errors': [
                r'ModuleNotFoundError',
                r'ImportError',
                r'No module named'
            ],
            'api_errors': [
                r'API.*error',
                r'HTTP.*error',
                r'Connection.*error',
                r'Timeout',
                r'401|403|404|500'
            ],
            'attribute_errors': [
                r'AttributeError',
                r'has no attribute'
            ],
            'type_errors': [
                r'TypeError',
                r'unsupported operand'
            ],
            'value_errors': [
                r'ValueError',
                r'invalid.*value'
            ],
            'key_errors': [
                r'KeyError',
                r'key.*not found'
            ],
            'ssl_errors': [
                r'SSL',
                r'certificate',
                r'CERTIFICATE_VERIFY_FAILED'
            ],
            'database_errors': [
                r'Database',
                r'SQL',
                r'db.*error'
            ]
        }
    
    def analyze_logs(self, hours: int = 24, log_type: str = 'all') -> Dict[str, Any]:
        """
        Analyze logs for the specified time period
        
        Args:
            hours: Number of hours to analyze
            log_type: 'debug', 'error', or 'all'
            
        Returns:
            Analysis results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'period_hours': hours,
            'errors': [],
            'warnings': [],
            'patterns': {},
            'recommendations': []
        }
        
        if log_type in ['debug', 'all']:
            debug_results = self._analyze_file(self.log_files['debug'], hours)
            results['debug'] = debug_results
        
        if log_type in ['error', 'all']:
            error_results = self._analyze_file(self.log_files['error'], hours)
            results['errors'].extend(error_results.get('errors', []))
            results['warnings'].extend(error_results.get('warnings', []))
        
        # Pattern analysis
        results['patterns'] = self._analyze_patterns(results)
        
        # Generate recommendations using AI agent
        results['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    def _analyze_file(self, log_file: str, hours: int) -> Dict:
        """Analyze a specific log file"""
        results = {
            'file': log_file,
            'errors': [],
            'warnings': [],
            'info_count': 0,
            'total_lines': 0
        }
        
        if not os.path.exists(log_file):
            results['error'] = f"Log file not found: {log_file}"
            return results
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    results['total_lines'] += 1
                    
                    # Parse timestamp if present
                    timestamp = self._extract_timestamp(line)
                    if timestamp and timestamp < cutoff_time:
                        continue
                    
                    # Check for errors
                    if self._is_error(line):
                        results['errors'].append({
                            'line': line.strip(),
                            'timestamp': timestamp.isoformat() if timestamp else None,
                            'type': self._classify_error(line)
                        })
                    
                    # Check for warnings
                    elif self._is_warning(line):
                        results['warnings'].append({
                            'line': line.strip(),
                            'timestamp': timestamp.isoformat() if timestamp else None
                        })
                    
                    elif 'INFO' in line.upper():
                        results['info_count'] += 1
        
        except Exception as e:
            logger.error(f"Error analyzing log file {log_file}: {e}")
            results['error'] = str(e)
        
        return results
    
    def _extract_timestamp(self, line: str) -> Optional[datetime]:
        """Extract timestamp from log line"""
        # Common log formats: 2026-01-03 19:39:40,497 or 2026-01-03T19:39:40
        patterns = [
            r'(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}[.,]\d+)',
            r'(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    ts_str = match.group(1).replace(',', '.').replace('T', ' ')
                    return datetime.strptime(ts_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
                except:
                    continue
        
        return None
    
    def _is_error(self, line: str) -> bool:
        """Check if line contains an error"""
        error_indicators = ['ERROR', 'Exception', 'Traceback', 'Failed', 'Error']
        return any(indicator in line for indicator in error_indicators)
    
    def _is_warning(self, line: str) -> bool:
        """Check if line contains a warning"""
        return 'WARNING' in line.upper() or 'WARN' in line.upper()
    
    def _classify_error(self, line: str) -> str:
        """Classify error type"""
        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return error_type
        return 'unknown'
    
    def _analyze_patterns(self, results: Dict) -> Dict:
        """Analyze error patterns and frequencies"""
        patterns = defaultdict(int)
        
        for error in results.get('errors', []):
            error_type = error.get('type', 'unknown')
            patterns[error_type] += 1
        
        return dict(patterns)
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate recommendations using AI agent"""
        if not results.get('errors'):
            return ["No errors found in the analyzed period."]
        
        # Prepare context for AI agent
        context = {
            'error_count': len(results.get('errors', [])),
            'error_patterns': results.get('patterns', {}),
            'sample_errors': results.get('errors', [])[:5]  # First 5 errors
        }
        
        prompt = f"""Analyze these application errors and provide specific recommendations:
        
Error Patterns: {context['error_patterns']}
Sample Errors: {json.dumps(context['sample_errors'], indent=2)}

Provide actionable recommendations to fix these issues."""
        
        try:
            analysis = self.agent.analyze(prompt, context)
            if 'response' in analysis:
                # Parse recommendations from response
                recommendations = self._parse_recommendations(analysis['response'])
                return recommendations
        except Exception as e:
            logger.error(f"Failed to generate AI recommendations: {e}")
        
        # Fallback recommendations
        return self._generate_fallback_recommendations(results)
    
    def _parse_recommendations(self, response: str) -> List[str]:
        """Parse recommendations from AI response"""
        recommendations = []
        
        # Look for numbered or bulleted lists
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('*') or 
                        re.match(r'^\d+[.)]', line)):
                recommendations.append(line.lstrip('-* ').lstrip('0123456789.) '))
        
        return recommendations if recommendations else [response]
    
    def _generate_fallback_recommendations(self, results: Dict) -> List[str]:
        """Generate basic recommendations without AI"""
        recommendations = []
        patterns = results.get('patterns', {})
        
        if 'import_errors' in patterns:
            recommendations.append("Check and update requirements.txt for missing dependencies")
        
        if 'api_errors' in patterns:
            recommendations.append("Verify API key validity and network connectivity")
        
        if 'attribute_errors' in patterns:
            recommendations.append("Review code for missing method/attribute implementations")
        
        if 'ssl_errors' in patterns:
            recommendations.append("Check SSL certificate configuration and proxy settings")
        
        return recommendations
    
    def get_recent_errors(self, count: int = 10) -> List[Dict]:
        """Get most recent errors"""
        if not os.path.exists(self.log_files['error']):
            return []
        
        errors = []
        try:
            with open(self.log_files['error'], 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                # Read from end of file
                for line in reversed(lines[-100:]):  # Check last 100 lines
                    if self._is_error(line):
                        errors.append({
                            'line': line.strip(),
                            'timestamp': self._extract_timestamp(line)
                        })
                        if len(errors) >= count:
                            break
        except Exception as e:
            logger.error(f"Error reading recent errors: {e}")
        
        return errors
