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
import sqlite3
from getpass import getpass
from termcolor import colored
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode

def generate_fernet_key(password):
    return Fernet(urlsafe_b64encode(password.encode('utf-8').ljust(32)[:32]))

# ==================================================
# CREATE the Cisco Meraki CLU Database
# ==================================================
def create_cisco_meraki_clu_db(db_path, fernet):
    """Create the Cisco Meraki CLU database"""
    try:
        conn = sqlite3.connect(db_path)
        
        # Create the sensitive_data table for API keys
        conn.execute('''
        CREATE TABLE IF NOT EXISTS sensitive_data (
            id INTEGER PRIMARY KEY,
            data BLOB
        )
        ''')
        
        # Create the tools_ipinfo table for IPinfo tokens
        conn.execute('''
        CREATE TABLE IF NOT EXISTS tools_ipinfo (
            id INTEGER PRIMARY KEY,
            access_token TEXT
        )
        ''')
        
        # Create the api_settings table for API mode
        conn.execute('''
        CREATE TABLE IF NOT EXISTS api_settings (
            id INTEGER PRIMARY KEY,
            api_mode TEXT DEFAULT 'custom'
        )
        ''')
        
        # Insert default API mode if not exists
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM api_settings")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO api_settings (api_mode) VALUES ('custom')")
        
        conn.commit()
        print(f"Database created successfully at {db_path}")
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# ==================================================
# CREATE a new Database table for IPinfo token
# ==================================================
def prompt_create_database():
    """Prompt user to create a new database"""
    print("\nNo database found. Creating a new one...")
    
    # Create the database directory if it doesn't exist
    db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Create the sensitive data database
    db_path = os.path.join(db_dir, 'cisco_meraki_clu_db.db')
    
    # Generate a default Fernet key for initial setup
    default_password = "cisco_meraki_clu_default_password"
    fernet = Fernet(urlsafe_b64encode(default_password.encode('utf-8').ljust(32)[:32]))
    
    if create_cisco_meraki_clu_db(db_path, fernet):
        print("Database created successfully.")
    else:
        print("Failed to create database.")
    
    # Create the settings database in user's home directory
    home_db_path = os.path.join(os.path.expanduser("~"), ".cisco_meraki_clu.db")
    if create_cisco_meraki_clu_db(home_db_path, fernet):
        print("Settings database created successfully.")
    else:
        print("Failed to create settings database.")

# ==================================================
# SET API mode (SDK or Custom)
# ==================================================
def set_api_mode(fernet, mode):
    """Store the API mode preference in the database"""
    conn = None
    try:
        # Use the settings database in user's home directory
        db_path = os.path.join(os.path.expanduser("~"), ".cisco_meraki_clu.db")
        
        # Ensure the database exists
        if not os.path.exists(db_path):
            prompt_create_database()
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ensure the api_settings table exists
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_settings (
            id INTEGER PRIMARY KEY,
            api_mode TEXT DEFAULT 'custom'
        )
        ''')
        
        try:
            # Check if a record exists in the api_settings table
            cursor.execute("SELECT COUNT(*) FROM api_settings")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Insert a new record
                cursor.execute("INSERT INTO api_settings (api_mode) VALUES (?)", (mode,))
            else:
                # Update the existing record
                cursor.execute("UPDATE api_settings SET api_mode = ? WHERE id = 1", (mode,))
            
            conn.commit()
            print(f"API mode set to: {mode}")
            return True
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            if conn:
                conn.rollback()
            return False
    except Exception as e:
        print(f"Error setting API mode: {e}")
        return False
    finally:
        if conn:
            conn.close()


# ==================================================
# GET API mode (SDK or Custom)
# ==================================================
def get_api_mode(fernet):
    """Retrieve the API mode preference from the database"""
    conn = None
    try:
        # Use the settings database in user's home directory
        db_path = os.path.join(os.path.expanduser("~"), ".cisco_meraki_clu.db")
        
        # Ensure the database exists
        if not os.path.exists(db_path):
            prompt_create_database()
            return "custom"  # Default to custom if database doesn't exist
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ensure the api_settings table exists
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_settings (
            id INTEGER PRIMARY KEY,
            api_mode TEXT DEFAULT 'custom'
        )
        ''')
        
        try:
            # Check if a record exists in the api_settings table
            cursor.execute("SELECT COUNT(*) FROM api_settings")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Insert default value
                cursor.execute("INSERT INTO api_settings (api_mode) VALUES ('custom')")
                conn.commit()
                return "custom"
            
            # Get the API mode
            cursor.execute("SELECT api_mode FROM api_settings WHERE id = 1")
            result = cursor.fetchone()
            
            if result and result[0]:
                return result[0]
            else:
                return "custom"  # Default to custom if no value is found
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return "custom"  # Default to custom on error
    except Exception as e:
        print(f"Error getting API mode: {e}")
        return "custom"  # Default to custom on error
    finally:
        if conn:
            conn.close()


# ==================================================
# GET IPinfo token
# ==================================================
def get_tools_ipinfo_access_token(fernet):
    """Retrieve the IPinfo access token from the database"""
    conn = None
    try:
        # Use the settings database in user's home directory
        db_path = os.path.join(os.path.expanduser("~"), ".cisco_meraki_clu.db")
        
        # Ensure the database exists
        if not os.path.exists(db_path):
            prompt_create_database()
            return None
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ensure the tools_ipinfo table exists
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tools_ipinfo (
            id INTEGER PRIMARY KEY,
            access_token TEXT
        )
        ''')
        
        # Get the access token
        cursor.execute("SELECT access_token FROM tools_ipinfo WHERE id = 1")
        result = cursor.fetchone()
        
        if result and result[0]:
            return result[0]
        else:
            return None
    except Exception as e:
        print(f"Error getting IPinfo token: {e}")
        return None
    finally:
        if conn:
            conn.close()


# ==================================================
# SET IPinfo token
# ==================================================
def store_tools_ipinfo_access_token(access_token, fernet):
    """Store the IPinfo access token in the database"""
    conn = None
    try:
        # Use the settings database in user's home directory
        db_path = os.path.join(os.path.expanduser("~"), ".cisco_meraki_clu.db")
        
        # Ensure the database exists
        if not os.path.exists(db_path):
            prompt_create_database()
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ensure the tools_ipinfo table exists
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tools_ipinfo (
            id INTEGER PRIMARY KEY,
            access_token TEXT
        )
        ''')
        
        # Check if a record exists
        cursor.execute("SELECT COUNT(*) FROM tools_ipinfo")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Insert a new record
            cursor.execute("INSERT INTO tools_ipinfo (access_token) VALUES (?)", (access_token,))
        else:
            # Update the existing record
            cursor.execute("UPDATE tools_ipinfo SET access_token = ? WHERE id = 1", (access_token,))
        
        conn.commit()
        print("IPinfo token stored successfully.")
        return True
    except Exception as e:
        print(f"Error storing IPinfo token: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


# ==================================================
# Check if database exists
# ==================================================
def database_exists(db_path):
    """Check if the database file exists"""
    return os.path.exists(db_path)