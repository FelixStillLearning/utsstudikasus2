from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import os
import base64
import json
import logging
from .key_management import get_key_manager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AESCipher:
    """
    Implements AES-256 encryption for sensitive health and DNA data.
    Uses CBC mode with proper padding and IV handling.
    """
    def __init__(self, key=None, key_id=None):
        if key is None and key_id is None:
            raise ValueError("Either key or key_id must be provided")
            
        if key_id:
            # Retrieve key from the key manager
            key_manager = get_key_manager()
            key = key_manager.get_key(key_id)
            if not key:
                raise ValueError(f"No key found with ID: {key_id}")
            self.key = key
            self.key_id = key_id
        else:
            # Use provided key
            if isinstance(key, str):
                key = key.encode('utf-8')
            self.key = key.ljust(32)[:32]  # Ensure key is 32 bytes
            self.key_id = None

    def encrypt(self, data, metadata=None):
        """
        Encrypt data using AES-256-CBC with a random IV
        
        Args:
            data: The data to encrypt (string or bytes)
            metadata: Optional metadata to include with the encrypted data
            
        Returns:
            Dictionary containing IV, ciphertext, and optional metadata
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        # Generate a random IV
        iv = get_random_bytes(AES.block_size)
        
        # Create new cipher with key and random IV
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        
        # Pad data to block size and encrypt
        ct_bytes = cipher.encrypt(pad(data, AES.block_size))
        
        # Encode binary data as base64 strings
        iv_b64 = base64.b64encode(iv).decode('utf-8')
        ct_b64 = base64.b64encode(ct_bytes).decode('utf-8')
        
        # Create result structure
        result = {
            'iv': iv_b64,
            'ciphertext': ct_b64,
            'algorithm': 'AES-256-CBC',
        }
        
        # Include key ID if available
        if self.key_id:
            result['key_id'] = self.key_id
            
        # Include metadata if provided
        if metadata:
            result['metadata'] = metadata
            
        return result

    def decrypt(self, encrypted_data):
        """
        Decrypt data that was encrypted with this cipher.
        
        Args:
            encrypted_data: Dictionary containing IV and ciphertext
            
        Returns:
            Decrypted data as string
        """
        # Extract necessary components
        iv = base64.b64decode(encrypted_data['iv'])
        ct = base64.b64decode(encrypted_data['ciphertext'])
        
        # Create cipher with same key and provided IV
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        
        # Decrypt and unpad
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        
        return pt.decode('utf-8')

    @staticmethod
    def encrypt_data(data, key_id='health_data_key'):
        """
        Static method to quickly encrypt data using the default key.
        For health/DNA data encryption.
        """
        key_manager = get_key_manager()
        key = key_manager.get_key(key_id)
        
        # If key doesn't exist, generate a new one
        if not key:
            logger.info(f"Generating new encryption key with ID: {key_id}")
            key = key_manager.generate_key(key_id)
            
        cipher = AESCipher(key=key, key_id=key_id)
        return cipher.encrypt(data)

    @staticmethod
    def decrypt_data(encrypted_data):
        """
        Static method to decrypt data using the appropriate key.
        """
        # Get key ID from encrypted data
        key_id = encrypted_data.get('key_id', 'health_data_key')
        
        # Get key from key manager
        key_manager = get_key_manager()
        key = key_manager.get_key(key_id)
        
        if not key:
            raise ValueError(f"No key found with ID: {key_id}")
            
        cipher = AESCipher(key=key)
        return cipher.decrypt(encrypted_data)

# Simplified functions for easy access
def encrypt_health_data(data, metadata=None):
    """Encrypt health or DNA data using AES-256"""
    return AESCipher.encrypt_data(data, key_id='health_data_key')
    
def decrypt_health_data(encrypted_data):
    """Decrypt health or DNA data"""
    return AESCipher.decrypt_data(encrypted_data)
    
def encrypt_dna_data(data, metadata=None):
    """Encrypt DNA data using AES-256 with a dedicated key"""
    return AESCipher.encrypt_data(data, key_id='dna_data_key')
    
def decrypt_dna_data(encrypted_data):
    """Decrypt DNA data"""
    return AESCipher.decrypt_data(encrypted_data)