#**************************************************************************
#   App:         Cisco Meraki CLU                                         *
#   Version:     1.4                                                      *
#   Author:      Matia Zanella                                            *
#   Description: Cisco Meraki CLU (Command Line Utility) is an essential  *
#                tool crafted for Network Administrators managing Meraki  *
#   Github:      https://github.com/akamura/cisco-meraki-clu/             *
#                                                                         *
#   Icon Author:        Cisco Systems, Inc.                               *
#   Icon Author URL:    https://meraki.cisco.com/                         *
#                                                                         *
#   Copyright (C) 2024 Matia Zanella                                      *
#   https://www.matiazanella.com                                          *
#                                                                         *
#   This program is free software; you can redistribute it and/or modify  *
#   it under the terms of the GNU General Public License as published by  *
#   the Free Software Foundation; either version 2 of the License, or     *
#   (at your option) any later version.                                   *
#                                                                         *
#   This program is distributed in the hope that it will be useful,       *
#   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#   GNU General Public License for more details.                          *
#                                                                         *
#   You should have received a copy of the GNU General Public License     *
#   along with this program; if not, write to the                         *
#   Free Software Foundation, Inc.,                                       *
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
#**************************************************************************


# ==================================================
# IMPORT various libraries and modules
# ==================================================
import os
import sys
from termcolor import colored
import logging
import traceback
import argparse

from api import meraki_api_manager
from settings import db_creator
from utilities import submenu
from settings import term_extra

required_packages = {
    "tabulate": "tabulate",
    "pathlib": "pathlib",
    "datetime": "datetime",
    "termcolor": "termcolor",
    "requests": "requests",
    "rich": "rich",
    "setuptools": "setuptools",
    "cryptography": "cryptography"
}

missing_packages = []
for module, package in required_packages.items():
    try:
        __import__(module)
    except ImportError:
        missing_packages.append(package)

if missing_packages:
    print("Missing required Python packages: " + ", ".join(missing_packages))
    print("Please install them using the following command:")
    print(f"{sys.executable} -m pip install " + " ".join(missing_packages))


# ==================================================
# IMPORT various libraries and modules
# ==================================================
import os
import sys
import logging
import traceback
import argparse

required_packages = {
    "tabulate": "tabulate",
    "pathlib": "pathlib",
    "datetime": "datetime",
    "termcolor": "termcolor",
    "requests": "requests",
    "rich": "rich",
    "setuptools": "setuptools",
    "cryptography": "cryptography"
}

missing_packages = []
for module, package in required_packages.items():
    try:
        __import__(module)
    except ImportError:
        missing_packages.append(package)

if missing_packages:
    print("Missing required Python packages: " + ", ".join(missing_packages))
    print("Please install them using the following command:")
    print(f"{sys.executable} -m pip install " + " ".join(missing_packages))
    sys.exit(1)
from getpass import getpass
from datetime import datetime
from termcolor import colored


# ==================================================
# ERROR logging
# ==================================================
logger = logging.getLogger('ciscomerakiclu')
logger.setLevel(logging.ERROR)

log_directory = 'log'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file = os.path.join(log_directory, 'error.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# ==================================================
# VISUALIZE the Main Menu
# ==================================================
def main_menu(fernet):
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()

        api_key = meraki_api_manager.get_api_key(fernet)
        ipinfo_token = db_creator.get_tools_ipinfo_access_token(fernet)
        
        options = [
            "Network wide",
            "Security & SD-WAN", 
            "Switch and wireless",
            "Environmental", 
            "Organization", 
            "The Swiss Army Knife", 
            f"{'Edit Cisco Meraki API Key' if api_key else 'Set Cisco Meraki API Key'}",
            f"{'Edit IPinfo Token' if ipinfo_token else 'Set IPinfo Token'}",
            "Test SSL Connection",  
            "Exit the Command Line Utility"
        ]
        
        current_year = datetime.now().year
        footer = f"\033[1mPROJECT PAGE\033[0m\n{current_year} Matia Zanella\nhttps://developer.cisco.com/codeexchange/github/repo/akamura/cisco-meraki-clu/\n\n\033[1mSUPPORT ME\033[0m\n Fuel me with a coffee if you found it useful https://www.paypal.com/paypalme/matiazanella/\n\n\033[1mDISCLAIMER\033[0m\nThis utility is not an official Cisco Meraki product but is based on the official Cisco Meraki API.\nIt is intended to provide Network Administrators with an easy daily companion in the swiss army knife."

        print("\n")
        print("┌" + "─" * 58 + "┐")
        print("│".ljust(59) + "│")
        for index, option in enumerate(options, start=1):
            print(f"│ {index}. {option}".ljust(59) + "│")
        print("│".ljust(59) + "│")
        print("└" + "─" * 58 + "┘")

        term_extra.print_footer(footer)
        choice = input(colored("Choose a menu option [1-10]: ", "cyan"))

        if choice == '1':
            if api_key:
                submenu.submenu_network_wide(api_key)
            else:
                print("Please set the Cisco Meraki API key first.")
            input(colored("\nPress Enter to return to the main menu...", "green"))
        elif choice == '2':
            if api_key:
                submenu.submenu_mx(api_key)
            else:
                print("Please set the Cisco Meraki API key first.")
            input(colored("\nPress Enter to return to the main menu...", "green"))
        elif choice == '3':
            if api_key:
                submenu.submenu_sw_and_ap(api_key)
            else:
                print("Please set the Cisco Meraki API key first.")
            input(colored("\nPress Enter to return to the main menu...", "green"))
        elif choice == '4':
            if api_key:
                submenu.submenu_environmental(api_key)
            else:
                print("Please set the Cisco Meraki API key first.")
            input(colored("\nPress Enter to return to the main menu...", "green"))
        elif choice == '5':
            if api_key:
                submenu.submenu_organization(api_key)
            else:
                print("Please set the Cisco Meraki API key first.")
            input(colored("\nPress Enter to return to the main menu...", "green"))
        elif choice == '6':
            submenu.swiss_army_knife_submenu(fernet)
        elif choice == '7':
            manage_api_key(fernet)
        elif choice == '8':
            manage_ipinfo_token(fernet)
        elif choice == '9':
            test_ssl_connection(fernet)
        elif choice == '10':
            term_extra.clear_screen()
            term_extra.print_ascii_art()
            print("\nThank you for using the Cisco Meraki Command Line Utility!")
            print("Exiting the program. Goodbye, and have a wonderful day!")
            print("\n \033[1mCONTRIBUTE\033[0m\nThis is not just a project; it's a community effort.\nI'm inviting you to be a part of this journey.\nStar it, fork it, contribute, or just play around with it.\nEvery feedback, issue, or pull request is an opportunity for us to make this tool even more amazing.\nYou are more than welcome to discuss it on GitHub https://github.com/akamura/cisco-meraki-clu/discussions")
            print("\n" * 2)
            break
        else:
            print(colored("Invalid choice. Please try again.", "red"))

def manage_api_key(fernet):
    term_extra.clear_screen()
    api_key = input("\nEnter the Cisco Meraki API Key: ")
    meraki_api_manager.save_api_key(api_key, fernet)

def manage_ipinfo_token(fernet):
    term_extra.clear_screen()
    current_token = db_creator.get_tools_ipinfo_access_token(fernet)
    if current_token:
        print(colored(f"Current IPinfo Token: {current_token}", "yellow"))
        change = input("Do you want to change it? [yes/no]: ").lower()
        if change != 'yes':
            return

    new_token = input("\nEnter the new IPinfo access token: ")
    if new_token:
        db_creator.store_tools_ipinfo_access_token(new_token, fernet)
        print(colored("\nIPinfo access token saved successfully.", "green"))
    else:
        print(colored("No token entered. No changes made.", "red"))

def initialize_api_key():
    """Initialize and manage the Meraki API key"""
    parser = argparse.ArgumentParser(description='Cisco Meraki CLU')
    parser.add_argument('--set-key', help='Set the Meraki API key')
    args = parser.parse_args()

    # Initialize Fernet for encryption
    from api import meraki_api_manager
    # Use a default password for encryption - in a production environment, this should be more secure
    encryption_password = "cisco_meraki_clu_default_key"
    fernet = meraki_api_manager.generate_fernet_key(encryption_password)

    if args.set_key:
        # Store the key securely if provided via command line
        if meraki_api_manager.save_api_key(args.set_key, fernet):
            return args.set_key

    # Try to get key from environment variable
    api_key = os.environ.get('MERAKI_DASHBOARD_API_KEY')
    if api_key:
        return api_key

    # Try to load stored key
    api_key = meraki_api_manager.get_api_key(fernet)
    if api_key:
        return api_key

    # If no key is found, show instructions
    print("\nNo API key found. Please set your Meraki API key using one of these methods:")
    print("\n1. Run the program with the --set-key option:")
    print("   python main.py --set-key YOUR_API_KEY")
    print("\n2. Set a Windows environment variable (Command Prompt as Administrator):")
    print("   setx MERAKI_DASHBOARD_API_KEY \"your-api-key\"")
    print("\n3. Set a temporary environment variable (current session only):")
    print("   set MERAKI_DASHBOARD_API_KEY=your-api-key")
    print("\nNote: After setting an environment variable, you may need to restart your command prompt.")
    return None

def test_ssl_connection(fernet):
    """
    Test the SSL connection handling with the Meraki API
    """
    try:
        term_extra.clear_screen()
        term_extra.print_ascii_art()
        
        print("\nCisco Meraki SSL Connection Test")
        print("===============================")
        
        # Get API key
        api_key = meraki_api_manager.get_api_key(fernet)
        if not api_key:
            print(colored("\nError: API key not found", "red"))
            print("Please set up your Meraki API key first (Option 7 in main menu)")
            input("\nPress Enter to return to main menu...")
            return

        print(colored("\nInitiating SSL connection test...", "cyan"))
        print("1. Testing API connectivity")
        print("2. Verifying SSL certificate handling")
        print("3. Checking proxy configuration")
        
        # Test API connection
        headers = {
            'X-Cisco-Meraki-API-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            # Try to get organizations (simple API call)
            url = 'https://api.meraki.com/api/v1/organizations'
            from modules.meraki.meraki_api import make_meraki_request
            
            response = make_meraki_request(url, headers)
            
            # Success messages
            print(colored("\nTest Results:", "cyan"))
            print(colored("✓ Successfully connected to Meraki API", "green"))
            print(colored("✓ SSL certificate verification successful", "green"))
            print(colored("✓ Proxy configuration working correctly", "green"))
            print(colored(f"✓ Retrieved {len(response)} organizations", "green"))
            print("\nAll tests completed successfully!")
            
        except Exception as e:
            print(colored("\nTest Results:", "red"))
            print(colored("✗ Connection test failed", "red"))
            print(colored(f"\nError details: {str(e)}", "yellow"))
            print(colored("\nTroubleshooting steps:", "cyan"))
            print("1. Verify your network connectivity")
            print("2. Check your proxy configuration")
            print("3. Ensure your API key is correct")
            print("4. Review error.log for detailed information")
            logging.error(f"SSL Connection Error: {str(e)}\n{traceback.format_exc()}")
            
    except Exception as e:
        print(colored(f"\nTest initialization failed: {str(e)}", "red"))
        logging.error(f"SSL Test Error: {str(e)}\n{traceback.format_exc()}")
    
    current_year = datetime.now().year
    footer = f"\033[1mPROJECT PAGE\033[0m\n{current_year} Matia Zanella\nhttps://developer.cisco.com/codeexchange/github/repo/akamura/cisco-meraki-clu/"
    term_extra.print_footer(footer)
    input(colored("\nPress Enter to return to the main menu...", "green"))

def main():
    """Main function to run the Cisco Meraki CLU"""
    try:
        # Initialize API key
        api_key = initialize_api_key()
        if not api_key:
            print("Please set your Meraki API key using one of these methods:")
            print("1. Set MERAKI_DASHBOARD_API_KEY environment variable")
            print("2. Run the program with --set-key YOUR_API_KEY")
            return

        db_path = 'db/cisco_meraki_clu_db.db'
        if not db_creator.database_exists(db_path):
            os.system('cls')  # Clears the terminal screen.
            term_extra.print_ascii_art()
            if db_creator.prompt_create_database():
                db_password = getpass(colored("\nEnter a password for encrypting the database: ", "green"))
                fernet = db_creator.generate_fernet_key(db_password)
                db_creator.update_database_schema(db_path, db_password)  # Update the database schema after creation.
            else:
                print(colored("Database creation cancelled. Exiting program.", "yellow"))
                exit()
        else:
            os.system('cls')  # Clears the terminal screen.
            term_extra.print_ascii_art()
            db_password = getpass(colored("\n\nWelcome to Cisco Meraki Command Line Utility!\nThis program contains sensitive information. Please insert your password to continue: ", "green"))
            fernet = db_creator.generate_fernet_key(db_password)

        # At this point, the database exists, so update the schema as needed.
        db_creator.update_database_schema(db_path, db_password)  # Ensure the schema is updated for existing databases too.

        main_menu(fernet)

    except Exception as e:
        logger.error("An error occurred", exc_info=True)
        print("An error occurred:")
        print(e)
        traceback.print_exc()
        input("\nPress Enter to exit.\n")

if __name__ == "__main__":
    main()