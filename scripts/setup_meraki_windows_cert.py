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
import winreg
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_temp_cert_path():
    """Get temporary path for certificate"""
    temp_dir = Path(tempfile.gettempdir())
    return temp_dir / "meraki_cert.cer"

def download_meraki_certificate():
    """Download Meraki's certificate"""
    cert_path = get_temp_cert_path()
    try:
        # Disable warnings temporarily
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Get the certificate
        cert = ssl.get_server_certificate(('api.meraki.com', 443))
        
        # Save certificate
        cert_path.write_text(cert)
        logging.info(f"Downloaded Meraki certificate to {cert_path}")
        return cert_path
    except Exception as e:
        logging.error(f"Error downloading certificate: {e}")
        return None

def import_to_windows_store(cert_path):
    """Import certificate to Windows certificate store"""
    try:
        # Import to Root CA store
        cmd = [
            'certutil', 
            '-addstore', 
            'ROOT', 
            str(cert_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if "CertUtil: -addstore command completed successfully." in result.stdout:
            logging.info("Certificate imported to Windows ROOT store successfully")
            return True
        else:
            logging.error(f"Error importing certificate: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Error running certutil: {e}")
        return False

def configure_requests_cert():
    """Configure requests to use Windows certificate store"""
    try:
        # Use certifi's default certificates
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        os.environ['SSL_CERT_FILE'] = certifi.where()
        
        # Set for user
        subprocess.run(['setx', 'REQUESTS_CA_BUNDLE', certifi.where()], check=True)
        subprocess.run(['setx', 'SSL_CERT_FILE', certifi.where()], check=True)
        
        logging.info("Configured requests to use system certificates")
        return True
    except Exception as e:
        logging.error(f"Error configuring requests: {e}")
        return False

def verify_connection():
    """Verify connection to Meraki API"""
    try:
        # Create session with custom settings
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

def backup_existing_cert():
    """Backup existing Meraki certificate if present"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path.home() / 'certificate_backups'
        backup_dir.mkdir(exist_ok=True)
        
        # Check for existing cert and backup
        cert_path = get_temp_cert_path()
        if cert_path.exists():
            backup_path = backup_dir / f"meraki_cert_backup_{timestamp}.cer"
            cert_path.rename(backup_path)
            logging.info(f"Backed up existing certificate to {backup_path}")
        
        return True
    except Exception as e:
        logging.error(f"Error backing up certificate: {e}")
        return False

def main():
    logging.info("Starting Meraki Windows Certificate Setup...")
    
    # Check if running as administrator
    if os.name == 'nt':
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            logging.error("This script needs to be run as administrator. Please restart with admin privileges.")
            return
    
    # Backup existing certificate
    backup_existing_cert()
    
    # Download certificate
    cert_path = download_meraki_certificate()
    if not cert_path:
        return
    
    # Import to Windows store
    if not import_to_windows_store(cert_path):
        return
    
    # Configure requests
    if not configure_requests_cert():
        return
    
    # Verify connection
    if verify_connection():
        logging.info("\nCertificate setup completed successfully!")
        logging.info("\nSetup Information:")
        logging.info(f"1. Certificate location: {cert_path}")
        logging.info(f"2. System certificate store: Certificates (Local Computer) > Trusted Root Certification Authorities")
        logging.info(f"3. Environment variables set for requests library")
    else:
        logging.error("\nCertificate setup completed with errors")
        logging.info("\nTroubleshooting steps:")
        logging.info("1. Open 'certmgr.msc' and check Trusted Root Certification Authorities > Certificates")
        logging.info("2. Verify the Meraki certificate is present and valid")
        logging.info("3. Try these PowerShell commands:")
        logging.info("   $env:REQUESTS_CA_BUNDLE = 'C:\\Python312\\Lib\\site-packages\\certifi\\cacert.pem'")
        logging.info("   $env:SSL_CERT_FILE = 'C:\\Python312\\Lib\\site-packages\\certifi\\cacert.pem'")
        logging.info("4. Restart your computer to ensure all certificate changes take effect")
        logging.info("5. Check if your organization's security policies allow certificate imports")

if __name__ == "__main__":
    main()