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
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode
from termcolor import colored

def generate_fernet_key(password):
    return Fernet(urlsafe_b64encode(password.encode('utf-8').ljust(32)[:32]))

# Use the settings database in user's home directory for API keys
db_path = os.path.join(os.path.expanduser("~"), ".cisco_meraki_clu.db")

def save_api_key(api_key, fernet):
    """Save the API key to the database"""
    conn = None
    try:
        # Ensure the database directory exists
        if not os.path.exists(os.path.dirname(db_path)):
            os.makedirs(os.path.dirname(db_path))
        
        # Encrypt the API key
        encrypted_api_key = fernet.encrypt(api_key.encode('utf-8'))
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ensure the sensitive_data table exists
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensitive_data (
            id INTEGER PRIMARY KEY,
            data BLOB
        )
        ''')
        
        # Insert or update the API key
        cursor.execute("INSERT OR REPLACE INTO sensitive_data (id, data) VALUES (1, ?)", (encrypted_api_key,))
        conn.commit()
        print(colored("API key saved successfully.", "green"))
        return True
    except Exception as e:
        print(colored(f"An error occurred while saving the API key: {e}", "red"))
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_api_key(fernet):
    """Retrieve the API key from the database"""
    conn = None
    try:
        # Check if the database exists
        if not os.path.exists(db_path):
            # Create the database directory if it doesn't exist
            if not os.path.exists(os.path.dirname(db_path)):
                os.makedirs(os.path.dirname(db_path))
            return None
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the sensitive_data table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sensitive_data'")
        if not cursor.fetchone():
            return None
        
        # Get the encrypted API key
        cursor.execute("SELECT data FROM sensitive_data WHERE id = 1")
        encrypted_api_key = cursor.fetchone()
        
        if not encrypted_api_key:
            return None
        
        # Decrypt the API key
        try:
            api_key = fernet.decrypt(encrypted_api_key[0])
            return api_key.decode('utf-8')
        except Exception as e:
            print(colored(f"Error decrypting API key: {e}", "red"))
            return None
    except Exception as e:
        print(colored(f"An error occurred while accessing the database: {e}", "red"))
        return None
    finally:
        if conn:
            conn.close()