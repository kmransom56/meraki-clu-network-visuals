"""
Agent Menu - Interactive menu for the self-healing agent system
"""

from termcolor import colored
from .agent_manager import AgentManager
from .agent_framework import AgentBackend
import json
from pathlib import Path


def agent_menu(fernet, agent_manager=None):
    """Display agent system menu"""
    # Use provided agent manager or create new one
    if agent_manager is None:
        agent_manager = AgentManager()
    while True:
        print("\n" + "=" * 60)
        print(colored("Self-Healing Agent System", "cyan", attrs=['bold']))
        print("=" * 60)
        print("1. Run Full Audit")
        print("2. Auto-Repair Issues")
        print("3. Optimize Application")
        print("4. View Insights")
        print("5. Agent Status")
        print("6. Configure Agent")
        print("7. Back to Main Menu")
        
        choice = input(colored("\nChoose an option [1-7]: ", "cyan"))
        
        if choice == '1':
            run_audit(agent_manager)
        elif choice == '2':
            run_repair(agent_manager)
        elif choice == '3':
            run_optimize(agent_manager)
        elif choice == '4':
            view_insights(agent_manager)
        elif choice == '5':
            view_status(agent_manager)
        elif choice == '6':
            configure_agent()
        elif choice == '7':
            break
        else:
            print(colored("Invalid option. Please try again.", "red"))


def run_audit(agent_manager=None):
    """Run full application audit"""
    print(colored("\nRunning full audit...", "yellow"))
    try:
        if agent_manager is None:
            agent_manager = AgentManager()
        results = agent_manager.run_full_audit()
        
        print(colored("\nAudit Complete!", "green"))
        print(f"Status: {results.get('status', 'unknown')}")
        
        # Show summary
        log_analysis = results.get('log_analysis', {})
        code_analysis = results.get('code_analysis', {})
        
        if log_analysis:
            print(f"\nLog Analysis:")
            print(f"  Errors: {len(log_analysis.get('errors', []))}")
            print(f"  Warnings: {len(log_analysis.get('warnings', []))}")
        
        if code_analysis:
            metrics = code_analysis.get('metrics', {})
            print(f"\nCode Analysis:")
            print(f"  Files analyzed: {code_analysis.get('files_analyzed', 0)}")
            print(f"  Issues found: {metrics.get('total_issues', 0)}")
        
        recommendations = results.get('recommendations', [])
        if recommendations:
            print(colored("\nTop Recommendations:", "yellow"))
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"  {i}. {rec}")
    
    except Exception as e:
        print(colored(f"Error running audit: {e}", "red"))


def run_repair(agent_manager=None):
    """Run automatic repairs"""
    print(colored("\nAuto-Repair Options:", "yellow"))
    print("1. Repair Log Issues")
    print("2. Repair Code Issues")
    print("3. Repair Dependencies")
    print("4. Repair All")
    
    choice = input(colored("\nChoose repair type [1-4]: ", "cyan"))
    
    repair_types = {
        '1': ['logs'],
        '2': ['code'],
        '3': ['dependencies'],
        '4': ['logs', 'code', 'dependencies']
    }
    
    types = repair_types.get(choice, ['logs', 'code', 'dependencies'])
    
    print(colored(f"\nRunning repairs: {', '.join(types)}...", "yellow"))
    try:
        if agent_manager is None:
            agent_manager = AgentManager()
        results = agent_manager.run_auto_repair(types)
        
        print(colored("\nRepair Complete!", "green"))
        print(f"Success: {results.get('success', 0)}")
        print(f"Failed: {results.get('failed', 0)}")
        print(f"Skipped: {results.get('skipped', 0)}")
        
        repairs = results.get('repairs', [])
        if repairs:
            print(colored("\nRepairs performed:", "yellow"))
            for repair in repairs[:10]:
                status = repair.get('status', 'unknown')
                status_color = 'green' if status == 'success' else 'red' if status == 'failed' else 'yellow'
                print(f"  [{colored(status.upper(), status_color)}] {repair.get('type', 'unknown')}")
                if repair.get('action'):
                    print(f"    {repair.get('action')}")
    
    except Exception as e:
        print(colored(f"Error running repairs: {e}", "red"))


def run_optimize(agent_manager=None):
    """Run optimizations"""
    print(colored("\nOptimization Options:", "yellow"))
    print("1. Optimize Code")
    print("2. Optimize Performance")
    print("3. Optimize Dependencies")
    print("4. Optimize All")
    
    choice = input(colored("\nChoose optimization type [1-4]: ", "cyan"))
    
    opt_types = {
        '1': ['code'],
        '2': ['performance'],
        '3': ['dependencies'],
        '4': ['code', 'performance', 'dependencies']
    }
    
    types = opt_types.get(choice, ['code', 'performance', 'dependencies'])
    
    print(colored(f"\nRunning optimizations: {', '.join(types)}...", "yellow"))
    try:
        if agent_manager is None:
            agent_manager = AgentManager()
        results = agent_manager.run_optimization(types)
        
        print(colored("\nOptimization Complete!", "green"))
        
        improvements = results.get('improvements', [])
        if improvements:
            print(colored("\nImprovements:", "yellow"))
            for improvement in improvements:
                print(f"  {improvement.get('metric')}: {improvement.get('improvement')}")
        else:
            print("No measurable improvements found.")
    
    except Exception as e:
        print(colored(f"Error running optimizations: {e}", "red"))


def view_insights(agent_manager=None):
    """View insights from learned patterns"""
    print(colored("\nGenerating insights...", "yellow"))
    try:
        if agent_manager is None:
            agent_manager = AgentManager()
        insights = agent_manager.get_insights()
        
        print(colored("\nInsights:", "green"))
        
        common_errors = insights.get('common_errors', [])
        if common_errors:
            print(colored("\nMost Common Errors:", "yellow"))
            for error in common_errors[:5]:
                print(f"  {error.get('type')}: {error.get('count')} occurrences")
        
        effective_fixes = insights.get('effective_fixes', [])
        if effective_fixes:
            print(colored("\nMost Effective Fixes:", "yellow"))
            for fix in effective_fixes[:5]:
                print(f"  {fix.get('error_type')}: {fix.get('fix_action')}")
                print(f"    Success rate: {fix.get('success_rate', 0):.1%}")
        
        recommendations = insights.get('recommendations', [])
        if recommendations:
            print(colored("\nRecommendations:", "yellow"))
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"  {i}. {rec}")
    
    except Exception as e:
        print(colored(f"Error generating insights: {e}", "red"))


def view_status(agent_manager=None):
    """View agent status"""
    try:
        if agent_manager is None:
            agent_manager = AgentManager()
        status = agent_manager.get_status()
        
        print(colored("\nAgent Status:", "green"))
        if 'last_run' in status:
            print(f"Last run: {status.get('last_run')}")
        
        results = status.get('results', {})
        if results:
            print(f"Status: {results.get('status', 'unknown')}")
        else:
            print("No previous runs found.")
    
    except Exception as e:
        print(colored(f"Error getting status: {e}", "red"))


def configure_agent():
    """Configure agent settings"""
    print(colored("\nAgent Configuration:", "yellow"))
    print("1. Set Backend (AutoGen, Magentic One, etc.)")
    print("2. Set API Key")
    print("3. View Current Config")
    print("4. Back")
    
    choice = input(colored("\nChoose an option [1-4]: ", "cyan"))
    
    if choice == '1':
        print("\nAvailable backends:")
        print("1. AutoGen (Microsoft)")
        print("2. Magentic One")
        print("3. Docker Cagent")
        print("4. OpenAI Direct")
        
        backend_choice = input(colored("\nChoose backend [1-4]: ", "cyan"))
        # Configuration would be saved here
        print(colored("Configuration saved (implementation pending)", "yellow"))
    
    elif choice == '2':
        api_key = input(colored("Enter API key: ", "cyan"))
        # Save API key securely
        print(colored("API key saved (implementation pending)", "yellow"))
    
    elif choice == '3':
        config_path = Path('agents/config.json')
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(json.dumps(config, indent=2))
        else:
            print("No configuration file found.")
