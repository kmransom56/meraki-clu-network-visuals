import os
import sys
import ssl
import certifi
import requests
import subprocess
from pathlib import Path
import logging
import urllib3
import winreg

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_windows_proxy_settings():
    """Get Windows proxy settings from registry"""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r'Software\Microsoft\Windows\CurrentVersion\Internet Settings') as key:
            proxy_enable = winreg.QueryValueEx(key, 'ProxyEnable')[0]
            if proxy_enable:
                proxy_server = winreg.QueryValueEx(key, 'ProxyServer')[0]
                return f"http://{proxy_server}"
            return None
    except Exception as e:
        logging.warning(f"Could not read proxy settings: {e}")
        return None

def create_cert_directories():
    """Create certificate directories in user's home folder"""
    cert_dir = Path.home() / '.certificates'
    try:
        cert_dir.mkdir(parents=True, exist_ok=True)
        return cert_dir
    except Exception as e:
        logging.error(f"Error creating certificate directory: {e}")
        return None

def download_meraki_cert(cert_dir):
    """Download Meraki's certificate chain"""
    try:
        # Disable warnings temporarily
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Get proxy settings
        proxy = get_windows_proxy_settings()
        proxies = {'https': proxy} if proxy else None
        
        # Create a session
        session = requests.Session()
        if proxies:
            session.proxies = proxies
        
        # Get the certificate chain
        response = session.get('https://api.meraki.com', verify=False)
        server_cert = ssl.get_server_certificate(('api.meraki.com', 443))
        
        # Save the certificate
        cert_path = cert_dir / 'meraki-chain.pem'
        with open(cert_path, 'w') as f:
            f.write(server_cert)
        
        logging.info(f"Saved Meraki certificate to {cert_path}")
        return cert_path
    except Exception as e:
        logging.error(f"Error downloading Meraki certificate: {e}")
        return None

def combine_certificates(cert_dir, meraki_cert_path):
    """Combine Meraki and system certificates"""
    try:
        combined_path = cert_dir / 'combined-certs.pem'
        
        # Start with certifi's certificates
        with open(certifi.where(), 'r') as certifi_file:
            certifi_certs = certifi_file.read()
        
        # Add Meraki certificate
        with open(meraki_cert_path, 'r') as meraki_file:
            meraki_cert = meraki_file.read()
        
        # Write combined certificates
        with open(combined_path, 'w') as combined_file:
            combined_file.write(certifi_certs)
            combined_file.write('\n')
            combined_file.write(meraki_cert)
        
        logging.info(f"Created combined certificate file at {combined_path}")
        return combined_path
    except Exception as e:
        logging.error(f"Error combining certificates: {e}")
        return None

def set_cert_environment(cert_path):
    """Set certificate environment variables"""
    try:
        # Set for current process
        os.environ['REQUESTS_CA_BUNDLE'] = str(cert_path)
        os.environ['SSL_CERT_FILE'] = str(cert_path)
        
        # Set for user
        subprocess.run(['setx', 'REQUESTS_CA_BUNDLE', str(cert_path)], check=True)
        subprocess.run(['setx', 'SSL_CERT_FILE', str(cert_path)], check=True)
        
        logging.info("Set certificate environment variables")
        return True
    except Exception as e:
        logging.error(f"Error setting environment variables: {e}")
        return False

def test_meraki_connection(cert_path):
    """Test connection to Meraki API"""
    try:
        # Get proxy settings
        proxy = get_windows_proxy_settings()
        proxies = {'https': proxy} if proxy else None
        
        # Create session with custom settings
        session = requests.Session()
        session.verify = str(cert_path)
        if proxies:
            session.proxies = proxies
        
        # Test connection
        response = session.get('https://api.meraki.com')
        logging.info(f"Successfully connected to Meraki API (Status: {response.status_code})")
        return True
    except requests.exceptions.SSLError as e:
        logging.error(f"SSL Error: {e}")
        return False
    except Exception as e:
        logging.error(f"Connection Error: {e}")
        return False

def main():
    logging.info("Starting Meraki SSL setup...")
    
    # Create certificate directory
    cert_dir = create_cert_directories()
    if not cert_dir:
        return
    
    # Download Meraki certificate
    meraki_cert_path = download_meraki_cert(cert_dir)
    if not meraki_cert_path:
        return
    
    # Combine certificates
    combined_cert_path = combine_certificates(cert_dir, meraki_cert_path)
    if not combined_cert_path:
        return
    
    # Set environment variables
    if not set_cert_environment(combined_cert_path):
        return
    
    # Test connection
    if test_meraki_connection(combined_cert_path):
        logging.info("\nSSL setup completed successfully!")
        logging.info(f"\nCertificate location: {combined_cert_path}")
        if proxy := get_windows_proxy_settings():
            logging.info(f"Using proxy: {proxy}")
    else:
        logging.error("\nSSL setup completed with errors")
        logging.info("\nTroubleshooting information:")
        logging.info(f"1. Certificate location: {combined_cert_path}")
        logging.info(f"2. Proxy settings: {get_windows_proxy_settings()}")
        logging.info("3. Try running these commands in PowerShell (as administrator):")
        logging.info(f"   $env:REQUESTS_CA_BUNDLE='{combined_cert_path}'")
        logging.info(f"   $env:SSL_CERT_FILE='{combined_cert_path}'")
        logging.info("4. Check your organization's security policies")
        logging.info("5. Verify network connectivity to api.meraki.com")

if __name__ == "__main__":
    main()