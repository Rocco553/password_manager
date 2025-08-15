"""
Backup & Export Dialog für den Passwort-Manager
Windows-klassisches Design mit Tab-System für alle Backup-Funktionen
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from pathlib import Path
from gui.modern_styles import (
    WindowsClassicStyles, WindowsClassicColors, 
    create_classic_frame, create_classic_label_frame, 
    create_classic_entry, ClassicSpacing
)


class BackupDialog:
    """Backup & Export Dialog mit Tab-System"""
    
    def __init__(self, parent, backup_manager):
        self.backup_manager = backup_manager
        
        WindowsClassicStyles.setup_windows_classic_theme()
        
        # Dialog erstellen
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Backup & Export")
        self.dialog.geometry("700x600")
        self.dialog.configure(bg=WindowsClassicColors.WINDOW_BG)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Zentrieren
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50, 
            parent.winfo_rooty() + 25
        ))
        
        self.dialog.focus_set()
        self.dialog.focus_force()
        
        self.create_backup_ui()
        self.load_backup_list()
        
        # Keyboard Navigation
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
        
        self.dialog.wait_window()
    
    def create_backup_ui(self):
        """Erstellt die Backup-UI"""
        # Hauptframe
        main_frame = create_classic_frame(self.dialog, WindowsClassicColors.DIALOG_BG)
        main_frame.pack(expand=True, fill='both', padx=12, pady=12)
        
        # Titel
        title_frame = create_classic_frame(main_frame, WindowsClassicColors.DIALOG_BG)
        title_frame.pack(fill='x', pady=(0, 16))
        
        icon_label = tk.Label(title_frame, text="💾", 
                             bg=WindowsClassicColors.DIALOG_BG, 
                             fg=WindowsClassicColors.ACCENT,
                             font=('Segoe UI', 16, 'normal'))
        icon_label.pack(side='left', padx=(0, 8))
        
        title_label = tk.Label(title_frame, text="Backup & Export", 
                              bg=WindowsClassicColors.DIALOG_BG, 
                              fg=WindowsClassicColors.TEXT_PRIMARY,
                              font=('Segoe UI', 14, 'bold'))
        title_label.pack(side='left')
        
        # Tab-System
        self.notebook = ttk.Notebook(main_frame, style='Classic.TNotebook')
        self.notebook.pack(expand=True, fill='both', pady=(0, 16))
        
        # Tabs erstellen
        self.create_backup_tab()
        self.create_export_tab()
        self.create_import_tab()
        
        # Schließen-Button
        self.create_close_button(main_frame)
    
    def create_backup_tab(self):
        """Erstellt den Backup-Tab"""
        backup_frame = create_classic_frame(self.notebook, WindowsClassicColors.WINDOW_BG)
        self.notebook.add(backup_frame, text='💾 Backup')
        
        # Schnell-Aktionen
        quick_frame = create_classic_label_frame(backup_frame, "⚡ Schnell-Aktionen")
        quick_frame.pack(fill='x', padx=8, pady=(8, 0))
        
        quick_container = create_classic_frame(quick_frame, WindowsClassicColors.WINDOW_BG)
        quick_container.pack(fill='x', padx=8, pady=8)
        
        # Backup-Buttons
        button_frame = create_classic_frame(quick_container, WindowsClassicColors.WINDOW_BG)
        button_frame.pack(fill='x', pady=4)
        
        create_backup_btn = tk.Button(button_frame, text="🔄 Backup erstellen", 
                                     command=self.create_backup,
                                     bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'bold'),
                                     relief='raised', bd=1, padx=15, pady=6)
        create_backup_btn.pack(side='left', padx=(0, 8))
        
        full_backup_btn = tk.Button(button_frame, text="📦 Vollständiges Backup", 
                                   command=self.create_full_backup,
                                   bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                                   relief='raised', bd=1, padx=15, pady=6)
        full_backup_btn.pack(side='left')
        
        # Backup-Liste
        list_frame = create_classic_label_frame(backup_frame, "📋 Verfügbare Backups")
        list_frame.pack(expand=True, fill='both', padx=8, pady=8)
        
        # TreeView für Backups
        tree_container = create_classic_frame(list_frame, WindowsClassicColors.WINDOW_BG, relief='sunken')
        tree_container.pack(expand=True, fill='both', padx=8, pady=8)
        
        self.backup_tree = ttk.Treeview(tree_container, 
                                       columns=('size', 'created'), 
                                       show='tree headings', 
                                       height=10,
                                       style='Classic.Treeview')
        
        self.backup_tree.heading('#0', text='📁 Backup-Name', anchor='w')
        self.backup_tree.heading('size', text='📏 Größe', anchor='w')
        self.backup_tree.heading('created', text='📅 Erstellt', anchor='w')
        
        self.backup_tree.column('#0', width=250)
        self.backup_tree.column('size', width=100)
        self.backup_tree.column('created', width=150)
        
        backup_scrollbar = ttk.Scrollbar(tree_container, orient='vertical', 
                                        command=self.backup_tree.yview)
        self.backup_tree.configure(yscrollcommand=backup_scrollbar.set)
        
        self.backup_tree.pack(side='left', expand=True, fill='both')
        backup_scrollbar.pack(side='right', fill='y')
        
        # Backup-Aktionen
        backup_actions = create_classic_frame(backup_frame, WindowsClassicColors.WINDOW_BG)
        backup_actions.pack(fill='x', padx=8, pady=(0, 8))
        
        restore_btn = tk.Button(backup_actions, text="↩️ Wiederherstellen", 
                               command=self.restore_backup,
                               bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                               relief='raised', bd=1, padx=12, pady=4)
        restore_btn.pack(side='left', padx=(0, 8))
        
        delete_backup_btn = tk.Button(backup_actions, text="🗑️ Löschen", 
                                     command=self.delete_backup,
                                     bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                                     relief='raised', bd=1, padx=12, pady=4)
        delete_backup_btn.pack(side='left', padx=8)
        
        refresh_btn = tk.Button(backup_actions, text="🔄 Aktualisieren", 
                               command=self.load_backup_list,
                               bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                               relief='raised', bd=1, padx=12, pady=4)
        refresh_btn.pack(side='right')
        
        # Hover-Effekte
        self._add_hover_effects([create_backup_btn, full_backup_btn, restore_btn, 
                               delete_backup_btn, refresh_btn])
    
    def create_export_tab(self):
        """Erstellt den Export-Tab"""
        export_frame = create_classic_frame(self.notebook, WindowsClassicColors.WINDOW_BG)
        self.notebook.add(export_frame, text='📤 Export')
        
        # Export-Optionen
        options_frame = create_classic_label_frame(export_frame, "⚙️ Export-Einstellungen")
        options_frame.pack(fill='x', padx=8, pady=8)
        
        options_container = create_classic_frame(options_frame, WindowsClassicColors.WINDOW_BG)
        options_container.pack(fill='x', padx=8, pady=8)
        
        # Passwörter einschließen
        self.include_passwords = tk.BooleanVar(value=True)
        pw_cb = tk.Checkbutton(options_container, text="🔑 Passwörter im Export einschließen",
                              variable=self.include_passwords,
                              bg=WindowsClassicColors.WINDOW_BG,
                              fg=WindowsClassicColors.TEXT_PRIMARY,
                              font=('Segoe UI', 9, 'normal'),
                              activebackground=WindowsClassicColors.WINDOW_BG,
                              selectcolor=WindowsClassicColors.INPUT_BG)
        pw_cb.pack(anchor='w', pady=4)
        
        # Warnung
        warning_label = tk.Label(options_container, 
                                text="⚠️ Achtung: Exportierte Dateien sind NICHT verschlüsselt!",
                                bg=WindowsClassicColors.WINDOW_BG,
                                fg=WindowsClassicColors.ERROR,
                                font=('Segoe UI', 8, 'italic'))
        warning_label.pack(anchor='w', pady=(8, 0))
        
        # Export-Buttons
        export_actions = create_classic_label_frame(export_frame, "📁 Export-Formate")
        export_actions.pack(fill='x', padx=8, pady=8)
        
        export_container = create_classic_frame(export_actions, WindowsClassicColors.WINDOW_BG)
        export_container.pack(fill='x', padx=8, pady=8)
        
        csv_btn = tk.Button(export_container, text="📊 CSV exportieren", 
                           command=self.export_csv,
                           bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                           relief='raised', bd=1, padx=15, pady=8)
        csv_btn.pack(fill='x', pady=(0, 8))
        
        json_btn = tk.Button(export_container, text="📋 JSON exportieren", 
                            command=self.export_json,
                            bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                            relief='raised', bd=1, padx=15, pady=8)
        json_btn.pack(fill='x')
        
        # Format-Infos
        info_frame = create_classic_label_frame(export_frame, "ℹ️ Format-Informationen")
        info_frame.pack(expand=True, fill='both', padx=8, pady=8)
        
        info_container = create_classic_frame(info_frame, WindowsClassicColors.INPUT_BG, relief='sunken')
        info_container.pack(expand=True, fill='both', padx=8, pady=8)
        
        info_text = tk.Text(info_container,
                           bg=WindowsClassicColors.INPUT_BG,
                           fg=WindowsClassicColors.TEXT_PRIMARY,
                           font=('Segoe UI', 9, 'normal'),
                           wrap='word', relief='flat', bd=0,
                           height=8, state='normal')
        info_text.pack(expand=True, fill='both', padx=4, pady=4)
        
        info_content = """📊 CSV-Format:
• Kompatibel mit Excel, LibreOffice
• Einfache Tabellen-Struktur
• Gut für Datenanalyse

📋 JSON-Format:
• Strukturierte Daten mit Metainformationen
• Gut für Entwickler und weitere Verarbeitung
• Behält alle Feldtypen bei

🔒 Sicherheitshinweis:
Exportierte Dateien sind im Klartext gespeichert! Löschen Sie sie nach der Verwendung oder speichern Sie sie an einem sicheren Ort."""
        
        info_text.insert('1.0', info_content)
        info_text.config(state='disabled')
        
        self._add_hover_effects([csv_btn, json_btn])
    
    def create_import_tab(self):
        """Erstellt den Import-Tab"""
        import_frame = create_classic_frame(self.notebook, WindowsClassicColors.WINDOW_BG)
        self.notebook.add(import_frame, text='📥 Import')
        
        # Import-Optionen
        options_frame = create_classic_label_frame(import_frame, "⚙️ Import-Einstellungen")
        options_frame.pack(fill='x', padx=8, pady=8)
        
        options_container = create_classic_frame(options_frame, WindowsClassicColors.WINDOW_BG)
        options_container.pack(fill='x', padx=8, pady=8)
        
        # Merge-Modus
        self.merge_mode = tk.BooleanVar(value=True)
        merge_cb = tk.Checkbutton(options_container, text="🔄 Bestehende Einträge überschreiben",
                                 variable=self.merge_mode,
                                 bg=WindowsClassicColors.WINDOW_BG,
                                 fg=WindowsClassicColors.TEXT_PRIMARY,
                                 font=('Segoe UI', 9, 'normal'),
                                 activebackground=WindowsClassicColors.WINDOW_BG,
                                 selectcolor=WindowsClassicColors.INPUT_BG)
        merge_cb.pack(anchor='w', pady=4)
        
        info_label = tk.Label(options_container, 
                             text="ℹ️ Deaktiviert: Doppelte Einträge werden übersprungen",
                             bg=WindowsClassicColors.WINDOW_BG,
                             fg=WindowsClassicColors.TEXT_SECONDARY,
                             font=('Segoe UI', 8, 'italic'))
        info_label.pack(anchor='w', pady=(0, 8))
        
        # Import-Buttons
        import_actions = create_classic_label_frame(import_frame, "📁 Import-Quellen")
        import_actions.pack(fill='x', padx=8, pady=8)
        
        import_container = create_classic_frame(import_actions, WindowsClassicColors.WINDOW_BG)
        import_container.pack(fill='x', padx=8, pady=8)
        
        csv_import_btn = tk.Button(import_container, text="📊 CSV importieren", 
                                  command=self.import_csv,
                                  bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                                  relief='raised', bd=1, padx=15, pady=8)
        csv_import_btn.pack(fill='x', pady=(0, 8))
        
        backup_restore_btn = tk.Button(import_container, text="💾 Backup wiederherstellen", 
                                      command=self.restore_backup_file,
                                      bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                                      relief='raised', bd=1, padx=15, pady=8)
        backup_restore_btn.pack(fill='x')
        
        # Import-Vorschau
        preview_frame = create_classic_label_frame(import_frame, "👁️ Import-Vorschau")
        preview_frame.pack(expand=True, fill='both', padx=8, pady=8)
        
        preview_container = create_classic_frame(preview_frame, WindowsClassicColors.WINDOW_BG, relief='sunken')
        preview_container.pack(expand=True, fill='both', padx=8, pady=8)
        
        self.preview_text = tk.Text(preview_container,
                                   bg=WindowsClassicColors.INPUT_BG,
                                   fg=WindowsClassicColors.TEXT_PRIMARY,
                                   font=('Courier New', 8, 'normal'),
                                   wrap='word', relief='flat', bd=0,
                                   height=10, state='disabled')
        
        preview_scrollbar = tk.Scrollbar(preview_container, orient='vertical', 
                                        command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_text.pack(side='left', expand=True, fill='both')
        preview_scrollbar.pack(side='right', fill='y')
        
        self._add_hover_effects([csv_import_btn, backup_restore_btn])
    
    def create_close_button(self, parent):
        """Erstellt den Schließen-Button"""
        button_frame = create_classic_frame(parent, WindowsClassicColors.DIALOG_BG)
        button_frame.pack(fill='x')
        
        # Links: Statistiken
        stats = self.backup_manager.get_backup_statistics()
        stats_text = f"💾 {stats['total_backups']} Backups • {stats['total_size_mb']} MB"
        
        stats_label = tk.Label(button_frame, text=stats_text,
                              bg=WindowsClassicColors.DIALOG_BG,
                              fg=WindowsClassicColors.TEXT_SECONDARY,
                              font=('Segoe UI', 8, 'normal'))
        stats_label.pack(side='left', anchor='w')
        
        # Rechts: Schließen-Button
        close_btn = tk.Button(button_frame, text="Schließen", 
                             command=self.dialog.destroy,
                             bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                             relief='raised', bd=1, padx=20, pady=6, width=10)
        close_btn.pack(side='right')
        
        self._add_hover_effects([close_btn])
    
    def _add_hover_effects(self, buttons):
        """Fügt Hover-Effekte zu Buttons hinzu"""
        def create_hover_effect(button):
            def on_enter(event):
                button.config(bg='#d5d5d5')
            def on_leave(event):
                button.config(bg='#e1e1e1')
            button.bind('<Enter>', on_enter)
            button.bind('<Leave>', on_leave)
        
        for btn in buttons:
            create_hover_effect(btn)
    
    # ✅ BACKUP-AKTIONEN
    
    def load_backup_list(self):
        """Lädt die Liste der verfügbaren Backups"""
        # Lösche alte Einträge
        for item in self.backup_tree.get_children():
            self.backup_tree.delete(item)
        
        backups = self.backup_manager.list_backups()
        
        for backup in backups:
            size_mb = round(backup['size'] / (1024 * 1024), 2)
            size_str = f"{size_mb} MB" if size_mb > 0 else "< 1 MB"
            
            created_str = backup['created'].strftime("%d.%m.%Y %H:%M")
            
            self.backup_tree.insert('', 'end', text=backup['name'],
                                   values=(size_str, created_str))
    
    def create_backup(self):
        """Erstellt ein neues Backup"""
        success, message = self.backup_manager.create_encrypted_backup()
        
        if success:
            messagebox.showinfo("Backup", message)
            self.load_backup_list()  # Liste aktualisieren
        else:
            messagebox.showerror("Backup-Fehler", message)
    
    def create_full_backup(self):
        """Erstellt ein vollständiges Backup-Archiv"""
        file_path = filedialog.asksaveasfilename(
            title="Vollständiges Backup speichern",
            defaultextension=".zip",
            filetypes=[("ZIP Archive", "*.zip"), ("Alle Dateien", "*.*")]
        )
        
        if file_path:
            success, message = self.backup_manager.create_complete_backup_archive(file_path)
            
            if success:
                messagebox.showinfo("Vollständiges Backup", message)
            else:
                messagebox.showerror("Backup-Fehler", message)
    
    def restore_backup(self):
        """Stellt ein ausgewähltes Backup wieder her"""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte ein Backup auswählen!")
            return
        
        backup_name = self.backup_tree.item(selection[0])['text']
        backup_path = self.backup_manager.backup_dir / f"{backup_name}.bak"
        
        if not backup_path.exists():
            messagebox.showerror("Fehler", "Backup-Datei nicht gefunden!")
            return
        
        # Sicherheitsabfrage
        if messagebox.askyesno("Backup wiederherstellen", 
                              f"Aktuelle Datenbank mit Backup '{backup_name}' überschreiben?\n\n"
                              "⚠️ Dies kann nicht rückgängig gemacht werden!"):
            
            success, message = self.backup_manager.restore_from_backup(str(backup_path))
            
            if success:
                messagebox.showinfo("Wiederherstellung", 
                                   f"{message}\n\nBitte melden Sie sich ab und wieder an.")
            else:
                messagebox.showerror("Wiederherstellungs-Fehler", message)
    
    def delete_backup(self):
        """Löscht ein ausgewähltes Backup"""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte ein Backup auswählen!")
            return
        
        backup_name = self.backup_tree.item(selection[0])['text']
        backup_path = self.backup_manager.backup_dir / f"{backup_name}.bak"
        
        if messagebox.askyesno("Backup löschen", f"Backup '{backup_name}' wirklich löschen?"):
            success, message = self.backup_manager.delete_backup(str(backup_path))
            
            if success:
                messagebox.showinfo("Gelöscht", message)
                self.load_backup_list()  # Liste aktualisieren
            else:
                messagebox.showerror("Lösch-Fehler", message)
    
    # ✅ EXPORT-AKTIONEN
    
    def export_csv(self):
        """Exportiert Daten als CSV"""
        file_path = filedialog.asksaveasfilename(
            title="CSV-Export speichern",
            defaultextension=".csv",
            filetypes=[("CSV Dateien", "*.csv"), ("Alle Dateien", "*.*")]
        )
        
        if file_path:
            include_pw = self.include_passwords.get()
            success, message = self.backup_manager.export_to_csv(file_path, include_pw)
            
            if success:
                messagebox.showinfo("CSV-Export", message)
            else:
                messagebox.showerror("Export-Fehler", message)
    
    def export_json(self):
        """Exportiert Daten als JSON"""
        file_path = filedialog.asksaveasfilename(
            title="JSON-Export speichern",
            defaultextension=".json",
            filetypes=[("JSON Dateien", "*.json"), ("Alle Dateien", "*.*")]
        )
        
        if file_path:
            include_pw = self.include_passwords.get()
            success, message = self.backup_manager.export_to_json(file_path, include_pw)
            
            if success:
                messagebox.showinfo("JSON-Export", message)
            else:
                messagebox.showerror("Export-Fehler", message)
    
    # ✅ IMPORT-AKTIONEN
    
    def import_csv(self):
        """Importiert Daten aus CSV"""
        file_path = filedialog.askopenfilename(
            title="CSV-Import auswählen",
            filetypes=[("CSV Dateien", "*.csv"), ("Alle Dateien", "*.*")]
        )
        
        if file_path:
            # Zeige Vorschau
            self._show_csv_preview(file_path)
            
            # Bestätigung
            if messagebox.askyesno("CSV-Import", 
                                  f"Daten aus '{Path(file_path).name}' importieren?\n\n"
                                  "Prüfen Sie die Vorschau auf Richtigkeit."):
                
                merge_mode = self.merge_mode.get()
                success, message, conflicts = self.backup_manager.import_from_csv(file_path, merge_mode)
                
                if success:
                    result_text = message
                    if conflicts:
                        result_text += f"\n\nKonflikte:\n" + "\n".join([
                            f"• {c['title']}: {c['reason']}" for c in conflicts[:5]
                        ])
                        if len(conflicts) > 5:
                            result_text += f"\n... und {len(conflicts) - 5} weitere"
                    
                    messagebox.showinfo("CSV-Import", result_text)
                else:
                    messagebox.showerror("Import-Fehler", message)
    
    def restore_backup_file(self):
        """Stellt Backup aus Datei wieder her"""
        file_path = filedialog.askopenfilename(
            title="Backup-Datei auswählen",
            filetypes=[("Backup Dateien", "*.bak"), ("Alle Dateien", "*.*")]
        )
        
        if file_path:
            if messagebox.askyesno("Backup wiederherstellen", 
                                  f"Aktuelle Datenbank mit '{Path(file_path).name}' überschreiben?\n\n"
                                  "⚠️ Dies kann nicht rückgängig gemacht werden!"):
                
                success, message = self.backup_manager.restore_from_backup(file_path)
                
                if success:
                    messagebox.showinfo("Wiederherstellung", 
                                       f"{message}\n\nBitte melden Sie sich ab und wieder an.")
                else:
                    messagebox.showerror("Wiederherstellungs-Fehler", message)
    
    def _show_csv_preview(self, csv_path):
        """Zeigt CSV-Vorschau an"""
        try:
            import csv
            
            self.preview_text.config(state='normal')
            self.preview_text.delete('1.0', tk.END)
            
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Header
                self.preview_text.insert(tk.END, "📊 CSV-Vorschau:\n\n")
                
                # Feldnamen
                if reader.fieldnames:
                    self.preview_text.insert(tk.END, f"Felder: {', '.join(reader.fieldnames)}\n\n")
                
                # Erste 5 Zeilen
                count = 0
                for row in reader:
                    if count >= 5:
                        break
                    
                    self.preview_text.insert(tk.END, f"Zeile {count + 1}:\n")
                    for field, value in row.items():
                        if field and value:
                            display_value = value[:50] + "..." if len(value) > 50 else value
                            self.preview_text.insert(tk.END, f"  {field}: {display_value}\n")
                    self.preview_text.insert(tk.END, "\n")
                    count += 1
                
                if count == 0:
                    self.preview_text.insert(tk.END, "❌ Keine gültigen Daten gefunden")
                elif count >= 5:
                    self.preview_text.insert(tk.END, "... (weitere Zeilen verfügbar)")
            
            self.preview_text.config(state='disabled')
            
        except Exception as e:
            self.preview_text.config(state='normal')
            self.preview_text.delete('1.0', tk.END)
            self.preview_text.insert(tk.END, f"❌ Fehler beim Lesen der CSV-Datei:\n{str(e)}")
            self.preview_text.config(state='disabled')