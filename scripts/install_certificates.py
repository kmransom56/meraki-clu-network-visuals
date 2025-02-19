#!/usr/bin/env python3

import os
import sys
import ssl
import certifi
import subprocess
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_system_cert_paths():
    """Get system certificate paths"""
    return ssl.get_default_verify_paths()

def install_certifi():
    """Install certifi package if not present"""
    try:
        import certifi
        logging.info(f"certifi is installed at: {certifi.where()}")
    except ImportError:
        logging.info("Installing certifi...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "certifi"])

def download_meraki_certificate():
    """Download Meraki's SSL certificate"""
    try:
        import requests
        url = "https://api.meraki.com"
        response = requests.get(url, verify=False)
        cert = ssl.get_server_certificate(('api.meraki.com', 443))
        
        # Save certificate
        cert_path = Path.home() / '.ssl' / 'meraki.pem'
        cert_path.parent.mkdir(parents=True, exist_ok=True)
        cert_path.write_text(cert)
        
        logging.info(f"Meraki certificate saved to: {cert_path}")
        return str(cert_path)
    except Exception as e:
        logging.error(f"Error downloading Meraki certificate: {e}")
        return None

def update_system_certificates():
    """Update system certificates"""
    try:
        if sys.platform.startswith('win'):
            # Windows
            logging.info("On Windows, certificates are managed through the Windows Certificate Store")
            logging.info("Please ensure you have the latest Windows updates installed")
        elif sys.platform.startswith('darwin'):
            # macOS
            logging.info("Updating macOS certificates...")
            subprocess.check_call(['security', 'find-certificate', '-a', '-p'])
        else:
            # Linux
            logging.info("Updating Linux certificates...")
            subprocess.check_call(['update-ca-certificates'])
    except Exception as e:
        logging.error(f"Error updating system certificates: {e}")

def main():
    """Main certificate installation function"""
    logging.info("Starting certificate installation...")
    
    # Show current certificate paths
    cert_paths = get_system_cert_paths()
    logging.info("Current certificate paths:")
    for attr, path in vars(cert_paths).items():
        logging.info(f"{attr}: {path}")
    
    # Install certifi
    install_certifi()
    
    # Update system certificates
    update_system_certificates()
    
    # Download Meraki certificate
    meraki_cert = download_meraki_certificate()
    
    if meraki_cert:
        logging.info("\nCertificate installation completed successfully!")
        logging.info(f"Meraki certificate location: {meraki_cert}")
        logging.info(f"System certificate paths: {cert_paths}")
        logging.info(f"Certifi certificate path: {certifi.where()}")
    else:
        logging.error("Failed to complete certificate installation")

if __name__ == "__main__":
    main()