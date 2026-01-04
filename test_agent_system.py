"""
Quick test script for the agent system
"""

from agents.agent_manager import AgentManager
from agents.agent_framework import AgentBackend

def test_agent_system():
    """Test the agent system"""
    print("Testing Agent System...")
    print("=" * 60)
    
    # Test AgentManager creation
    print("\n1. Creating AgentManager...")
    try:
        manager = AgentManager(AgentBackend.OPENAI)
        print("   [OK] AgentManager created successfully")
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return
    
    # Test status
    print("\n2. Checking agent status...")
    try:
        status = manager.get_status()
        print(f"   [OK] Status: {status.get('status', 'ready')}")
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
    
    # Test log analyzer
    print("\n3. Testing log analyzer...")
    try:
        from agents.log_analyzer import LogAnalyzer
        analyzer = LogAnalyzer()
        print("   [OK] LogAnalyzer created successfully")
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
    
    # Test code analyzer
    print("\n4. Testing code analyzer...")
    try:
        from agents.code_analyzer import CodeAnalyzer
        analyzer = CodeAnalyzer()
        print("   [OK] CodeAnalyzer created successfully")
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
    
    print("\n" + "=" * 60)
    print("Agent system test complete!")
    print("\nTo use the agent system:")
    print("  1. Run: python main.py")
    print("  2. Select option 11: Self-Healing Agent System")
    print("  3. Choose from the agent menu options")

if __name__ == '__main__':
    test_agent_system()
