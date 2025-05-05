from sqlalchemy import Column, Integer, String, Text
from app.extensions import db  # Import the shared db instance

class HealthData(db.Model):
    __tablename__ = 'health_data'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    data_type = Column(String(50), nullable=False)
    encrypted_data = Column(Text, nullable=False)

    def __init__(self, user_id, data_type, encrypted_data):
        self.user_id = user_id
        self.data_type = data_type
        self.encrypted_data = encrypted_data

    def __repr__(self):
        return f'<HealthData {self.id} - {self.data_type}>'