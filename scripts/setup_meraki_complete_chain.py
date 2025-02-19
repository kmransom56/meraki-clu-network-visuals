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
import socket
import OpenSSL.SSL

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_cert_paths():
    """Get certificate paths"""
    temp_dir = Path(tempfile.gettempdir())
    return {
        'chain_pem': temp_dir / "meraki_chain.pem",
        'chain_der': temp_dir / "meraki_chain.cer",
        'ps1': temp_dir / "import_chain.ps1"
    }

def get_certificate_chain(hostname='api.meraki.com', port=443):
    """Get the complete certificate chain"""
    try:
        # Create SSL context
        context = OpenSSL.SSL.Context(OpenSSL.SSL.TLSv1_2_METHOD)
        context.set_verify(OpenSSL.SSL.VERIFY_NONE)

        # Create connection
        conn = OpenSSL.SSL.Connection(context, socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        conn.set_connect_state()
        conn.connect((hostname, port))
        conn.do_handshake()

        # Get certificate chain
        certs = conn.get_peer_cert_chain()
        
        # Convert to PEM format
        cert_chain = []
        for cert in certs:
            cert_chain.append(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert).decode())

        # Close connection
        conn.close()

        return cert_chain
    except Exception as e:
        logging.error(f"Error getting certificate chain: {e}")
        return None

def save_certificate_chain(cert_chain):
    """Save certificate chain to files"""
    try:
        paths = get_cert_paths()
        
        # Save PEM chain
        with open(paths['chain_pem'], 'w') as f:
            for cert in cert_chain:
                f.write(cert)

        # Create PowerShell script to import certificates
        ps_script = """
$ErrorActionPreference = "Stop"
$certPath = "{}"
$certs = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2Collection
$certs.Import($certPath)

$store = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root", "LocalMachine")
$store.Open("ReadWrite")

try {{
    foreach ($cert in $certs) {{
        try {{
            $store.Add($cert)
            Write-Output "Added certificate: $($cert.Subject)"
        }} catch {{
            Write-Error "Failed to add certificate: $($cert.Subject)"
            Write-Error $_
        }}
    }}
    Write-Output "Certificate chain imported successfully"
}} finally {{
    $store.Close()
}}
""".format(paths['chain_pem'].as_posix())

        paths['ps1'].write_text(ps_script)
        
        logging.info(f"Certificate chain saved to: {paths['chain_pem']}")
        return paths
    except Exception as e:
        logging.error(f"Error saving certificate chain: {e}")
        return None

def import_certificate_chain(ps_path):
    """Import certificate chain using PowerShell"""
    try:
        cmd = [
            'powershell.exe',
            '-ExecutionPolicy',
            'Bypass',
            '-File',
            str(ps_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if "Certificate chain imported successfully" in result.stdout:
            logging.info("Certificate chain imported successfully")
            logging.info("Imported certificates:")
            for line in result.stdout.splitlines():
                if line.startswith("Added certificate:"):
                    logging.info(f"  {line}")
            return True
        else:
            logging.error(f"Error importing certificate chain: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Error running PowerShell script: {e}")
        return False

def configure_ssl_environment(cert_path):
    """Configure SSL environment"""
    try:
        # Set environment variables
        os.environ['REQUESTS_CA_BUNDLE'] = str(cert_path)
        os.environ['SSL_CERT_FILE'] = str(cert_path)
        
        # Set permanent environment variables
        ps_commands = f"""
[Environment]::SetEnvironmentVariable('REQUESTS_CA_BUNDLE', '{str(cert_path).replace("\\", "\\\\")}', 'User')
[Environment]::SetEnvironmentVariable('SSL_CERT_FILE', '{str(cert_path).replace("\\", "\\\\")}', 'User')
"""
        ps_path = Path(tempfile.gettempdir()) / "set_ssl_env.ps1"
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
        logging.error(f"Error configuring SSL environment: {e}")
        return False

def verify_setup():
    """Verify the setup"""
    try:
        # Disable warnings for verification
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Create session
        session = requests.Session()
        
        # Try different verification methods
        methods = [
            ("System certificates", True),
            ("Chain file", get_cert_paths()['chain_pem']),
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
    logging.info("Starting Meraki Certificate Chain Setup...")
    
    # Check if running as administrator
    if os.name == 'nt':
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            logging.error("This script needs to be run as administrator. Please restart with admin privileges.")
            return
    
    # Install required packages
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyOpenSSL"])
    except Exception as e:
        logging.error(f"Error installing required packages: {e}")
        return
    
    # Get certificate chain
    cert_chain = get_certificate_chain()
    if not cert_chain:
        return
    
    # Save certificate chain
    paths = save_certificate_chain(cert_chain)
    if not paths:
        return
    
    # Import certificate chain
    if not import_certificate_chain(paths['ps1']):
        return
    
    # Configure SSL environment
    if not configure_ssl_environment(paths['chain_pem']):
        return
    
    # Verify setup
    if verify_setup():
        logging.info("\nCertificate chain setup completed successfully!")
        logging.info("\nSetup Information:")
        logging.info(f"1. Certificate chain location: {paths['chain_pem']}")
        logging.info("2. Certificates imported to Windows Root store")
        logging.info("3. Environment variables configured")
    else:
        logging.error("\nCertificate setup completed with errors")
        logging.info("\nTroubleshooting steps:")
        logging.info("1. Verify certificate chain in certmgr.msc")
        logging.info("2. Check certificate file contents:")
        logging.info(f"   type {paths['chain_pem']}")
        logging.info("3. Try these PowerShell commands:")
        logging.info(f"   $env:REQUESTS_CA_BUNDLE = '{paths['chain_pem']}'")
        logging.info(f"   $env:SSL_CERT_FILE = '{paths['chain_pem']}'")
        logging.info("4. Restart your computer")
        logging.info("5. If issues persist, check with IT about:")
        logging.info("   - Proxy settings")
        logging.info("   - Certificate trust policies")
        logging.info("   - Network security policies")

if __name__ == "__main__":
    main()