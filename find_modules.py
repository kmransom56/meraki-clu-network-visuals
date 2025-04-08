import os
import sys
import importlib

def find_imported_modules(directory):
    """Find all imported modules in Python files in a directory."""
    imported_modules = set()
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        for line in lines:
                            line = line.strip()
                            # Skip comments
                            if line.startswith('#'):
                                continue
                            # Look for import statements
                            if line.startswith('import ') or line.startswith('from '):
                                # Handle from X import Y
                                if line.startswith('from '):
                                    module = line.split('from ')[1].split(' import')[0].strip()
                                    imported_modules.add(module.split('.')[0])
                                # Handle import X
                                elif line.startswith('import '):
                                    # Handle multiple imports on one line (import x, y, z)
                                    modules = line[7:].split(',')
                                    for module in modules:
                                        mod = module.strip().split(' as ')[0].strip()
                                        imported_modules.add(mod.split('.')[0])
                except Exception as e:
                    print(f"Error processing {os.path.join(root, file)}: {e}")
    
    return imported_modules

def is_standard_library(module_name):
    """Check if a module is part of the Python standard library."""
    if module_name in sys.builtin_module_names:
        return True
    
    try:
        # Try to find the module spec
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return False
        
        # If the module is in the standard library, its location will not contain 'site-packages'
        return 'site-packages' not in spec.origin
    except (ImportError, AttributeError, ValueError):
        return False

def generate_requirements(directory):
    """Generate requirements.txt based on imports."""
    modules = find_imported_modules(directory)
    print(f"Found {len(modules)} imported modules")
    
    # Filter out standard library modules
    third_party_modules = []
    for module in modules:
        if not is_standard_library(module):
            third_party_modules.append(module)
    
    print(f"Found {len(third_party_modules)} third-party modules:")
    for module in sorted(third_party_modules):
        print(f"- {module}")
    
    # Write to requirements.txt
    with open('requirements.txt', 'w') as f:
        for module in sorted(third_party_modules):
            f.write(f"{module}\n")
    
    print(f"\nGenerated requirements.txt with {len(third_party_modules)} packages")

if __name__ == "__main__":
    # Use current directory
    project_dir = "."
    generate_requirements(project_dir),