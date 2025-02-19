import os
import sys
import ssl
import certifi
import requests
import subprocess
import tempfile
from pathlib import Path
import logging
import urllib3
import base64

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_temp_cert_path():
    """Get temporary path for certificate"""
    temp_dir = Path(tempfile.gettempdir())
    return temp_dir / "meraki_cert.cer"

def download_meraki_certificate():
    """Download Meraki's certificate chain"""
    cert_path = get_temp_cert_path()
    try:
        # Disable warnings temporarily
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Get the certificate
        cert = ssl.get_server_certificate(('api.meraki.com', 443))
        
        # Save certificate in both PEM and Base64 format
        cert_path.write_text(cert)
        
        # Convert to Base64 for PowerShell
        cert_base64 = base64.b64encode(cert.encode()).decode()
        
        # Create PowerShell script
        ps_script = f"""
$certContent = [System.Convert]::FromBase64String('{cert_base64}')
$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($certContent)
$store = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root", "LocalMachine")
$store.Open("ReadWrite")
try {{
    $store.Add($cert)
    Write-Output "Certificate added successfully"
}} catch {{
    Write-Error $_
}} finally {{
    $store.Close()
}}
"""
        
        # Save PowerShell script
        ps_script_path = cert_path.with_suffix('.ps1')
        ps_script_path.write_text(ps_script)
        
        logging.info(f"Downloaded Meraki certificate to {cert_path}")
        return ps_script_path
    except Exception as e:
        logging.error(f"Error downloading certificate: {e}")
        return None

def import_certificate(ps_script_path):
    """Import certificate using PowerShell"""
    try:
        # Run PowerShell script with proper execution policy
        cmd = [
            'powershell.exe',
            '-ExecutionPolicy',
            'Bypass',
            '-File',
            str(ps_script_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if "Certificate added successfully" in result.stdout:
            logging.info("Certificate imported successfully")
            return True
        else:
            logging.error(f"Error importing certificate: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Error running PowerShell script: {e}")
        return False

def configure_python_ssl():
    """Configure Python SSL settings"""
    try:
        # Set environment variables
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        os.environ['SSL_CERT_FILE'] = certifi.where()
        
        # Create PowerShell commands to set permanent environment variables
        ps_commands = f"""
[Environment]::SetEnvironmentVariable('REQUESTS_CA_BUNDLE', '{certifi.where().replace("\\", "\\\\")}', 'User')
[Environment]::SetEnvironmentVariable('SSL_CERT_FILE', '{certifi.where().replace("\\", "\\\\")}', 'User')
"""
        
        # Save and execute PowerShell commands
        ps_path = Path(tempfile.gettempdir()) / "set_env_vars.ps1"
        ps_path.write_text(ps_commands)
        
        subprocess.run([
            'powershell.exe',
            '-ExecutionPolicy',
            'Bypass',
            '-File',
            str(ps_path)
        ], check=True)
        
        logging.info("SSL environment variables configured")
        return True
    except Exception as e:
        logging.error(f"Error configuring SSL settings: {e}")
        return False

def verify_connection():
    """Verify connection to Meraki API"""
    try:
        # Create session
        session = requests.Session()
        
        # Try different verification methods
        methods = [
            ("Default verification", None),
            ("Certifi verification", certifi.where()),
            ("System verification", True)
        ]
        
        for name, verify in methods:
            try:
                response = session.get('https://api.meraki.com', verify=verify)
                logging.info(f"{name} successful (Status: {response.status_code})")
                return True
            except requests.exceptions.SSLError as e:
                logging.warning(f"{name} failed: {e}")
                continue
            except Exception as e:
                logging.warning(f"{name} error: {e}")
                continue
        
        return False
    except Exception as e:
        logging.error(f"Connection verification failed: {e}")
        return False

def main():
    logging.info("Starting Meraki Certificate Setup (PowerShell method)...")
    
    # Check if running as administrator
    if os.name == 'nt':
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            logging.error("This script needs to be run as administrator. Please restart with admin privileges.")
            return
    
    # Download and prepare certificate
    ps_script_path = download_meraki_certificate()
    if not ps_script_path:
        return
    
    # Import certificate
    if not import_certificate(ps_script_path):
        return
    
    # Configure Python SSL
    if not configure_python_ssl():
        return
    
    # Verify connection
    if verify_connection():
        logging.info("\nCertificate setup completed successfully!")
        logging.info("\nSetup Information:")
        logging.info(f"1. Certificate store: Certificates (Local Machine) > Trusted Root Certification Authorities")
        logging.info(f"2. Python SSL file: {certifi.where()}")
        logging.info("3. Environment variables have been set")
    else:
        logging.error("\nCertificate setup completed with errors")
        logging.info("\nTroubleshooting steps:")
        logging.info("1. Open 'certmgr.msc' to verify certificate installation")
        logging.info("2. Try restarting your Python environment")
        logging.info("3. Check these environment variables:")
        logging.info(f"   REQUESTS_CA_BUNDLE={os.environ.get('REQUESTS_CA_BUNDLE', 'Not set')}")
        logging.info(f"   SSL_CERT_FILE={os.environ.get('SSL_CERT_FILE', 'Not set')}")
        logging.info("4. Consider restarting your computer")
        logging.info("5. Contact your IT department if issues persist")

if __name__ == "__main__":
    main()