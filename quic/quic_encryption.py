from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os


class QuicEncryption:
    def __init__(self, key):
        self.key = key
        self.backend = default_backend()
        self.block_size = 128

    def encrypt(self, plaintext):
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CFB(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        padded_plaintext = self._pad(plaintext)
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        return iv + ciphertext

    def decrypt(self, ciphertext):
        iv = ciphertext[:16]
        cipher = Cipher(algorithms.AES(self.key), modes.CFB(iv), backend=self.backend)
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext[16:]) + decryptor.finalize()
        plaintext = self._unpad(padded_plaintext)
        return plaintext

    def _pad(self, data):
        padder = padding.PKCS7(self.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()
        return padded_data

    def _unpad(self, padded_data):
        unpadder = padding.PKCS7(self.block_size).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        return data