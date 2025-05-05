from flask_sqlalchemy import SQLAlchemy
from app.crypto.aes import encrypt, decrypt

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.LargeBinary, nullable=False)

    def set_password(self, password):
        self.password_hash = encrypt(password)

    def check_password(self, password):
        return decrypt(self.password_hash) == password