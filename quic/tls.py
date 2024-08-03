from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os


class TLSContext:
    def __init__(self):
        self.key = os.urandom(32)  # 256-bit rand key
        self.iv = os.urandom(16)  # 128-bit init vector

    def handshake(self):
        """
        Initialize TLS handshake
        """
        pass

    def encrypt(self, data):
        """
        Encrypt data
        """
        cipher = Cipher(algorithms.AES(self.key), modes.GCM(self.iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(data) + encryptor.finalize()
        return self.iv + encryptor.tag + encrypted_data

    def decrypt(self, data):
        """
        Decrypt data
        """
        iv = data[:16]
        tag = data[16:32]
        encrypted_data = data[32:]
        cipher = Cipher(algorithms.AES(self.key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        return decrypted_data