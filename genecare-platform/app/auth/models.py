from flask_sqlalchemy import SQLAlchemy
from app.crypto.aes import encrypt, decrypt

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)  # Store hashed password
    email = db.Column(db.String(120), unique=True, nullable=True)  # Added email field

    def set_password(self, password):
        self.password = encrypt(password)

    def check_password(self, password):
        return decrypt(self.password) == password