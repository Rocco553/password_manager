import json
import os
from pathlib import Path


class SettingsManager:
    def __init__(self):
        self.settings_file = Path("data/settings.json")
        self.settings_file.parent.mkdir(exist_ok=True)
        self.settings = self._load_default_settings()
        self.load_settings()
    
    def _load_default_settings(self):
        return {
            "auto_lock_enabled": True,
            "auto_lock_timeout_minutes": 0.75,
            "auto_lock_warning_seconds": 15,
            "clipboard_clear_enabled": True,
            "clipboard_clear_seconds": 10,
            "theme": "windows_classic",
            "remember_last_database": True,
            "show_splash_screen": False,
            "start_minimized": False,
            "show_password_strength": True,
            "require_password_confirmation": True,
            "backup_on_save": False,
            "window_width": 800,
            "window_height": 600,
            "show_status_bar": True,
            "show_toolbar_icons": True
        }
    
    def load_settings(self):
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
        except Exception as e:
            print(f"Fehler beim Laden der Einstellungen: {e}")
    
    def save_settings(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern der Einstellungen: {e}")
    
    def get(self, key, default=None):
        return self.settings.get(key, default)
    
    def set(self, key, value):
        self.settings[key] = value
    
    def get_auto_lock_timeout_seconds(self):
        return self.get("auto_lock_timeout_minutes") * 60
    
    def reset_to_defaults(self):
        self.settings = self._load_default_settings()
        self.save_settings()
    
    def export_settings(self, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Export-Fehler: {e}")
            return False
    
    def import_settings(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
                defaults = self._load_default_settings()
                for key, value in imported_settings.items():
                    if key in defaults:
                        self.settings[key] = value
            self.save_settings()
            return True
        except Exception as e:
            print(f"Import-Fehler: {e}")
            return False