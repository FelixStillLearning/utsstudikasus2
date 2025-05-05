from app.data.models import HealthData
from app.crypto.aes import encrypt_health_data, decrypt_health_data, encrypt_dna_data, decrypt_dna_data
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthDataRepository:
    """
    Repository for handling health and DNA data with encryption.
    All sensitive data is encrypted with AES-256 before storage.
    """
    def __init__(self, db_session):
        self.db_session = db_session
        logger.info("HealthDataRepository initialized")

    def save_health_data(self, user_id, data_type, raw_data):
        """
        Save health data with encryption.
        
        Args:
            user_id: ID of the user this data belongs to
            data_type: Type of health data (e.g., 'medical_record', 'lab_result')
            raw_data: The raw health data to encrypt and store
        
        Returns:
            ID of the saved health data record
        """
        logger.info(f"Saving health data for user {user_id}, type: {data_type}")
        
        # Convert data to JSON string if it's a dict
        if isinstance(raw_data, dict):
            raw_data = json.dumps(raw_data)
            
        # Encrypt the data using AES-256
        encrypted_data = encrypt_health_data(raw_data)
        
        # Store as JSON string
        encrypted_json = json.dumps(encrypted_data)
        
        # Create new health data record
        health_data = HealthData(
            user_id=user_id,
            data_type=data_type,
            encrypted_data=encrypted_json
        )
        
        # Save to database
        self.db_session.add(health_data)
        self.db_session.commit()
        
        logger.info(f"Health data saved with ID: {health_data.id}")
        return health_data.id

    def save_dna_data(self, user_id, raw_data, data_type='dna_analysis'):
        """
        Save DNA data with dedicated encryption.
        
        Args:
            user_id: ID of the user this DNA data belongs to
            raw_data: The raw DNA data to encrypt and store
            data_type: Type of DNA data (default: 'dna_analysis')
            
        Returns:
            ID of the saved DNA data record
        """
        logger.info(f"Saving DNA data for user {user_id}")
        
        # Convert data to JSON string if it's a dict
        if isinstance(raw_data, dict):
            raw_data = json.dumps(raw_data)
            
        # Encrypt the DNA data using dedicated DNA key
        encrypted_data = encrypt_dna_data(raw_data)
        
        # Store as JSON string
        encrypted_json = json.dumps(encrypted_data)
        
        # Create new health data record with DNA type
        dna_data = HealthData(
            user_id=user_id,
            data_type=data_type,
            encrypted_data=encrypted_json
        )
        
        # Save to database
        self.db_session.add(dna_data)
        self.db_session.commit()
        
        logger.info(f"DNA data saved with ID: {dna_data.id}")
        return dna_data.id

    def get_health_data(self, data_id):
        """
        Retrieve and decrypt health data from the database.
        
        Args:
            data_id: ID of the health data record to retrieve
            
        Returns:
            Decrypted health data
        """
        logger.info(f"Retrieving health data with ID: {data_id}")
        
        # Get encrypted data from database
        health_data = self.db_session.query(HealthData).filter_by(id=data_id).first()
        
        if not health_data:
            logger.warning(f"No health data found with ID: {data_id}")
            return None
            
        # Parse the stored JSON
        encrypted_data = json.loads(health_data.encrypted_data)
        
        # Decrypt based on data type
        if 'dna' in health_data.data_type.lower():
            decrypted_data = decrypt_dna_data(encrypted_data)
        else:
            decrypted_data = decrypt_health_data(encrypted_data)
            
        # Try to parse as JSON if it looks like it
        try:
            if decrypted_data.startswith('{') and decrypted_data.endswith('}'):
                return json.loads(decrypted_data)
        except:
            pass
            
        return decrypted_data

    def get_user_health_data(self, user_id, data_type=None):
        """
        Get all health data for a specific user, optionally filtered by type.
        
        Args:
            user_id: ID of the user
            data_type: Optional data type to filter by
            
        Returns:
            List of decrypted health data records
        """
        logger.info(f"Retrieving health data for user: {user_id}")
        
        # Build query
        query = self.db_session.query(HealthData).filter_by(user_id=user_id)
        
        # Apply data type filter if provided
        if data_type:
            query = query.filter_by(data_type=data_type)
            
        # Get results
        health_data_records = query.all()
        
        # Decrypt all records
        result = []
        for record in health_data_records:
            decrypted_data = self.get_health_data(record.id)
            result.append({
                'id': record.id,
                'data_type': record.data_type,
                'data': decrypted_data
            })
            
        return result

    def delete_health_data(self, data_id):
        """
        Delete health data from the database.
        
        Args:
            data_id: ID of the health data to delete
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Deleting health data with ID: {data_id}")
        
        # Find the record
        health_data = self.db_session.query(HealthData).filter_by(id=data_id).first()
        
        if not health_data:
            logger.warning(f"No health data found with ID: {data_id}")
            return False
            
        # Delete from database
        self.db_session.delete(health_data)
        self.db_session.commit()
        
        logger.info(f"Health data with ID {data_id} deleted successfully")
        return True