import os
import sys
import pkg_resources
import importlib

def find_imported_modules(directory):
    """Find all imported modules in Python files in a directory."""
    imported_modules = set()
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    try:
                        content = f.read()
                        lines = content.split('\n')
                        for line in lines:
                            line = line.strip()
                            # Look for import statements
                            if line.startswith('import ') or ' import ' in line:
                                # Handle multiple imports on one line
                                if ',' in line:
                                    parts = line.replace('import ', '').replace('from ', '').split(',')
                                    for part in parts:
                                        module = part.strip().split(' ')[0]
                                        imported_modules.add(module.split('.')[0])
                                else:
                                    if line.startswith('import '):
                                        module = line[7:].strip().split(' ')[0]
                                        imported_modules.add(module.split('.')[0])
                                    elif ' import ' in line:
                                        module = line.split('from ')[1].split(' import')[0].strip()
                                        imported_modules.add(module.split('.')[0])
                    except Exception as e:
                        print(f"Error processing {file}: {e}")
    
    return imported_modules

def filter_standard_modules(modules):
    """Filter out standard library modules."""
    non_standard_modules = set()
    for module in modules:
        try:
            # If it's in the standard library, skip it
            if module in sys.builtin_module_names:
                continue
            
            # Try to get the module's location
            spec = importlib.util.find_spec(module)
            if spec is None:
                # Module not found, probably a third-party module
                non_standard_modules.add(module)
            elif 'site-packages' in spec.origin:
                # Module is in site-packages, so it's a third-party module
                non_standard_modules.add(module)
        except (ImportError, AttributeError):
            # If we can't import it, it's probably a third-party module
            non_standard_modules.add(module)
    
    return non_standard_modules

def get_installed_packages():
    """Get all installed packages and their versions."""
    return {pkg.key: pkg.version for pkg in pkg_resources.working_set}

def generate_requirements(directory):
    """Generate requirements.txt based on imports in directory."""
    modules = find_imported_modules(directory)
    non_standard_modules = filter_standard_modules(modules)
    installed_packages = get_installed_packages()
    
    requirements = []
    for module in non_standard_modules:
        if module in installed_packages:
            requirements.append(f"{module}=={installed_packages[module]}")
        else:
            requirements.append(module)
    
    with open('requirements.txt', 'w') as f:
        f.write('\n'.join(sorted(requirements)))
    
    print(f"Generated requirements.txt with {len(requirements)} packages")

if __name__ == "__main__":
    # Replace with your project directory
    project_dir = "."
    generate_requirements(project_dir)