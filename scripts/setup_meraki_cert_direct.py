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
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_cert_paths():
    """Get certificate paths"""
    temp_dir = Path(tempfile.gettempdir())
    return {
        'pem': temp_dir / "meraki.pem",
        'der': temp_dir / "meraki.cer",
        'ps1': temp_dir / "import_cert.ps1"
    }

def download_certificate_chain():
    """Download complete certificate chain from Meraki"""
    try:
        # Disable SSL warnings temporarily
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Get server certificate
        cert_pem = ssl.get_server_certificate(('api.meraki.com', 443))
        
        # Parse the certificate
        cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())
        
        # Get paths
        paths = get_cert_paths()
        
        # Save PEM format
        paths['pem'].write_text(cert_pem)
        
        # Save DER format
        der_data = cert.public_bytes(serialization.Encoding.DER)
        paths['der'].write_bytes(der_data)
        
        # Create PowerShell script
        ps_script = f"""
# Import certificate to Root store
$certPath = "{paths['der'].as_posix()}"
$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($certPath)
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
        paths['ps1'].write_text(ps_script)
        
        logging.info(f"Certificate files prepared:\nPEM: {paths['pem']}\nDER: {paths['der']}")
        return paths
    except Exception as e:
        logging.error(f"Error preparing certificates: {e}")
        return None

def import_certificate(ps_path):
    """Import certificate using PowerShell"""
    try:
        cmd = [
            'powershell.exe',
            '-ExecutionPolicy',
            'Bypass',
            '-File',
            str(ps_path)
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

def configure_ssl_environment():
    """Configure SSL environment for Python"""
    try:
        # Set environment variables
        cert_paths = get_cert_paths()
        pem_path = str(cert_paths['pem'])
        
        # Set for current process
        os.environ['REQUESTS_CA_BUNDLE'] = pem_path
        os.environ['SSL_CERT_FILE'] = pem_path
        
        # Set for user using PowerShell
        ps_commands = f"""
[Environment]::SetEnvironmentVariable('REQUESTS_CA_BUNDLE', '{pem_path.replace("\\", "\\\\")}', 'User')
[Environment]::SetEnvironmentVariable('SSL_CERT_FILE', '{pem_path.replace("\\", "\\\\")}', 'User')
"""
        ps_path = Path(tempfile.gettempdir()) / "set_env.ps1"
        ps_path.write_text(ps_commands)
        
        subprocess.run([
            'powershell.exe',
            '-ExecutionPolicy',
            'Bypass',
            '-File',
            str(ps_path)
        ], check=True)
        
        logging.info("SSL environment configured")
        return True
    except Exception as e:
        logging.error(f"Error configuring SSL environment: {e}")
        return False

def verify_setup():
    """Verify the certificate setup"""
    try:
        # Create session with custom settings
        session = requests.Session()
        cert_paths = get_cert_paths()
        
        # Try different verification methods
        methods = [
            ("System certificates", True),
            ("PEM file", str(cert_paths['pem'])),
            ("Certifi bundle", certifi.where())
        ]
        
        for name, verify in methods:
            try:
                response = session.get('https://api.meraki.com', verify=verify)
                logging.info(f"{name} verification successful (Status: {response.status_code})")
                return True
            except requests.exceptions.SSLError as e:
                logging.warning(f"{name} verification failed: {e}")
            except Exception as e:
                logging.warning(f"{name} error: {e}")
        
        return False
    except Exception as e:
        logging.error(f"Verification failed: {e}")
        return False

def main():
    logging.info("Starting Meraki Certificate Setup...")
    
    # Check if running as administrator
    if os.name == 'nt':
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            logging.error("This script needs to be run as administrator. Please restart with admin privileges.")
            return
    
    # Install required package
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography"])
    except Exception as e:
        logging.error(f"Error installing cryptography package: {e}")
        return
    
    # Download and prepare certificates
    cert_paths = download_certificate_chain()
    if not cert_paths:
        return
    
    # Import certificate
    if not import_certificate(cert_paths['ps1']):
        return
    
    # Configure SSL environment
    if not configure_ssl_environment():
        return
    
    # Verify setup
    if verify_setup():
        logging.info("\nCertificate setup completed successfully!")
        logging.info("\nSetup Information:")
        logging.info(f"1. Certificate files location: {Path(tempfile.gettempdir())}")
        logging.info(f"2. Environment variables set for SSL verification")
        logging.info("3. Certificate imported to Windows Root store")
    else:
        logging.error("\nCertificate setup completed with errors")
        logging.info("\nTroubleshooting steps:")
        logging.info("1. Open 'certmgr.msc' and check Trusted Root Certification Authorities")
        logging.info("2. Verify certificate files exist in the temp directory")
        logging.info("3. Try these commands in PowerShell:")
        logging.info(f"   $env:REQUESTS_CA_BUNDLE = '{cert_paths['pem']}'")
        logging.info(f"   $env:SSL_CERT_FILE = '{cert_paths['pem']}'")
        logging.info("4. Restart your computer to apply all changes")
        logging.info("5. Contact IT if issues persist")

if __name__ == "__main__":
    main()