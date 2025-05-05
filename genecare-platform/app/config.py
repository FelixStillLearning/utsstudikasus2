import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_default_secret_key'
    # Change DATABASE_URI to SQLALCHEMY_DATABASE_URI for Flask-SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking for better performance
    AES_KEY = os.environ.get('AES_KEY') or 'a_default_aes_key_32_bytes_long'  # Must be 32 bytes for AES-256
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'