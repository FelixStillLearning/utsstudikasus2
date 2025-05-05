import unittest
from app.crypto.aes import encrypt, decrypt
from app.crypto.key_management import generate_key

class TestCrypto(unittest.TestCase):

    def setUp(self):
        self.key = generate_key()
        self.data = "Sensitive Health Data"
        self.encrypted_data = encrypt(self.data, self.key)

    def test_encryption(self):
        self.assertNotEqual(self.data, self.encrypted_data)

    def test_decryption(self):
        decrypted_data = decrypt(self.encrypted_data, self.key)
        self.assertEqual(self.data, decrypted_data)

    def test_decryption_with_wrong_key(self):
        wrong_key = generate_key()
        with self.assertRaises(ValueError):
            decrypt(self.encrypted_data, wrong_key)

if __name__ == '__main__':
    unittest.main()