import json
import os
from datetime import datetime
from typing import List, Optional
from core.encryption import PasswordEncryption

class PasswordEntry:
    def __init__(self, title: str, username: str, password: str, url: str = "", notes: str = "", totp_secret: str = "", category: str = "Other"):
        self.title = title
        self.username = username
        self.password = password
        self.url = url
        self.notes = notes
        self.totp_secret = totp_secret
        self.category = category
        self.created = datetime.now().isoformat()
        self.modified = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'username': self.username,
            'password': self.password,
            'url': self.url,
            'notes': self.notes,
            'totp_secret': self.totp_secret,
            'category': self.category,
            'created': self.created,
            'modified': self.modified
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        entry = cls(
            title=data['title'],
            username=data['username'],
            password=data['password'],
            url=data.get('url', ''),
            notes=data.get('notes', ''),
            totp_secret=data.get('totp_secret', ''),
            category=data.get('category', 'Other')
        )
        entry.created = data.get('created', datetime.now().isoformat())
        entry.modified = data.get('modified', datetime.now().isoformat())
        return entry
    
    def update(self, title: str = None, username: str = None, password: str = None, 
               url: str = None, notes: str = None, totp_secret: str = None, category: str = None):
        if title is not None:
            self.title = title
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password
        if url is not None:
            self.url = url
        if notes is not None:
            self.notes = notes
        if totp_secret is not None:
            self.totp_secret = totp_secret
        if category is not None:
            self.category = category
        self.modified = datetime.now().isoformat()
    
    def has_totp(self):
        return bool(self.totp_secret.strip())
    
    def __str__(self):
        return f"🔒 {self.title} ({self.username})"


class PasswordManager:
    def __init__(self, database_file: str = "data/passwords.enc"):
        self.database_file = database_file
        self.encryptor = PasswordEncryption()
        self.entries: List[PasswordEntry] = []
        self.is_unlocked = False
        
        os.makedirs(os.path.dirname(database_file), exist_ok=True)
    
    def create_new_database(self, master_password: str):
        self.encryptor.setup_encryption(master_password)
        self.entries = []
        self.is_unlocked = True
        self.save_database()
    
    def unlock_database(self, master_password: str) -> bool:
        if not os.path.exists(self.database_file):
            return False
        
        try:
            with open(self.database_file, 'rb') as f:
                salt = f.read(16)
                encrypted_data = f.read()
            
            self.encryptor.setup_encryption(master_password, salt)
            
            decrypted_json = self.encryptor.decrypt_data(encrypted_data)
            data = json.loads(decrypted_json)
            
            self.entries = [PasswordEntry.from_dict(entry_data) for entry_data in data['entries']]
            self.is_unlocked = True
            
            return True
            
        except Exception:
            return False
    
    def save_database(self):
        if not self.is_unlocked:
            return
        
        try:
            data = {
                'version': '1.0',
                'created': datetime.now().isoformat(),
                'entries': [entry.to_dict() for entry in self.entries]
            }
            
            json_string = json.dumps(data, indent=2)
            encrypted_data = self.encryptor.encrypt_data(json_string)
            
            with open(self.database_file, 'wb') as f:
                f.write(self.encryptor.get_salt())
                f.write(encrypted_data)
            
        except Exception as e:
            print(f"Fehler beim Speichern: {str(e)}")
    
    def add_entry(self, title: str, username: str, password: str, url: str = "", notes: str = "", totp_secret: str = "", category: str = "Other") -> bool:
        if not self.is_unlocked:
            return False
        
        if any(entry.title.lower() == title.lower() for entry in self.entries):
            return False
        
        new_entry = PasswordEntry(title, username, password, url, notes, totp_secret, category)
        self.entries.append(new_entry)
        self.save_database()
        return True
    
    def get_entry(self, title: str) -> Optional[PasswordEntry]:
        if not self.is_unlocked:
            return None
        
        for entry in self.entries:
            if entry.title.lower() == title.lower():
                return entry
        return None
    
    def list_entries(self) -> List[PasswordEntry]:
        if not self.is_unlocked:
            return []
        return self.entries.copy()
    
    def get_entries_by_category(self, category: str) -> List[PasswordEntry]:
        if not self.is_unlocked:
            return []
        
        if category == "All":
            return self.entries.copy()
        
        return [entry for entry in self.entries if entry.category == category]
    
    def get_categories_with_counts(self) -> dict:
        if not self.is_unlocked:
            return {}
        
        categories = {}
        for entry in self.entries:
            category = entry.category or "Other"
            categories[category] = categories.get(category, 0) + 1
        
        return categories
    
    def delete_entry(self, title: str) -> bool:
        if not self.is_unlocked:
            return False
        
        for i, entry in enumerate(self.entries):
            if entry.title.lower() == title.lower():
                self.entries.pop(i)
                self.save_database()
                return True
        
        return False
    
    def lock_database(self):
        self.entries = []
        self.is_unlocked = False
        self.encryptor = PasswordEncryption()