from app.crypto.aes import encrypt, decrypt

class HealthDataRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    def save_health_data(self, health_data):
        encrypted_data = encrypt(health_data)
        # Code to save encrypted_data to the database
        self.db_session.add(encrypted_data)
        self.db_session.commit()

    def get_health_data(self, data_id):
        # Code to retrieve encrypted_data from the database using data_id
        encrypted_data = self.db_session.query(HealthData).filter_by(id=data_id).first()
        if encrypted_data:
            return decrypt(encrypted_data)
        return None

    def delete_health_data(self, data_id):
        # Code to delete health data from the database
        health_data = self.db_session.query(HealthData).filter_by(id=data_id).first()
        if health_data:
            self.db_session.delete(health_data)
            self.db_session.commit()