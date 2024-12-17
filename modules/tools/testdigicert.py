import os
import ssl
import certifi
import requests
import platform
import sys
import json
import socket
import OpenSSL.crypto
from datetime import datetime

# Add the parent directory to the Python path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from modules.meraki import meraki_api

def test_ssl_connection():
    """Test SSL connection to Meraki API using different methods"""
    print(f"Python version: {platform.python_version()}")
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Certifi version: {certifi.__version__}")
    print(f"Requests version: {requests.__version__}")
    
    print("\nTesting Meraki API connection...")
    
    # Get API key from environment
    api_key = os.getenv('MERAKI_DASHBOARD_API_KEY')
    if not api_key:
        print("No API key found in environment. Please set MERAKI_DASHBOARD_API_KEY.")
        return
    
    # Test connection using our custom implementation
    try:
        headers = {
            "X-Cisco-Meraki-API-Key": api_key,
            "Content-Type": "application/json"
        }
        url = "https://api.meraki.com/api/v1/organizations"
        
        print("\nAttempting to connect to Meraki API...")
        response = meraki_api.make_meraki_request(url, headers)
        
        if response:
            print("✓ Successfully connected to Meraki API!")
            print(f"✓ Found {len(response)} organizations")
            print("\nFirst organization details:")
            print(json.dumps(response[0], indent=2))
    except Exception as e:
        print(f"✗ Failed to connect: {str(e)}")
    
    print("\nProxy Information:")
    print(f"HTTP_PROXY: {os.environ.get('HTTP_PROXY', 'Not set')}")
    print(f"HTTPS_PROXY: {os.environ.get('HTTPS_PROXY', 'Not set')}")
    
    print("\nCertificate Paths:")
    paths = ssl.get_default_verify_paths()
    print(f"CAFILE: {paths.cafile}")
    print(f"CAPATH: {paths.capath}")
    print(f"OPENSSL_DIR: {paths.openssl_cafile}")
    print(f"OPENSSL_CAPATH: {paths.openssl_capath}")

if __name__ == "__main__":
    test_ssl_connection()