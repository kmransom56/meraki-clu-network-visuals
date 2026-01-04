"""
CLI interface for the self-healing agent system
"""

import argparse
import json
import sys
from pathlib import Path
from termcolor import colored

from .agent_manager import AgentManager
from .agent_framework import AgentBackend


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Self-Auditing and Self-Healing Agent System'
    )
    
    parser.add_argument(
        '--backend',
        choices=['autogen', 'magentic_one', 'docker_cagent', 'openai'],
        default='autogen',
        help='Agent backend to use'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to agent configuration file'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Audit command
    audit_parser = subparsers.add_parser('audit', help='Run full application audit')
    
    # Repair command
    repair_parser = subparsers.add_parser('repair', help='Run automatic repairs')
    repair_parser.add_argument(
        '--types',
        nargs='+',
        choices=['logs', 'code', 'dependencies'],
        default=['logs', 'code', 'dependencies'],
        help='Types of repairs to perform'
    )
    
    # Optimize command
    optimize_parser = subparsers.add_parser('optimize', help='Run optimizations')
    optimize_parser.add_argument(
        '--types',
        nargs='+',
        choices=['code', 'performance', 'dependencies'],
        default=['code', 'performance', 'dependencies'],
        help='Types of optimizations to perform'
    )
    
    # Insights command
    subparsers.add_parser('insights', help='Get insights from learned patterns')
    
    # Status command
    subparsers.add_parser('status', help='Get agent status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Load config
    config = {}
    if args.config and Path(args.config).exists():
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Initialize agent manager
    backend_map = {
        'autogen': AgentBackend.AUTOGEN,
        'magentic_one': AgentBackend.MAGENTIC_ONE,
        'docker_cagent': AgentBackend.DOCKER_CAGENT,
        'openai': AgentBackend.OPENAI
    }
    
    backend = backend_map.get(args.backend, AgentBackend.AUTOGEN)
    manager = AgentManager(backend, config)
    
    # Execute command
    try:
        if args.command == 'audit':
            print(colored("Running full audit...", "cyan"))
            results = manager.run_full_audit()
            print_results(results)
        
        elif args.command == 'repair':
            print(colored(f"Running repairs: {', '.join(args.types)}...", "cyan"))
            results = manager.run_auto_repair(args.types)
            print_repair_results(results)
        
        elif args.command == 'optimize':
            print(colored(f"Running optimizations: {', '.join(args.types)}...", "cyan"))
            results = manager.run_optimization(args.types)
            print_optimization_results(results)
        
        elif args.command == 'insights':
            print(colored("Generating insights...", "cyan"))
            insights = manager.get_insights()
            print_insights(insights)
        
        elif args.command == 'status':
            status = manager.get_status()
            print_status(status)
    
    except Exception as e:
        print(colored(f"Error: {e}", "red"))
        sys.exit(1)


def print_results(results: dict):
    """Print audit results"""
    print("\n" + "=" * 60)
    print(colored("AUDIT RESULTS", "green", attrs=['bold']))
    print("=" * 60)
    
    # Log analysis
    log_analysis = results.get('log_analysis', {})
    if log_analysis:
        print("\n" + colored("Log Analysis:", "yellow"))
        print(f"  Errors found: {len(log_analysis.get('errors', []))}")
        print(f"  Warnings: {len(log_analysis.get('warnings', []))}")
        if log_analysis.get('patterns'):
            print("  Error patterns:")
            for pattern, count in log_analysis['patterns'].items():
                print(f"    - {pattern}: {count}")
    
    # Code analysis
    code_analysis = results.get('code_analysis', {})
    if code_analysis:
        print("\n" + colored("Code Analysis:", "yellow"))
        metrics = code_analysis.get('metrics', {})
        print(f"  Files analyzed: {code_analysis.get('files_analyzed', 0)}")
        print(f"  Issues found: {metrics.get('total_issues', 0)}")
        print(f"    - High severity: {metrics.get('high_severity', 0)}")
        print(f"    - Medium severity: {metrics.get('medium_severity', 0)}")
        print(f"    - Low severity: {metrics.get('low_severity', 0)}")
    
    # Recommendations
    recommendations = results.get('recommendations', [])
    if recommendations:
        print("\n" + colored("Recommendations:", "yellow"))
        for i, rec in enumerate(recommendations[:10], 1):
            print(f"  {i}. {rec}")
    
    print("\n" + "=" * 60)


def print_repair_results(results: dict):
    """Print repair results"""
    print("\n" + "=" * 60)
    print(colored("REPAIR RESULTS", "green", attrs=['bold']))
    print("=" * 60)
    
    print(f"\nSuccess: {results.get('success', 0)}")
    print(f"Failed: {results.get('failed', 0)}")
    print(f"Skipped: {results.get('skipped', 0)}")
    
    repairs = results.get('repairs', [])
    if repairs:
        print("\n" + colored("Repairs performed:", "yellow"))
        for repair in repairs:
            status_color = 'green' if repair.get('status') == 'success' else 'red'
            print(f"  [{colored(repair.get('status', 'unknown').upper(), status_color)}] {repair.get('type', 'unknown')}")
            if repair.get('action'):
                print(f"    {repair.get('action')}")
    
    print("\n" + "=" * 60)


def print_optimization_results(results: dict):
    """Print optimization results"""
    print("\n" + "=" * 60)
    print(colored("OPTIMIZATION RESULTS", "green", attrs=['bold']))
    print("=" * 60)
    
    improvements = results.get('improvements', [])
    if improvements:
        print("\n" + colored("Improvements:", "yellow"))
        for improvement in improvements:
            print(f"  {improvement.get('metric')}: {improvement.get('improvement')}")
            print(f"    Before: {improvement.get('before')}, After: {improvement.get('after')}")
    
    print("\n" + "=" * 60)


def print_insights(insights: dict):
    """Print insights"""
    print("\n" + "=" * 60)
    print(colored("INSIGHTS", "green", attrs=['bold']))
    print("=" * 60)
    
    common_errors = insights.get('common_errors', [])
    if common_errors:
        print("\n" + colored("Most Common Errors:", "yellow"))
        for error in common_errors:
            print(f"  {error.get('type')}: {error.get('count')} occurrences")
    
    effective_fixes = insights.get('effective_fixes', [])
    if effective_fixes:
        print("\n" + colored("Most Effective Fixes:", "yellow"))
        for fix in effective_fixes:
            print(f"  {fix.get('error_type')}: {fix.get('fix_action')}")
            print(f"    Success rate: {fix.get('success_rate', 0):.1%}")
    
    recommendations = insights.get('recommendations', [])
    if recommendations:
        print("\n" + colored("Recommendations:", "yellow"))
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    print("\n" + "=" * 60)


def print_status(status: dict):
    """Print agent status"""
    print("\n" + "=" * 60)
    print(colored("AGENT STATUS", "green", attrs=['bold']))
    print("=" * 60)
    
    if 'last_run' in status:
        print(f"\nLast run: {status.get('last_run')}")
    
    results = status.get('results', {})
    if results:
        print(f"Status: {results.get('status', 'unknown')}")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
