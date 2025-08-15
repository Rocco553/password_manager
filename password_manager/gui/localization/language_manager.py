import json
import os
from pathlib import Path


class LanguageManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        
        self.initialized = True
        self.current_language = 'en'
        self.strings = {}
        self.language_file = Path("data/language.json")
        self.language_file.parent.mkdir(exist_ok=True)
        
        self._load_language_preference()
        self._load_strings()
    
    def _load_language_preference(self):
        try:
            if self.language_file.exists():
                with open(self.language_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_language = data.get('language', 'en')
        except:
            self.current_language = 'en'
    
    def _save_language_preference(self):
        try:
            with open(self.language_file, 'w', encoding='utf-8') as f:
                json.dump({'language': self.current_language}, f, ensure_ascii=False)
        except:
            pass
    
    def _load_strings(self):
        try:
            if self.current_language == 'de':
                from gui.localization.strings_de import STRINGS
            else:
                from gui.localization.strings_en import STRINGS
            
            self.strings = STRINGS
        except ImportError:
            from gui.localization.strings_en import STRINGS
            self.strings = STRINGS
            self.current_language = 'en'
    
    def get(self, key, default=None):
        return self.strings.get(key, default or key)
    
    def set_language(self, language_code):
        if language_code in ['en', 'de']:
            self.current_language = language_code
            self._save_language_preference()
            self._load_strings()
            return True
        return False
    
    def get_current_language(self):
        return self.current_language
    
    def get_language_name(self):
        names = {
            'en': 'English',
            'de': 'Deutsch'
        }
        return names.get(self.current_language, 'English')
    
    def get_available_languages(self):
        return [
            ('en', 'English'),
            ('de', 'Deutsch')
        ]


def _(key, default=None):
    return LanguageManager().get(key, default)