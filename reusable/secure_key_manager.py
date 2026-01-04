"""
Secure Key Manager - Reusable API Key Management

A secure, reusable module for storing and retrieving API keys and other sensitive data.
Uses Fernet encryption and SQLite for storage.

Usage:
    from reusable.secure_key_manager import SecureKeyManager
    
    # Initialize with your app name (creates app-specific storage)
    key_manager = SecureKeyManager(app_name="my_app")
    
    # Save an API key
    key_manager.save_key("OPENAI_API_KEY", "sk-...")
    
    # Retrieve an API key
    api_key = key_manager.get_key("OPENAI_API_KEY")
    
    # Check if a key exists
    if key_manager.has_key("OPENAI_API_KEY"):
        print("Key exists")
    
    # Delete a key
    key_manager.delete_key("OPENAI_API_KEY")
"""

import os
import sqlite3
from typing import Optional
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode
import hashlib


class SecureKeyManager:
    """
    Secure key manager for storing and retrieving encrypted API keys and sensitive data.
    
    Features:
    - Fernet encryption for secure storage
    - SQLite database for persistence
    - App-specific storage (isolated by app name)
    - Environment variable fallback support
    - Multiple key storage (not just one key)
    """
    
    def __init__(self, app_name: str = "default_app", encryption_password: Optional[str] = None, 
                 db_path: Optional[str] = None):
        """
        Initialize the secure key manager.
        
        Args:
            app_name: Name of the application (used for database isolation)
            encryption_password: Password for encryption key generation. 
                                If None, uses a default based on app_name.
            db_path: Custom database path. If None, uses ~/.{app_name}_keys.db
        """
        self.app_name = app_name
        
        # Generate encryption password if not provided
        if encryption_password is None:
            # Use app name + user home to create a unique key per app/user
            default_password = f"{app_name}_{os.path.expanduser('~')}"
            encryption_password = hashlib.sha256(default_password.encode()).hexdigest()[:32]
        
        # Generate Fernet key from password
        self.fernet = Fernet(urlsafe_b64encode(encryption_password.encode('utf-8').ljust(32)[:32]))
        
        # Set database path
        if db_path is None:
            self.db_path = os.path.join(os.path.expanduser("~"), f".{app_name}_keys.db")
        else:
            self.db_path = db_path
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize the database and create tables if needed"""
        try:
            # Ensure directory exists
            if not os.path.exists(os.path.dirname(self.db_path)):
                os.makedirs(os.path.dirname(self.db_path))
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table for storing keys
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS secure_keys (
                    key_name TEXT PRIMARY KEY,
                    encrypted_data BLOB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize database: {e}")
    
    def save_key(self, key_name: str, key_value: str, env_var_name: Optional[str] = None) -> bool:
        """
        Save an API key or sensitive value securely.
        
        Args:
            key_name: Internal name for the key (e.g., "openai_api_key")
            key_value: The actual key value to store
            env_var_name: Optional environment variable name to check first
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check environment variable first if specified
            if env_var_name and os.environ.get(env_var_name):
                # Environment variable takes precedence, but we'll still store it
                pass
            
            # Encrypt the key
            encrypted_data = self.fernet.encrypt(key_value.encode('utf-8'))
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert or update the key
            cursor.execute('''
                INSERT OR REPLACE INTO secure_keys (key_name, encrypted_data, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key_name.lower(), encrypted_data))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving key {key_name}: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def get_key(self, key_name: str, env_var_name: Optional[str] = None, 
                default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve an API key or sensitive value.
        
        Priority order:
        1. Environment variable (if env_var_name provided)
        2. Stored encrypted key
        3. Default value (if provided)
        
        Args:
            key_name: Internal name for the key
            env_var_name: Optional environment variable name to check first
            default: Default value if key not found
            
        Returns:
            The decrypted key value, or None if not found
        """
        # Check environment variable first
        if env_var_name and os.environ.get(env_var_name):
            return os.environ.get(env_var_name)
        
        # Try to get from database
        try:
            if not os.path.exists(self.db_path):
                return default
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT encrypted_data FROM secure_keys WHERE key_name = ?", 
                          (key_name.lower(),))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                # Decrypt the key
                try:
                    decrypted_key = self.fernet.decrypt(result[0])
                    return decrypted_key.decode('utf-8')
                except Exception as e:
                    print(f"Error decrypting key {key_name}: {e}")
                    return default
            else:
                return default
        except Exception as e:
            print(f"Error retrieving key {key_name}: {e}")
            return default
    
    def has_key(self, key_name: str) -> bool:
        """Check if a key exists in storage"""
        try:
            if not os.path.exists(self.db_path):
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT 1 FROM secure_keys WHERE key_name = ?", (key_name.lower(),))
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
        except Exception:
            return False
    
    def delete_key(self, key_name: str) -> bool:
        """Delete a stored key"""
        try:
            if not os.path.exists(self.db_path):
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM secure_keys WHERE key_name = ?", (key_name.lower(),))
            conn.commit()
            deleted = cursor.rowcount > 0
            conn.close()
            
            return deleted
        except Exception as e:
            print(f"Error deleting key {key_name}: {e}")
            return False
    
    def list_keys(self) -> list:
        """List all stored key names"""
        try:
            if not os.path.exists(self.db_path):
                return []
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT key_name FROM secure_keys")
            keys = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return keys
        except Exception as e:
            print(f"Error listing keys: {e}")
            return []
    
    def get_fernet(self) -> Fernet:
        """Get the Fernet instance for advanced usage"""
        return self.fernet
