"""
Backup Manager für den Passwort-Manager
Verwaltet Backups, Export und Import von Datenbanken
"""

import json
import os
import shutil
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import zipfile
from core.encryption import PasswordEncryption


class BackupManager:
    """Verwaltet alle Backup- und Export-Funktionen"""
    
    def __init__(self, password_manager, settings_manager):
        self.pm = password_manager
        self.settings_manager = settings_manager
        
        # Backup-Verzeichnisse
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        self.export_dir = Path("exports")
        self.export_dir.mkdir(exist_ok=True)
    
    # ✅ BACKUP-FUNKTIONEN
    
    def create_encrypted_backup(self, backup_path: str = None) -> tuple[bool, str]:
        """Erstellt ein verschlüsseltes Backup der aktuellen Datenbank"""
        try:
            if not self.pm.is_unlocked:
                return False, "Datenbank ist nicht entsperrt"
            
            # Standard-Pfad generieren falls nicht angegeben
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                db_name = Path(self.pm.database_file).stem if self.pm.database_file else "database"
                backup_path = self.backup_dir / f"{db_name}_backup_{timestamp}.bak"
            
            # Kopiere die aktuelle Datenbank-Datei
            if os.path.exists(self.pm.database_file):
                shutil.copy2(self.pm.database_file, backup_path)
                
                # Erstelle Backup-Info
                info_file = str(backup_path).replace('.bak', '.info')
                self._create_backup_info(info_file, backup_path)
                
                return True, f"Backup erstellt: {backup_path}"
            else:
                return False, "Quelldatenbank nicht gefunden"
                
        except Exception as e:
            return False, f"Backup-Fehler: {str(e)}"
    
    def restore_from_backup(self, backup_path: str, target_path: str = None) -> tuple[bool, str]:
        """Stellt eine Datenbank aus einem Backup wieder her"""
        try:
            if not os.path.exists(backup_path):
                return False, "Backup-Datei nicht gefunden"
            
            # Ziel-Pfad bestimmen
            if not target_path:
                target_path = self.pm.database_file
            
            # Backup der aktuellen Datei (falls vorhanden)
            if os.path.exists(target_path):
                backup_current = f"{target_path}.pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(target_path, backup_current)
            
            # Wiederherstellen
            shutil.copy2(backup_path, target_path)
            
            return True, f"Backup wiederhergestellt: {target_path}"
            
        except Exception as e:
            return False, f"Wiederherstellungs-Fehler: {str(e)}"
    
    def list_backups(self) -> List[Dict]:
        """Listet alle verfügbaren Backups auf"""
        backups = []
        
        try:
            for backup_file in self.backup_dir.glob("*.bak"):
                info_file = str(backup_file).replace('.bak', '.info')
                
                backup_info = {
                    'file': backup_file,
                    'name': backup_file.stem,
                    'size': backup_file.stat().st_size,
                    'created': datetime.fromtimestamp(backup_file.stat().st_mtime),
                    'info': self._load_backup_info(info_file) if os.path.exists(info_file) else {}
                }
                
                backups.append(backup_info)
            
            # Sortiere nach Erstellungsdatum (neueste zuerst)
            backups.sort(key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            print(f"⚠️ Fehler beim Auflisten der Backups: {e}")
        
        return backups
    
    def delete_backup(self, backup_path: str) -> tuple[bool, str]:
        """Löscht ein Backup"""
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
                
                # Lösche auch Info-Datei
                info_file = str(backup_path).replace('.bak', '.info')
                if os.path.exists(info_file):
                    os.remove(info_file)
                
                return True, "Backup gelöscht"
            else:
                return False, "Backup-Datei nicht gefunden"
                
        except Exception as e:
            return False, f"Lösch-Fehler: {str(e)}"
    
    # ✅ EXPORT-FUNKTIONEN
    
    def export_to_csv(self, export_path: str, include_passwords: bool = True) -> tuple[bool, str]:
        """Exportiert Passwörter zu CSV"""
        try:
            if not self.pm.is_unlocked:
                return False, "Datenbank ist nicht entsperrt"
            
            entries = self.pm.list_entries()
            
            with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['title', 'username', 'password', 'url', 'notes', 'created', 'modified']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for entry in entries:
                    row = {
                        'title': entry.title,
                        'username': entry.username,
                        'password': entry.password if include_passwords else '***HIDDEN***',
                        'url': entry.url,
                        'notes': entry.notes,
                        'created': entry.created,
                        'modified': entry.modified
                    }
                    writer.writerow(row)
            
            return True, f"CSV-Export erstellt: {export_path}"
            
        except Exception as e:
            return False, f"CSV-Export-Fehler: {str(e)}"
    
    def export_to_json(self, export_path: str, include_passwords: bool = True) -> tuple[bool, str]:
        """Exportiert Passwörter zu JSON"""
        try:
            if not self.pm.is_unlocked:
                return False, "Datenbank ist nicht entsperrt"
            
            entries = self.pm.list_entries()
            
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'source': 'Password Manager',
                'version': '1.0',
                'entry_count': len(entries),
                'entries': []
            }
            
            for entry in entries:
                entry_data = {
                    'title': entry.title,
                    'username': entry.username,
                    'password': entry.password if include_passwords else '***HIDDEN***',
                    'url': entry.url,
                    'notes': entry.notes,
                    'created': entry.created,
                    'modified': entry.modified
                }
                export_data['entries'].append(entry_data)
            
            with open(export_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
            
            return True, f"JSON-Export erstellt: {export_path}"
            
        except Exception as e:
            return False, f"JSON-Export-Fehler: {str(e)}"
    
    def create_complete_backup_archive(self, archive_path: str) -> tuple[bool, str]:
        """Erstellt ein komplettes Backup-Archiv mit Datenbank und Einstellungen"""
        try:
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Datenbank hinzufügen
                if os.path.exists(self.pm.database_file):
                    zipf.write(self.pm.database_file, 'database.enc')
                
                # Einstellungen hinzufügen
                if os.path.exists(self.settings_manager.settings_file):
                    zipf.write(self.settings_manager.settings_file, 'settings.json')
                
                # Archive-Info hinzufügen
                archive_info = {
                    'created_at': datetime.now().isoformat(),
                    'app_version': '1.0',
                    'contains': ['database', 'settings']
                }
                
                zipf.writestr('archive_info.json', json.dumps(archive_info, indent=2))
            
            return True, f"Vollständiges Backup erstellt: {archive_path}"
            
        except Exception as e:
            return False, f"Archiv-Fehler: {str(e)}"
    
    # ✅ IMPORT-FUNKTIONEN
    
    def import_from_csv(self, csv_path: str, merge_mode: bool = True) -> tuple[bool, str, List[Dict]]:
        """Importiert Passwörter aus CSV"""
        try:
            if not self.pm.is_unlocked:
                return False, "Datenbank ist nicht entsperrt", []
            
            imported_entries = []
            conflicts = []
            
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    title = row.get('title', '').strip()
                    if not title:
                        continue
                    
                    # Prüfe auf Konflikte
                    existing_entry = self.pm.get_entry(title)
                    if existing_entry and not merge_mode:
                        conflicts.append({
                            'title': title,
                            'action': 'skipped',
                            'reason': 'Eintrag existiert bereits'
                        })
                        continue
                    
                    # Importiere Eintrag
                    success = self.pm.add_entry(
                        title=title,
                        username=row.get('username', ''),
                        password=row.get('password', ''),
                        url=row.get('url', ''),
                        notes=row.get('notes', '')
                    )
                    
                    if success:
                        imported_entries.append(row)
                    else:
                        conflicts.append({
                            'title': title,
                            'action': 'failed',
                            'reason': 'Konnte nicht hinzugefügt werden'
                        })
            
            result_msg = f"CSV-Import: {len(imported_entries)} Einträge importiert"
            if conflicts:
                result_msg += f", {len(conflicts)} Konflikte"
            
            return True, result_msg, conflicts
            
        except Exception as e:
            return False, f"CSV-Import-Fehler: {str(e)}", []
    
    # ✅ AUTO-BACKUP
    
    def create_auto_backup(self) -> tuple[bool, str]:
        """Erstellt automatisches Backup beim Speichern"""
        if not self.settings_manager.get("backup_on_save", False):
            return True, "Auto-Backup deaktiviert"
        
        try:
            # Altes Auto-Backup löschen (nur eines behalten)
            auto_backup_pattern = self.backup_dir.glob("*_auto.bak")
            for old_backup in auto_backup_pattern:
                try:
                    old_backup.unlink()
                except:
                    pass
            
            # Neues Auto-Backup erstellen
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            db_name = Path(self.pm.database_file).stem if self.pm.database_file else "database"
            auto_backup_path = self.backup_dir / f"{db_name}_auto.bak"
            
            return self.create_encrypted_backup(str(auto_backup_path))
            
        except Exception as e:
            return False, f"Auto-Backup-Fehler: {str(e)}"
    
    # ✅ HILFSFUNKTIONEN
    
    def _create_backup_info(self, info_file: str, backup_path: str):
        """Erstellt Info-Datei für Backup"""
        try:
            info = {
                'created_at': datetime.now().isoformat(),
                'original_db': self.pm.database_file,
                'backup_path': str(backup_path),
                'file_size': os.path.getsize(backup_path),
                'app_version': '1.0'
            }
            
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(info, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Fehler beim Erstellen der Backup-Info: {e}")
    
    def _load_backup_info(self, info_file: str) -> Dict:
        """Lädt Info-Datei für Backup"""
        try:
            with open(info_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def get_backup_statistics(self) -> Dict:
        """Gibt Backup-Statistiken zurück"""
        backups = self.list_backups()
        
        total_size = sum(backup['size'] for backup in backups)
        
        return {
            'total_backups': len(backups),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'latest_backup': backups[0]['created'] if backups else None,
            'auto_backup_enabled': self.settings_manager.get("backup_on_save", False)
        }