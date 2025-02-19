
import os
import sys
import ssl
import certifi
import shutil
import requests
import subprocess
from pathlib import Path
import logging
import urllib3
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_ssl_directories():
    """Create necessary SSL directories"""
    ssl_base = Path(r"C:\Program Files\Common Files\SSL")
    ssl_certs = ssl_base / "certs"
    
    try:
        # Create directories with proper permissions
        ssl_base.mkdir(parents=True, exist_ok=True)
        ssl_certs.mkdir(parents=True, exist_ok=True)
        
        logging.info(f"Created SSL directories:\n{ssl_base}\n{ssl_certs}")
        return ssl_base, ssl_certs
    except PermissionError:
        logging.error("Permission denied. Please run this script as administrator.")
        return None, None
    except Exception as e:
        logging.error(f"Error creating SSL directories: {e}")
        return None, None

def install_certificates(ssl_base):
    """Install and update certificates"""
    try:
        # Install certifi if not already installed
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "certifi"])
        logging.info("Certifi package installed/updated successfully")
        
        # Get certifi's certificate path
        certifi_path = Path(certifi.where())
        system_cert_path = ssl_base / "cert.pem"
        logging.info(f"Certifi certificates location: {certifi_path}")
        
        # Copy certifi's certificates to system location
        shutil.copy2(certifi_path, system_cert_path)
        logging.info(f"Copied certificates from {certifi_path} to {system_cert_path}")
        
        return certifi_path
    except Exception as e:
        logging.error(f"Error installing certificates: {e}")
        return None

def download_meraki_certificate(ssl_certs):
    """Download Meraki's certificate"""
    try:
        # Temporarily disable warnings for this specific request
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        response = requests.get("https://api.meraki.com", verify=False)
        cert = ssl.get_server_certificate(('api.meraki.com', 443))
        
        cert_path = ssl_certs / "meraki.pem"
        cert_path.write_text(cert)
        
        logging.info(f"Downloaded Meraki certificate to {cert_path}")
        return True
    except Exception as e:
        logging.error(f"Error downloading Meraki certificate: {e}")
        return False

def set_environment_variables(ssl_base):
    """Set SSL environment variables"""
    try:
        cert_path = str(ssl_base / "cert.pem")
        
        # Set for current process
        os.environ['SSL_CERT_FILE'] = cert_path
        os.environ['REQUESTS_CA_BUNDLE'] = cert_path
        
        # Set system environment variables using setx
        subprocess.run(['setx', 'SSL_CERT_FILE', cert_path, '/M'], check=True)
        subprocess.run(['setx', 'REQUESTS_CA_BUNDLE', cert_path, '/M'], check=True)
        
        logging.info(f"Set environment variables:\nSSL_CERT_FILE={cert_path}\nREQUESTS_CA_BUNDLE={cert_path}")
        return True
    except Exception as e:
        logging.error(f"Error setting environment variables: {e}")
        logging.info("Please set the following environment variables manually:")
        logging.info(f"SSL_CERT_FILE={ssl_base / 'cert.pem'}")
        logging.info(f"REQUESTS_CA_BUNDLE={ssl_base / 'cert.pem'}")
        return False

def verify_certificate_setup():
    """Verify certificate setup by making a test request"""
    try:
        # Create a custom session with specific SSL configuration
        session = requests.Session()
        session.verify = certifi.where()
        
        # Make test request
        response = session.get("https://api.meraki.com")
        logging.info("Certificate verification successful!")
        return True
    except requests.exceptions.SSLError as e:
        logging.error(f"Certificate verification failed: {e}")
        logging.info("Attempting alternative verification method...")
        try:
            # Try with system certificates
            response = requests.get("https://api.meraki.com", verify=True)
            logging.info("Alternative verification successful!")
            return True
        except Exception as alt_e:
            logging.error(f"Alternative verification failed: {alt_e}")
            return False
    except Exception as e:
        logging.error(f"Error during verification: {e}")
        return False

def main():
    logging.info("Starting enhanced SSL certificate setup...")
    
    # Check if running as administrator
    if os.name == 'nt':  # Windows
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            logging.error("This script needs to be run as administrator. Please restart with admin privileges.")
            return
    
    # Create SSL directories
    ssl_base, ssl_certs = create_ssl_directories()
    if not ssl_base or not ssl_certs:
        return
    
    # Install certificates
    certifi_path = install_certificates(ssl_base)
    if not certifi_path:
        return
    
    # Download Meraki certificate
    if not download_meraki_certificate(ssl_certs):
        return
    
    # Set environment variables
    if not set_environment_variables(ssl_base):
        return
    
    # Print certificate paths
    paths = ssl.get_default_verify_paths()
    logging.info("\nCertificate paths:")
    logging.info(f"cafile: {paths.cafile}")
    logging.info(f"capath: {paths.capath}")
    logging.info(f"openssl_cafile: {paths.openssl_cafile}")
    logging.info(f"openssl_capath: {paths.openssl_capath}")
    
    # Verify setup
    if verify_certificate_setup():
        logging.info("\nSSL Certificate setup completed successfully!")
    else:
        logging.error("\nSSL Certificate setup completed with errors.")
        logging.info("\nTroubleshooting steps:")
        logging.info("1. Verify that the certificate files exist in the specified locations")
        logging.info("2. Check if your organization uses a proxy")
        logging.info("3. Ensure your system time is correct")
        logging.info("4. Try restarting your computer to apply environment variables")
        logging.info("5. Check if any antivirus software is blocking the connections")

if __name__ == "__main__":
    main()
