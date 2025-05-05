from app.crypto.aes import AESCipher
from app.extensions import db  # Import the shared db instance
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'  # Changed from 'users' to 'user' to match SQLAlchemy's default convention
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)  # Store hashed password
    email = db.Column(db.String(120), unique=True, nullable=True)  # Added email field

    def set_password(self, password):
        # Use the AESCipher class to encrypt the password
        cipher = AESCipher(key_id='user_password_key')
        encrypted_data = cipher.encrypt(password)
        self.password = str(encrypted_data)  # Convert to string for storage

    def check_password(self, password):
        # Decrypt the stored password and compare
        try:
            import json
            # Convert stored string back to dictionary
            encrypted_data = json.loads(self.password.replace("'", '"'))
            cipher = AESCipher(key_id='user_password_key')
            decrypted = cipher.decrypt(encrypted_data)
            return decrypted == password
        except Exception as e:
            print(f"Password check error: {e}")
            return False