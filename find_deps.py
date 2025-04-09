import os
import sys
import importlib
import subprocess
import pkg_resources

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
    # Common standard library modules that might not be detected correctly
    known_stdlib_modules = {
        'argparse', 'base64', 'collections', 'csv', 'ctypes', 'datetime',
        'getpass', 'json', 'logging', 'os', 'pathlib', 'platform', 'random',
        're', 'secrets', 'shutil', 'socket', 'sqlite3', 'ssl', 'string',
        'subprocess', 'sys', 'tempfile', 'threading', 'traceback', 'uuid',
        'webbrowser', 'time', 'calendar', 'zlib', 'hashlib', 'ipaddress'
    }
    
    if module_name in known_stdlib_modules:
        return True
    
    if module_name in sys.builtin_module_names:
        return True
    
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return False
        
        # Check if the module is in standard library paths
        stdlib_paths = [os.path.dirname(os.__file__)]
        return spec.origin and any(spec.origin.startswith(p) for p in stdlib_paths)
    except (ImportError, AttributeError, ValueError):
        return False
def get_installed_version(module_name):
    """Get the installed version of a module."""
    try:
        # Try using pkg_resources first
        try:
            return pkg_resources.get_distribution(module_name).version
        except (pkg_resources.DistributionNotFound, ModuleNotFoundError):
            pass
        
        # Try using pip list as a fallback
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', module_name],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
        except subprocess.CalledProcessError:
            pass
        
        # Try importing the module and checking its version
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, '__version__'):
                return module.__version__
            if hasattr(module, 'version'):
                return module.version
        except (ImportError, AttributeError):
            pass
        
        return None
    except Exception as e:
        print(f"Error getting version for {module_name}: {e}")
        return None

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
    
    # Map module names to package names if different
    package_mapping = {
        'PIL': 'Pillow',
        'yaml': 'PyYAML',
        'bs4': 'beautifulsoup4',
        'sklearn': 'scikit-learn',
        'cv2': 'opencv-python',
        # Add more mappings as needed
    }
    
    # Get versions and write to requirements.txt
    with open('requirements.txt', 'w') as f:
        for module in sorted(third_party_modules):
            package_name = package_mapping.get(module, module)
            version = get_installed_version(package_name)
            
            if version:
                req_line = f"{package_name}=={version}"
                print(f"- {req_line}")
                f.write(f"{req_line}\n")
            else:
                req_line = package_name
                print(f"- {req_line} (version unknown)")
                f.write(f"{req_line}\n")
    
    # Add common Meraki CLI dependencies if not already detected
    meraki_deps = [
        'meraki',
        'tabulate',
        'pathlib',
        'termcolor',
        'pysqlcipher3',
        'rich',
        'setuptools',
        'dnspython',
        'ipinfo',
        'scapy',
        'numpy',
        'ipaddress',
        'PyYAML',
        'click',
        'requests',
        'cryptography'
    ]
    
    # Check if any common dependencies are missing
    with open('requirements.txt', 'r') as f:
        existing_packages = [line.split('==')[0].strip() for line in f.readlines()]
    
    missing_packages = []
    for dep in meraki_deps:
        if dep not in existing_packages and dep.lower() not in [p.lower() for p in existing_packages]:
            missing_packages.append(dep)
    
    # Append missing common dependencies
    if missing_packages:
        print("\nAdding common Meraki CLI dependencies:")
        with open('requirements.txt', 'a') as f:
            for package in missing_packages:
                version = get_installed_version(package)
                if version:
                    req_line = f"{package}=={version}"
                    print(f"- {req_line}")
                    f.write(f"{req_line}\n")
                else:
                    req_line = package
                    print(f"- {req_line} (version unknown)")
                    f.write(f"{req_line}\n")
    
    print(f"\nGenerated requirements.txt with all detected packages and common dependencies")

if __name__ == "__main__":
    # Use current directory
    project_dir = "."
    generate_requirements(project_dir)