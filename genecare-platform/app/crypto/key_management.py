from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import serialization
import os
import base64
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KeyManager:
    """
    Simulates a secure key management service for AES-256 keys.
    In a production environment, this would interface with a cloud KMS like AWS KMS, 
    Azure Key Vault, or GCP KMS, but for this demo we'll use a local simulation.
    """
    def __init__(self, key_store_path='key_store.json'):
        self.key_store_path = key_store_path
        self.keys = self._load_keys()
        
    def _load_keys(self):
        """Load keys from the simulated key store"""
        try:
            if os.path.exists(self.key_store_path):
                with open(self.key_store_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading keys: {e}")
            return {}
            
    def _save_keys(self):
        """Save keys to the simulated key store"""
        try:
            with open(self.key_store_path, 'w') as f:
                json.dump(self.keys, f)
        except Exception as e:
            logger.error(f"Error saving keys: {e}")
            
    def generate_key(self, key_id, salt=None):
        """Generate a new AES-256 key with the given ID"""
        if salt is None:
            salt = os.urandom(16)
        
        # Generate a random master key
        master_key = os.urandom(32)  # 256 bit key
        
        # Encode for storage
        encoded_key = base64.b64encode(master_key).decode('utf-8')
        encoded_salt = base64.b64encode(salt).decode('utf-8')
        
        # Store the key and salt
        self.keys[key_id] = {
            'key': encoded_key,
            'salt': encoded_salt,
            'created': True  # We could add timestamp here
        }
        
        # Save the updated key store
        self._save_keys()
        
        logger.info(f"Generated new key with ID: {key_id}")
        return master_key
    
    def get_key(self, key_id):
        """Retrieve a key from the key store by ID"""
        if key_id not in self.keys:
            logger.error(f"Key ID {key_id} not found in key store")
            return None
        
        key_data = self.keys[key_id]
        decoded_key = base64.b64decode(key_data['key'])
        
        return decoded_key
    
    def delete_key(self, key_id):
        """Delete a key from the key store"""
        if key_id in self.keys:
            del self.keys[key_id]
            self._save_keys()
            logger.info(f"Deleted key with ID: {key_id}")
            return True
        return False

# Global key manager instance
_key_manager = None

def get_key_manager():
    """Get the global key manager instance"""
    global _key_manager
    if _key_manager is None:
        _key_manager = KeyManager()
    return _key_manager

def derive_key_from_password(password, salt=None):
    """
    Derive an encryption key from a password using PBKDF2.
    This is for demonstration purposes - in production, use a KMS.
    """
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 256 bits
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode())
    return key, salt