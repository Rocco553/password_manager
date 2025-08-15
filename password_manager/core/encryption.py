import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

class PasswordEncryption:
    def __init__(self):
        self.fernet = None
        self.salt = None
    
    def generate_key_from_password(self, master_password: str, salt: bytes = None) -> bytes:
        if salt is None:
            salt = os.urandom(16)
        
        self.salt = salt
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        return key
    
    def setup_encryption(self, master_password: str, salt: bytes = None):
        key = self.generate_key_from_password(master_password, salt)
        self.fernet = Fernet(key)
    
    def encrypt_data(self, data: str) -> bytes:
        if not self.fernet:
            raise ValueError("Verschlüsselung nicht initialisiert!")
        
        encrypted_data = self.fernet.encrypt(data.encode())
        return encrypted_data
    
    def decrypt_data(self, encrypted_data: bytes) -> str:
        if not self.fernet:
            raise ValueError("Verschlüsselung nicht initialisiert!")
        
        try:
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError("Entschlüsselung fehlgeschlagen. Falsches Passwort?") from e
    
    def get_salt(self) -> bytes:
        return self.salt