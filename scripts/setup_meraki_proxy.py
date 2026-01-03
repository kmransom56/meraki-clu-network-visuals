import os
import sys
import requests
import logging
import urllib3
from pathlib import Path
import tempfile
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_proxy_settings():
    """Get proxy settings from Windows registry"""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r'Software\Microsoft\Windows\CurrentVersion\Internet Settings') as key:
            proxy_enable = winreg.QueryValueEx(key, 'ProxyEnable')[0]
            if proxy_enable:
                proxy_server = winreg.QueryValueEx(key, 'ProxyServer')[0]
                return {
                    'http': f'http://{proxy_server}',
                    'https': f'http://{proxy_server}'
                }
    except Exception as e:
        logging.warning(f"Could not read proxy settings: {e}")
    return None

def configure_requests():
    """Configure requests to work with proxy"""
    try:
        # Disable SSL verification warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Get proxy settings
        proxies = get_proxy_settings()
        if proxies:
            logging.info(f"Found proxy settings: {proxies}")
        else:
            logging.info("No proxy settings found")
        
        return proxies
    except Exception as e:
        logging.error(f"Error configuring requests: {e}")
        return None

def test_connection(proxies=None):
    """Test connection to Meraki API"""
    try:
        # Create session
        session = requests.Session()
        if proxies:
            session.proxies = proxies
        
        # Try connection with verify=False
        response = session.get('https://api.meraki.com', verify=False)
        logging.info(f"Connection successful (Status: {response.status_code})")
        return True
    except Exception as e:
        logging.error(f"Connection test failed: {e}")
        return False

def set_environment_variables():
    """Set environment variables for requests"""
    try:
        # Create PowerShell script to set environment variables
        ps_script = """
# Disable SSL verification for requests
[Environment]::SetEnvironmentVariable('PYTHONHTTPSVERIFY', '0', 'User')
[Environment]::SetEnvironmentVariable('REQUESTS_CA_BUNDLE', '', 'User')
[Environment]::SetEnvironmentVariable('SSL_CERT_FILE', '', 'User')

# Set current session variables
$env:PYTHONHTTPSVERIFY = '0'
$env:REQUESTS_CA_BUNDLE = ''
$env:SSL_CERT_FILE = ''

Write-Output "Environment variables set successfully"
"""
        
        # Save and execute PowerShell script
        ps_path = Path(tempfile.gettempdir()) / "set_env.ps1"
        ps_path.write_text(ps_script)
        
        result = subprocess.run([
            'powershell.exe',
            '-ExecutionPolicy',
            'Bypass',
            '-File',
            str(ps_path)
        ], capture_output=True, text=True)
        
        if "Environment variables set successfully" in result.stdout:
            logging.info("Environment variables configured successfully")
            return True
        else:
            logging.error(f"Error setting environment variables: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Error setting environment variables: {e}")
        return False

def create_meraki_wrapper():
    """Create a wrapper script for Meraki API calls"""
    try:
        wrapper_content = """
import os
import requests
import urllib3

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_proxy_settings():
    '''Get proxy settings from environment or Windows registry'''
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r'Software\Microsoft\Windows\CurrentVersion\Internet Settings') as key:
            proxy_enable = winreg.QueryValueEx(key, 'ProxyEnable')[0]
            if proxy_enable:
                proxy_server = winreg.QueryValueEx(key, 'ProxyServer')[0]
                return {
                    'http': f'http://{proxy_server}',
                    'https': f'http://{proxy_server}'
                }
    except:
        pass
    return None

class MerakiAPI:
    def __init__(self, api_key):
        self.session = requests.Session()
        self.session.verify = False
        self.proxies = get_proxy_settings()
        if self.proxies:
            self.session.proxies = self.proxies
        self.base_url = 'https://api.meraki.com/api/v1'
        self.headers = {
            'X-Cisco-Meraki-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def get(self, endpoint):
        '''Make GET request to Meraki API'''
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint, data):
        '''Make POST request to Meraki API'''
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
"""
        
        # Save wrapper script
        wrapper_path = Path(__file__).parent.parent / "modules" / "meraki" / "meraki_proxy.py"
        wrapper_path.write_text(wrapper_content)
        
        logging.info(f"Created Meraki API wrapper at {wrapper_path}")
        return True
    except Exception as e:
        logging.error(f"Error creating wrapper script: {e}")
        return False

def main():
    logging.info("Starting Meraki Proxy Configuration...")
    
    # Configure requests
    proxies = configure_requests()
    
    # Set environment variables
    if not set_environment_variables():
        return
    
    # Create Meraki wrapper
    if not create_meraki_wrapper():
        return
    
    # Test connection
    if test_connection(proxies):
        logging.info("\nProxy configuration completed successfully!")
        logging.info("\nConfiguration Information:")
        if proxies:
            logging.info(f"1. Proxy settings: {proxies}")
        else:
            logging.info("1. No proxy settings found (direct connection)")
        logging.info("2. SSL verification disabled for Meraki API")
        logging.info("3. Meraki API wrapper created with proxy support")
        logging.info("\nNext steps:")
        logging.info("1. Update your code to use the new meraki_proxy.py module")
        logging.info("2. Import MerakiAPI from meraki_proxy instead of the regular module")
        logging.info("3. Example usage:")
        logging.info("""
    from modules.meraki.meraki_proxy import MerakiAPI
    
    api = MerakiAPI(api_key)
    organizations = api.get('/organizations')
    """)
    else:
        logging.error("\nProxy configuration completed with errors")
        logging.info("\nTroubleshooting steps:")
        logging.info("1. Check your network connectivity")
        logging.info("2. Verify proxy settings in Windows")
        logging.info("3. Contact IT about:")
        logging.info("   - Proxy authentication requirements")
        logging.info("   - Firewall rules for api.meraki.com")
        logging.info("   - Zscaler configuration")




logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_proxy_settings():
    """Get proxy settings from Windows registry"""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r'Software\Microsoft\Windows\CurrentVersion\Internet Settings') as key:
            proxy_enable = winreg.QueryValueEx(key, 'ProxyEnable')[0]
            if proxy_enable:
                proxy_server = winreg.QueryValueEx(key, 'ProxyServer')[0]
                return {
                    'http': f'http://{proxy_server}',
                    'https': f'http://{proxy_server}'
                }
    except Exception as e:
        logging.warning(f"Could not read proxy settings: {e}")
    return None

def configure_requests():
    """Configure requests to work with proxy"""
    try:
        # Disable SSL verification warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Get proxy settings
        proxies = get_proxy_settings()
        if proxies:
            logging.info(f"Found proxy settings: {proxies}")
        else:
            logging.info("No proxy settings found")
        
        return proxies
    except Exception as e:
        logging.error(f"Error configuring requests: {e}")
        return None

def test_connection(proxies=None):
    """Test connection to Meraki API"""
    try:
        # Create session
        session = requests.Session()
        if proxies:
            session.proxies = proxies
        
        # Try connection with verify=False
        response = session.get('https://api.meraki.com', verify=False)
        logging.info(f"Connection successful (Status: {response.status_code})")
        return True
    except Exception as e:
        logging.error(f"Connection test failed: {e}")
        return False

def set_environment_variables():
    """Set environment variables for requests"""
    try:
        # Create PowerShell script to set environment variables
        ps_script = """
# Disable SSL verification for requests
[Environment]::SetEnvironmentVariable('PYTHONHTTPSVERIFY', '0', 'User')
[Environment]::SetEnvironmentVariable('REQUESTS_CA_BUNDLE', '', 'User')
[Environment]::SetEnvironmentVariable('SSL_CERT_FILE', '', 'User')

# Set current session variables
$env:PYTHONHTTPSVERIFY = '0'
$env:REQUESTS_CA_BUNDLE = ''
$env:SSL_CERT_FILE = ''

Write-Output "Environment variables set successfully"
"""
        
        # Save and execute PowerShell script
        ps_path = Path(tempfile.gettempdir()) / "set_env.ps1"
        ps_path.write_text(ps_script)
        
        result = subprocess.run([
            'powershell.exe',
            '-ExecutionPolicy',
            'Bypass',
            '-File',
            str(ps_path)
        ], capture_output=True, text=True)
        
        if "Environment variables set successfully" in result.stdout:
            logging.info("Environment variables configured successfully")
            return True
        else:
            logging.error(f"Error setting environment variables: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Error setting environment variables: {e}")
        return False

def create_meraki_wrapper():
    """Create a wrapper script for Meraki API calls"""
    try:
        wrapper_content = """
import os
import requests
import urllib3

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_proxy_settings():
    '''Get proxy settings from environment or Windows registry'''
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r'Software\Microsoft\Windows\CurrentVersion\Internet Settings') as key:
            proxy_enable = winreg.QueryValueEx(key, 'ProxyEnable')[0]
            if proxy_enable:
                proxy_server = winreg.QueryValueEx(key, 'ProxyServer')[0]
                return {
                    'http': f'http://{proxy_server}',
                    'https': f'http://{proxy_server}'
                }
    except:
        pass
    return None

class MerakiAPI:
    def __init__(self, api_key):
        self.session = requests.Session()
        self.session.verify = False
        self.proxies = get_proxy_settings()
        if self.proxies:
            self.session.proxies = self.proxies
        self.base_url = 'https://api.meraki.com/api/v1'
        self.headers = {
            'X-Cisco-Meraki-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def get(self, endpoint):
        '''Make GET request to Meraki API'''
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint, data):
        '''Make POST request to Meraki API'''
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
"""
        
        # Save wrapper script
        wrapper_path = Path(__file__).parent.parent / "modules" / "meraki" / "meraki_proxy.py"
        wrapper_path.write_text(wrapper_content)
        
        logging.info(f"Created Meraki API wrapper at {wrapper_path}")
        return True
    except Exception as e:
        logging.error(f"Error creating wrapper script: {e}")
        return False

def main():
    logging.info("Starting Meraki Proxy Configuration...")
    
    # Configure requests
    proxies = configure_requests()
    
    # Set environment variables
    if not set_environment_variables():
        return
    
    # Create Meraki wrapper
    if not create_meraki_wrapper():
        return
    
    # Test connection
    if test_connection(proxies):
        logging.info("\nProxy configuration completed successfully!")
        logging.info("\nConfiguration Information:")
        if proxies:
            logging.info(f"1. Proxy settings: {proxies}")
        else:
            logging.info("1. No proxy settings found (direct connection)")
        logging.info("2. SSL verification disabled for Meraki API")
        logging.info("3. Meraki API wrapper created with proxy support")
        logging.info("\nNext steps:")
        logging.info("1. Update your code to use the new meraki_proxy.py module")
        logging.info("2. Import MerakiAPI from meraki_proxy instead of the regular module")
        logging.info("3. Example usage:")
        logging.info("""
    from modules.meraki.meraki_proxy import MerakiAPI
    
    api = MerakiAPI(api_key)
    organizations = api.get('/organizations')
    """)
    else:
        logging.error("\nProxy configuration completed with errors")
        logging.info("\nTroubleshooting steps:")
        logging.info("1. Check your network connectivity")
        logging.info("2. Verify proxy settings in Windows")
        logging.info("3. Contact IT about:")
        logging.info("   - Proxy authentication requirements")
        logging.info("   - Firewall rules for api.meraki.com")
        logging.info("   - Zscaler configuration")



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_proxy_settings():
    """Get proxy settings from Windows registry"""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r'Software\Microsoft\Windows\CurrentVersion\Internet Settings') as key:
            proxy_enable = winreg.QueryValueEx(key, 'ProxyEnable')[0]
            if proxy_enable:
                proxy_server = winreg.QueryValueEx(key, 'ProxyServer')[0]
                return {
                    'http': f'http://{proxy_server}',
                    'https': f'http://{proxy_server}'
                }
    except Exception as e:
        logging.warning(f"Could not read proxy settings: {e}")
    return None

def configure_requests():
    """Configure requests to work with proxy"""
    try:
        # Disable SSL verification warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Get proxy settings
        proxies = get_proxy_settings()
        if proxies:
            logging.info(f"Found proxy settings: {proxies}")
        else:
            logging.info("No proxy settings found")
        
        return proxies
    except Exception as e:
        logging.error(f"Error configuring requests: {e}")
        return None

def test_connection(proxies=None):
    """Test connection to Meraki API"""
    try:
        # Create session
        session = requests.Session()
        if proxies:
            session.proxies = proxies
        
        # Try connection with verify=False
        response = session.get('https://api.meraki.com', verify=False)
        logging.info(f"Connection successful (Status: {response.status_code})")
        return True
    except Exception as e:
        logging.error(f"Connection test failed: {e}")
        return False

def set_environment_variables():
    """Set environment variables for requests"""
    try:
        # Create PowerShell script to set environment variables
        ps_script = """
# Disable SSL verification for requests
[Environment]::SetEnvironmentVariable('PYTHONHTTPSVERIFY', '0', 'User')
[Environment]::SetEnvironmentVariable('REQUESTS_CA_BUNDLE', '', 'User')
[Environment]::SetEnvironmentVariable('SSL_CERT_FILE', '', 'User')

# Set current session variables
$env:PYTHONHTTPSVERIFY = '0'
$env:REQUESTS_CA_BUNDLE = ''
$env:SSL_CERT_FILE = ''

Write-Output "Environment variables set successfully"
"""
        
        # Save and execute PowerShell script
        ps_path = Path(tempfile.gettempdir()) / "set_env.ps1"
        ps_path.write_text(ps_script)
        
        result = subprocess.run([
            'powershell.exe',
            '-ExecutionPolicy',
            'Bypass',
            '-File',
            str(ps_path)
        ], capture_output=True, text=True)
        
        if "Environment variables set successfully" in result.stdout:
            logging.info("Environment variables configured successfully")
            return True
        else:
            logging.error(f"Error setting environment variables: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Error setting environment variables: {e}")
        return False

def create_meraki_wrapper():
    """Create a wrapper script for Meraki API calls"""
    try:
        wrapper_content = """
import os
import requests
import urllib3

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_proxy_settings():
    '''Get proxy settings from environment or Windows registry'''
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r'Software\Microsoft\Windows\CurrentVersion\Internet Settings') as key:
            proxy_enable = winreg.QueryValueEx(key, 'ProxyEnable')[0]
            if proxy_enable:
                proxy_server = winreg.QueryValueEx(key, 'ProxyServer')[0]
                return {
                    'http': f'http://{proxy_server}',
                    'https': f'http://{proxy_server}'
                }
    except:
        pass
    return None

class MerakiAPI:
    def __init__(self, api_key):
        self.session = requests.Session()
        self.session.verify = False
        self.proxies = get_proxy_settings()
        if self.proxies:
            self.session.proxies = self.proxies
        self.base_url = 'https://api.meraki.com/api/v1'
        self.headers = {
            'X-Cisco-Meraki-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def get(self, endpoint):
        '''Make GET request to Meraki API'''
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint, data):
        '''Make POST request to Meraki API'''
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
"""
        
        # Save wrapper script
        wrapper_path = Path(__file__).parent.parent / "modules" / "meraki" / "meraki_proxy.py"
        wrapper_path.write_text(wrapper_content)
        
        logging.info(f"Created Meraki API wrapper at {wrapper_path}")
        return True
    except Exception as e:
        logging.error(f"Error creating wrapper script: {e}")
        return False

def main():
    logging.info("Starting Meraki Proxy Configuration...")
    
    # Configure requests
    proxies = configure_requests()
    
    # Set environment variables
    if not set_environment_variables():
        return
    
    # Create Meraki wrapper
    if not create_meraki_wrapper():
        return
    
    # Test connection
    if test_connection(proxies):
        logging.info("\nProxy configuration completed successfully!")
        logging.info("\nConfiguration Information:")
        if proxies:
            logging.info(f"1. Proxy settings: {proxies}")
        else:
            logging.info("1. No proxy settings found (direct connection)")
        logging.info("2. SSL verification disabled for Meraki API")
        logging.info("3. Meraki API wrapper created with proxy support")
        logging.info("\nNext steps:")
        logging.info("1. Update your code to use the new meraki_proxy.py module")
        logging.info("2. Import MerakiAPI from meraki_proxy instead of the regular module")
        logging.info("3. Example usage:")
        logging.info("""
    from modules.meraki.meraki_proxy import MerakiAPI
    
    api = MerakiAPI(api_key)
    organizations = api.get('/organizations')
    """)
    else:
        logging.error("\nProxy configuration completed with errors")
        logging.info("\nTroubleshooting steps:")
        logging.info("1. Check your network connectivity")
        logging.info("2. Verify proxy settings in Windows")
        logging.info("3. Contact IT about:")
        logging.info("   - Proxy authentication requirements")
        logging.info("   - Firewall rules for api.meraki.com")
        logging.info("   - Zscaler configuration")

if __name__ == "__main__":
    main()