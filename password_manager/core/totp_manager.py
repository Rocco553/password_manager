import pyotp
import qrcode
from io import BytesIO
import base64
from PIL import Image, ImageTk
import secrets


class TOTPManager:
    def __init__(self):
        pass
    
    def generate_secret(self):
        return pyotp.random_base32()
    
    def generate_qr_code(self, secret, account_name, issuer="Password Manager"):
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=account_name,
            issuer_name=issuer
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        return img
    
    def get_current_totp(self, secret):
        """✅ FIXED: Entfernte alle Debug-Ausgaben"""
        if not secret or not secret.strip():
            return None, 0
        
        try:
            secret = secret.strip().replace(' ', '').upper()
            
            if len(secret) < 16:
                return None, 0
            
            totp = pyotp.TOTP(secret)
            current_code = totp.now()
            
            import time
            remaining_time = 30 - int(time.time() % 30)
            
            return current_code, remaining_time
            
        except Exception:
            # ✅ FIXED: Keine Debug-Ausgaben mehr
            return None, 0
    
    def verify_totp(self, secret, token):
        if not secret or not token:
            return False
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token)
        except:
            return False
    
    def generate_backup_codes(self, count=10):
        codes = []
        for _ in range(count):
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            codes.append(formatted_code)
        return codes