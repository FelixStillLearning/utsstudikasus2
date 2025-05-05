from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os
import base64

class AESCipher:
    def __init__(self, key):
        self.key = key.ljust(32)[:32].encode('utf-8')  # Ensure key is 32 bytes

    def encrypt(self, raw):
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(raw.encode('utf-8'), AES.block_size))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        return iv, ct

    def decrypt(self, iv, ct):
        iv = base64.b64decode(iv)
        ct = base64.b64decode(ct)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode('utf-8')

def encrypt(key, raw):
    cipher = AESCipher(key)
    return cipher.encrypt(raw)

def decrypt(key, iv, ct):
    cipher = AESCipher(key)
    return cipher.decrypt(iv, ct)

encrypt_data = encrypt
decrypt_data = decrypt