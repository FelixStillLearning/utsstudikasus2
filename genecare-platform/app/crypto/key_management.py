from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

class KeyManager:
    def __init__(self, key_size=2048):
        self.key_size = key_size
        self.private_key = None
        self.public_key = None

    def generate_keys(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.key_size,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

    def save_private_key(self, file_path):
        if self.private_key is None:
            raise ValueError("Private key not generated.")
        with open(file_path, "wb") as f:
            f.write(self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
            ))

    def save_public_key(self, file_path):
        if self.public_key is None:
            raise ValueError("Public key not generated.")
        with open(file_path, "wb") as f:
            f.write(self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            ))

    def load_private_key(self, file_path):
        with open(file_path, "rb") as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )

    def load_public_key(self, file_path):
        with open(file_path, "rb") as f:
            self.public_key = serialization.load_pem_public_key(
                f.read(),
                backend=default_backend()
            )

    def get_private_key(self):
        return self.private_key

    def get_public_key(self):
        return self.public_key

def generate_key():
    key_manager = KeyManager()
    key_manager.generate_keys()
    return key_manager.get_private_key(), key_manager.get_public_key()

def load_key(private_key_path, public_key_path):
    key_manager = KeyManager()
    key_manager.load_private_key(private_key_path)
    key_manager.load_public_key(public_key_path)
    return key_manager.get_private_key(), key_manager.get_public_key()

# Example usage:
# key_manager = KeyManager()
# key_manager.generate_keys()
# key_manager.save_private_key("private_key.pem")
# key_manager.save_public_key("public_key.pem")