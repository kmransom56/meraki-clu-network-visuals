import os
import ssl
import certifi
import requests
import logging
from pathlib import Path
import urllib3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_certificate_paths():
    """Check all certificate paths"""
    logging.info("Checking certificate paths...")
    
    # Get default verify paths
    paths = ssl.get_default_verify_paths()
    
    # Check each path
    checks = {
        "SSL_CERT_FILE": os.environ.get('SSL_CERT_FILE'),
        "REQUESTS_CA_BUNDLE": os.environ.get('REQUESTS_CA_BUNDLE'),
        "Certifi location": certifi.where(),
        "System cafile": paths.cafile,
        "System capath": paths.capath,
        "OpenSSL cafile": paths.openssl_cafile,
        "OpenSSL capath": paths.openssl_capath
    }
    
    for name, path in checks.items():
        if path:
            exists = Path(path).exists() if path else False
            logging.info(f"{name}: {path} {'(exists)' if exists else '(not found)'}")
        else:
            logging.info(f"{name}: Not set")

def test_ssl_connection():
    """Test SSL connection to Meraki API"""
    logging.info("\nTesting SSL connection to Meraki API...")
    
    # Test configurations
    configs = [
        ("Default verification", None),
        ("Certifi verification", certifi.where()),
        ("System SSL_CERT_FILE", os.environ.get('SSL_CERT_FILE')),
        ("System REQUESTS_CA_BUNDLE", os.environ.get('REQUESTS_CA_BUNDLE'))
    ]
    
    for name, verify in configs:
        try:
            if verify is None:
                response = requests.get("https://api.meraki.com")
            else:
                response = requests.get("https://api.meraki.com", verify=verify)
            logging.info(f"{name}: Success (Status code: {response.status_code})")
        except requests.exceptions.SSLError as e:
            logging.error(f"{name}: SSL Error - {str(e)}")
        except Exception as e:
            logging.error(f"{name}: Error - {str(e)}")

def check_ssl_version():
    """Check SSL/TLS version information"""
    logging.info("\nChecking SSL/TLS information...")
    logging.info(f"OpenSSL version: {ssl.OPENSSL_VERSION}")
    logging.info(f"Default SSL protocol: {ssl.get_default_verify_flags()}")

def main():
    logging.info("Starting certificate verification...")
    
    # Check certificate paths
    check_certificate_paths()
    
    # Check SSL version
    check_ssl_version()
    
    # Test SSL connection
    test_ssl_connection()
    
    logging.info("\nVerification complete!")

if __name__ == "__main__":
    main()