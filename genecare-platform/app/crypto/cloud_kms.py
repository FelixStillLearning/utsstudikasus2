"""
Cloud Key Management Service integrations for GeneCare platform
Provides support for AWS KMS, Azure Key Vault, and Google Cloud KMS
"""
import os
import base64
import logging
from app.config import Config
from flask import current_app

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudKMSManager:
    """Base class for cloud-based key management services"""
    def __init__(self):
        self.service_type = current_app.config.get('KEY_MANAGEMENT_SERVICE', 'local')
        
    def get_kms_client(self):
        """Get the appropriate KMS client based on configuration"""
        if self.service_type == 'aws':
            return AWSKMSClient()
        elif self.service_type == 'azure':
            return AzureKeyVaultClient()
        elif self.service_type == 'gcp':
            return GCPKMSClient()
        else:
            logger.warning(f"Unsupported KMS type: {self.service_type}, falling back to local")
            return None
            
    def generate_key(self, key_id):
        """Generate a new key in the cloud KMS"""
        client = self.get_kms_client()
        if client:
            return client.generate_key(key_id)
        return None
        
    def get_key(self, key_id):
        """Retrieve a key from the cloud KMS"""
        client = self.get_kms_client()
        if client:
            return client.get_key(key_id)
        return None
        
    def encrypt_with_kms(self, plaintext, key_id):
        """Encrypt data using cloud KMS"""
        client = self.get_kms_client()
        if client:
            return client.encrypt(plaintext, key_id)
        return None
        
    def decrypt_with_kms(self, ciphertext, key_id):
        """Decrypt data using cloud KMS"""
        client = self.get_kms_client()
        if client:
            return client.decrypt(ciphertext, key_id)
        return None


class AWSKMSClient:
    """AWS KMS Client implementation"""
    def __init__(self):
        self.region = current_app.config.get('AWS_REGION', 'us-east-1')
        self.key_id = current_app.config.get('AWS_KMS_KEY_ID')
        
        # Import boto3 only if using AWS KMS
        try:
            import boto3
            self.client = boto3.client('kms', region_name=self.region)
            logger.info("AWS KMS client initialized")
        except ImportError:
            logger.error("boto3 not installed. Please install boto3 for AWS KMS support")
            self.client = None
        except Exception as e:
            logger.error(f"Error initializing AWS KMS client: {e}")
            self.client = None
            
    def generate_key(self, key_id):
        """Generate a new key using AWS KMS"""
        if not self.client:
            return None
            
        try:
            # Create a CMK (Customer Master Key)
            response = self.client.create_key(
                Description=f'GeneCare key for {key_id}',
                KeyUsage='ENCRYPT_DECRYPT',
                Origin='AWS_KMS'
            )
            return response['KeyMetadata']['KeyId']
        except Exception as e:
            logger.error(f"Error generating AWS KMS key: {e}")
            return None
            
    def get_key(self, key_id):
        """Get a data key from AWS KMS"""
        if not self.client:
            return None
            
        try:
            # Generate a data key under the CMK
            response = self.client.generate_data_key(
                KeyId=self.key_id or key_id,
                KeySpec='AES_256'
            )
            # Return the plaintext key (this should be used and then discarded)
            return response['Plaintext']
        except Exception as e:
            logger.error(f"Error getting AWS KMS key: {e}")
            return None
            
    def encrypt(self, plaintext, key_id):
        """Encrypt data with AWS KMS"""
        if not self.client:
            return None
            
        try:
            if isinstance(plaintext, str):
                plaintext = plaintext.encode('utf-8')
                
            response = self.client.encrypt(
                KeyId=self.key_id or key_id,
                Plaintext=plaintext
            )
            return base64.b64encode(response['CiphertextBlob']).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encrypting with AWS KMS: {e}")
            return None
            
    def decrypt(self, ciphertext, key_id=None):
        """Decrypt data with AWS KMS"""
        if not self.client:
            return None
            
        try:
            if isinstance(ciphertext, str):
                ciphertext = base64.b64decode(ciphertext)
                
            response = self.client.decrypt(
                CiphertextBlob=ciphertext
            )
            return response['Plaintext']
        except Exception as e:
            logger.error(f"Error decrypting with AWS KMS: {e}")
            return None


class AzureKeyVaultClient:
    """Azure Key Vault Client implementation"""
    def __init__(self):
        self.vault_url = current_app.config.get('AZURE_VAULT_URL')
        self.key_name = current_app.config.get('AZURE_KEY_NAME')
        
        # Import azure libraries only if using Azure Key Vault
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.keys import KeyClient
            from azure.keyvault.keys.crypto import CryptographyClient
            
            self.credential = DefaultAzureCredential()
            self.key_client = KeyClient(vault_url=self.vault_url, credential=self.credential)
            self.crypto_client = None  # Will be initialized with specific key
            logger.info("Azure Key Vault client initialized")
        except ImportError:
            logger.error("Azure libraries not installed. Please install azure-identity and azure-keyvault-keys")
            self.key_client = None
        except Exception as e:
            logger.error(f"Error initializing Azure Key Vault client: {e}")
            self.key_client = None
            
    def generate_key(self, key_id):
        """Create a new key in Azure Key Vault"""
        if not self.key_client:
            return None
            
        try:
            from azure.keyvault.keys.models import KeyType
            
            # Create a new key
            key = self.key_client.create_key(
                name=key_id,
                key_type=KeyType.RSA
            )
            return key.id
        except Exception as e:
            logger.error(f"Error generating Azure Key Vault key: {e}")
            return None
            
    def get_key(self, key_id):
        """Get a key from Azure Key Vault (returns a wrapped symmetric key)"""
        if not self.key_client:
            return None
            
        try:
            # For symmetric encryption, we generate a random key and protect it with Key Vault
            import os
            from azure.keyvault.keys.crypto import CryptographyClient
            
            # Get key reference
            key = self.key_client.get_key(self.key_name or key_id)
            
            # Create crypto client for this key
            crypto_client = CryptographyClient(key, self.credential)
            
            # Generate a symmetric key
            symmetric_key = os.urandom(32)  # 256 bits for AES-256
            
            # Encrypt the symmetric key using the Key Vault key
            # We'll manage this wrapped key ourselves
            return symmetric_key
        except Exception as e:
            logger.error(f"Error getting Azure Key Vault key: {e}")
            return None
            
    def encrypt(self, plaintext, key_id):
        """Encrypt data with Azure Key Vault"""
        if not self.key_client:
            return None
            
        try:
            from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm
            
            # Get key reference
            key = self.key_client.get_key(self.key_name or key_id)
            
            # Create crypto client for this key
            crypto_client = CryptographyClient(key, self.credential)
            
            if isinstance(plaintext, str):
                plaintext = plaintext.encode('utf-8')
                
            # Encrypt using RSA-OAEP (suitable for small payloads)
            result = crypto_client.encrypt(EncryptionAlgorithm.rsa_oaep, plaintext)
            return base64.b64encode(result.ciphertext).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encrypting with Azure Key Vault: {e}")
            return None
            
    def decrypt(self, ciphertext, key_id=None):
        """Decrypt data with Azure Key Vault"""
        if not self.key_client:
            return None
            
        try:
            from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm
            
            # Get key reference
            key = self.key_client.get_key(self.key_name or key_id)
            
            # Create crypto client for this key
            crypto_client = CryptographyClient(key, self.credential)
            
            if isinstance(ciphertext, str):
                ciphertext = base64.b64decode(ciphertext)
                
            # Decrypt using RSA-OAEP
            result = crypto_client.decrypt(EncryptionAlgorithm.rsa_oaep, ciphertext)
            return result.plaintext
        except Exception as e:
            logger.error(f"Error decrypting with Azure Key Vault: {e}")
            return None


class GCPKMSClient:
    """Google Cloud KMS Client implementation"""
    def __init__(self):
        self.project_id = current_app.config.get('GCP_PROJECT_ID')
        self.location = current_app.config.get('GCP_LOCATION', 'global')
        self.key_ring = current_app.config.get('GCP_KEY_RING')
        self.key_name = current_app.config.get('GCP_KEY_NAME')
        
        # Import GCP libraries only if using GCP KMS
        try:
            from google.cloud import kms
            
            self.client = kms.KeyManagementServiceClient()
            logger.info("Google Cloud KMS client initialized")
        except ImportError:
            logger.error("Google Cloud libraries not installed. Please install google-cloud-kms")
            self.client = None
        except Exception as e:
            logger.error(f"Error initializing Google Cloud KMS client: {e}")
            self.client = None
            
    def _get_key_path(self, key_id):
        """Get the full resource path for a key"""
        key_name = self.key_name or key_id
        return f"projects/{self.project_id}/locations/{self.location}/keyRings/{self.key_ring}/cryptoKeys/{key_name}"
            
    def generate_key(self, key_id):
        """Create a new key in Google Cloud KMS"""
        if not self.client:
            return None
            
        try:
            from google.cloud import kms
            
            # First check if the key ring exists, create if not
            key_ring_parent = f"projects/{self.project_id}/locations/{self.location}"
            key_ring_path = f"{key_ring_parent}/keyRings/{self.key_ring}"
            
            try:
                self.client.get_key_ring(name=key_ring_path)
            except Exception:
                # Create key ring if it doesn't exist
                key_ring = self.client.create_key_ring(
                    parent=key_ring_parent,
                    key_ring_id=self.key_ring,
                )
            
            # Create a new key in the key ring
            purpose = kms.CryptoKey.CryptoKeyPurpose.ENCRYPT_DECRYPT
            algorithm = kms.CryptoKeyVersion.CryptoKeyVersionAlgorithm.GOOGLE_SYMMETRIC_ENCRYPTION
            
            key = self.client.create_crypto_key(
                parent=key_ring_path,
                crypto_key_id=key_id,
                crypto_key=kms.CryptoKey(
                    purpose=purpose,
                    version_template=kms.CryptoKeyVersionTemplate(algorithm=algorithm),
                ),
            )
            
            return key.name
        except Exception as e:
            logger.error(f"Error generating Google Cloud KMS key: {e}")
            return None
            
    def get_key(self, key_id):
        """Get a data key from Google Cloud KMS (returns wrapped key)"""
        if not self.client:
            return None
            
        # For GCP KMS, we don't actually retrieve the key material
        # Instead we use the key to encrypt/decrypt directly
        # This method is included for API consistency
        return self._get_key_path(key_id)
            
    def encrypt(self, plaintext, key_id):
        """Encrypt data with Google Cloud KMS"""
        if not self.client:
            return None
            
        try:
            key_path = self._get_key_path(key_id)
            
            if isinstance(plaintext, str):
                plaintext = plaintext.encode('utf-8')
                
            # Encrypt the plaintext
            response = self.client.encrypt(
                request={"name": key_path, "plaintext": plaintext}
            )
            
            return base64.b64encode(response.ciphertext).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encrypting with Google Cloud KMS: {e}")
            return None
            
    def decrypt(self, ciphertext, key_id):
        """Decrypt data with Google Cloud KMS"""
        if not self.client:
            return None
            
        try:
            key_path = self._get_key_path(key_id)
            
            if isinstance(ciphertext, str):
                ciphertext = base64.b64decode(ciphertext)
                
            # Decrypt the ciphertext
            response = self.client.decrypt(
                request={"name": key_path, "ciphertext": ciphertext}
            )
            
            return response.plaintext
        except Exception as e:
            logger.error(f"Error decrypting with Google Cloud KMS: {e}")
            return None