import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import shutil
from pathlib import Path
from datetime import datetime
from gui.modern_styles import (
    WindowsClassicStyles, WindowsClassicColors, 
    create_classic_frame, create_classic_label_frame, 
    create_classic_entry, ClassicSpacing
)


class DatabaseSettingsDialog:
    def __init__(self, parent, password_manager, settings_manager):
        self.pm = password_manager
        self.settings_manager = settings_manager
        self.result = None
        
        WindowsClassicStyles.setup_windows_classic_theme()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Datenbank-Einstellungen")
        self.dialog.geometry("700x900")
        self.dialog.configure(bg=WindowsClassicColors.WINDOW_BG)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 100, 
            parent.winfo_rooty() + 50
        ))
        
        self.dialog.focus_set()
        self.dialog.focus_force()

        self.create_settings_ui()
        self.load_database_info()
        
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
        
        self.dialog.wait_window()
    
    def create_settings_ui(self):
        main_frame = create_classic_frame(self.dialog, WindowsClassicColors.DIALOG_BG)
        main_frame.pack(expand=True, fill='both')
        
        header_frame = create_classic_frame(main_frame, "#6ba644")
        header_frame.pack(fill='x')
        
        header_content = create_classic_frame(header_frame, "#6ba644")
        header_content.pack(expand=True, fill='x', padx=40, pady=25)
        
        icon_frame = create_classic_frame(header_content, "#5a9137")
        icon_frame.configure(width=50, height=50)
        icon_frame.pack_propagate(False)
        icon_frame.pack(pady=(0, 10))
        
        icon_label = tk.Label(icon_frame, text="🗃️", 
                             bg="#5a9137", fg="white", 
                             font=('Segoe UI', 20, 'normal'))
        icon_label.place(relx=0.5, rely=0.5, anchor='center')

        title_label = tk.Label(header_content, text="Datenbank-Einstellungen",
                               font=('Segoe UI', 16, 'bold'),
                               bg="#6ba644", fg="white")
        title_label.pack()
        
        content_frame = create_classic_frame(main_frame, WindowsClassicColors.DIALOG_BG)
        content_frame.pack(expand=True, fill='both', padx=30, pady=30)
        
        self.notebook = ttk.Notebook(content_frame, style='Classic.TNotebook')
        self.notebook.pack(expand=True, fill='both', pady=(0, 20))
        
        self.create_info_tab()
        self.create_security_tab()
        self.create_maintenance_tab()
        
        self.create_button_area(content_frame)
    
    def create_info_tab(self):
        info_frame = create_classic_frame(self.notebook, WindowsClassicColors.WINDOW_BG)
        self.notebook.add(info_frame, text='📊 Informationen')
        
        db_info_frame = create_classic_label_frame(info_frame, "📋 Datenbank-Details")
        db_info_frame.pack(fill='x', padx=15, pady=15)
        
        info_container = create_classic_frame(db_info_frame, WindowsClassicColors.WINDOW_BG)
        info_container.pack(fill='x', padx=15, pady=15)
        
        self.info_labels = {}
        
        info_fields = [
            ("Dateiname:", "filename"),
            ("Pfad:", "path"),
            ("Größe:", "size"),
            ("Erstellt:", "created"),
            ("Zuletzt geändert:", "modified"),
            ("Anzahl Einträge:", "entries"),
            ("Mit 2FA:", "totp_entries"),
            ("Kategorien:", "categories")
        ]
        
        for label_text, field_name in info_fields:
            row_frame = create_classic_frame(info_container, WindowsClassicColors.WINDOW_BG)
            row_frame.pack(fill='x', pady=4)
            
            label = tk.Label(row_frame, text=label_text,
                           bg=WindowsClassicColors.WINDOW_BG,
                           fg=WindowsClassicColors.TEXT_PRIMARY,
                           font=('Segoe UI', 10, 'bold'),
                           width=18, anchor='w')
            label.pack(side='left')
            
            value_label = tk.Label(row_frame, text="",
                                 bg=WindowsClassicColors.WINDOW_BG,
                                 fg=WindowsClassicColors.TEXT_SECONDARY,
                                 font=('Segoe UI', 10, 'normal'),
                                 anchor='w')
            value_label.pack(side='left', fill='x', expand=True)
            
            self.info_labels[field_name] = value_label
        
        stats_frame = create_classic_label_frame(info_frame, "📈 Statistiken")
        stats_frame.pack(fill='x', padx=15, pady=15)
        
        stats_container = create_classic_frame(stats_frame, WindowsClassicColors.WINDOW_BG)
        stats_container.pack(fill='x', padx=15, pady=15)
        
        stats_fields = [
            ("Starke Passwörter:", "strong_passwords"),
            ("Schwache Passwörter:", "weak_passwords"),
            ("Doppelte Passwörter:", "duplicate_passwords"),
            ("Durchschnittliche Länge:", "avg_length"),
            ("Ältester Eintrag:", "oldest_entry"),
            ("Neuester Eintrag:", "newest_entry")
        ]
        
        for label_text, field_name in stats_fields:
            row_frame = create_classic_frame(stats_container, WindowsClassicColors.WINDOW_BG)
            row_frame.pack(fill='x', pady=4)
            
            label = tk.Label(row_frame, text=label_text,
                           bg=WindowsClassicColors.WINDOW_BG,
                           fg=WindowsClassicColors.TEXT_PRIMARY,
                           font=('Segoe UI', 10, 'bold'),
                           width=18, anchor='w')
            label.pack(side='left')
            
            value_label = tk.Label(row_frame, text="",
                                 bg=WindowsClassicColors.WINDOW_BG,
                                 fg=WindowsClassicColors.TEXT_SECONDARY,
                                 font=('Segoe UI', 10, 'normal'),
                                 anchor='w')
            value_label.pack(side='left', fill='x', expand=True)
            
            self.info_labels[field_name] = value_label
    
    def create_security_tab(self):
        security_frame = create_classic_frame(self.notebook, WindowsClassicColors.WINDOW_BG)
        self.notebook.add(security_frame, text='🔒 Sicherheit')
        
        password_frame = create_classic_label_frame(security_frame, "🔐 Master-Passwort")
        password_frame.pack(fill='x', padx=15, pady=15)
        
        password_container = create_classic_frame(password_frame, WindowsClassicColors.WINDOW_BG)
        password_container.pack(fill='x', padx=15, pady=15)
        
        current_strength_frame = create_classic_frame(password_container, WindowsClassicColors.WINDOW_BG)
        current_strength_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(current_strength_frame, text="Aktuelle Stärke:",
                bg=WindowsClassicColors.WINDOW_BG, fg=WindowsClassicColors.TEXT_PRIMARY,
                font=('Segoe UI', 10, 'bold')).pack(side='left')
        
        self.password_strength_label = tk.Label(current_strength_frame, text="Unbekannt",
                                               bg=WindowsClassicColors.WINDOW_BG,
                                               fg=WindowsClassicColors.TEXT_SECONDARY,
                                               font=('Segoe UI', 10, 'normal'))
        self.password_strength_label.pack(side='left', padx=(8, 0))
        
        change_pw_btn = tk.Button(password_container, text="🔐 Master-Passwort ändern",
                                 command=self.change_master_password,
                                 bg="#6ba644", fg="white", font=('Segoe UI', 11, 'bold'),
                                 relief='flat', bd=0, padx=20, pady=12,
                                 cursor='hand2')
        change_pw_btn.pack(fill='x', pady=(0, 10))
        
        encryption_frame = create_classic_label_frame(security_frame, "🛡️ Verschlüsselung")
        encryption_frame.pack(fill='x', padx=15, pady=15)
        
        encryption_container = create_classic_frame(encryption_frame, WindowsClassicColors.WINDOW_BG)
        encryption_container.pack(fill='x', padx=15, pady=15)
        
        encryption_info = [
            ("Algorithmus:", "AES-256 (Fernet)"),
            ("Schlüssel-Ableitung:", "PBKDF2-HMAC-SHA256"),
            ("Iterationen:", "100.000"),
            ("Salt-Länge:", "16 Bytes")
        ]
        
        for label_text, value in encryption_info:
            row_frame = create_classic_frame(encryption_container, WindowsClassicColors.WINDOW_BG)
            row_frame.pack(fill='x', pady=2)
            
            label = tk.Label(row_frame, text=label_text,
                           bg=WindowsClassicColors.WINDOW_BG,
                           fg=WindowsClassicColors.TEXT_PRIMARY,
                           font=('Segoe UI', 10, 'bold'),
                           width=18, anchor='w')
            label.pack(side='left')
            
            value_label = tk.Label(row_frame, text=value,
                                 bg=WindowsClassicColors.WINDOW_BG,
                                 fg=WindowsClassicColors.TEXT_SECONDARY,
                                 font=('Segoe UI', 10, 'normal'),
                                 anchor='w')
            value_label.pack(side='left')
        
        def create_hover_effect(button, normal_color, hover_color):
            def on_enter(event):
                button.config(bg=hover_color)
            def on_leave(event):
                button.config(bg=normal_color)
            button.bind('<Enter>', on_enter)
            button.bind('<Leave>', on_leave)
        
        create_hover_effect(change_pw_btn, "#6ba644", "#5a9137")
    
    def create_maintenance_tab(self):
        maintenance_frame = create_classic_frame(self.notebook, WindowsClassicColors.WINDOW_BG)
        self.notebook.add(maintenance_frame, text='🔧 Wartung')
        
        database_frame = create_classic_label_frame(maintenance_frame, "📁 Datenbank-Datei")
        database_frame.pack(fill='x', padx=15, pady=15)
        
        database_container = create_classic_frame(database_frame, WindowsClassicColors.WINDOW_BG)
        database_container.pack(fill='x', padx=15, pady=15)
        
        buttons_data = [
            ("📋 Datenbank kopieren", self.copy_database),
            ("📁 Datenbank verschieben", self.move_database),
            ("✏️ Datenbank umbenennen", self.rename_database)
        ]
        
        for text, command in buttons_data:
            btn = tk.Button(database_container, text=text,
                           command=command,
                           bg="#4a90e2", fg="white", font=('Segoe UI', 10, 'normal'),
                           relief='flat', bd=0, padx=15, pady=8)
            btn.pack(fill='x', pady=3)
            self._create_button_hover(btn, "#4a90e2", "#357abd")
        
        cleanup_frame = create_classic_label_frame(maintenance_frame, "🧹 Bereinigung")
        cleanup_frame.pack(fill='x', padx=15, pady=15)
        
        cleanup_container = create_classic_frame(cleanup_frame, WindowsClassicColors.WINDOW_BG)
        cleanup_container.pack(fill='x', padx=15, pady=15)
        
        cleanup_buttons = [
            ("🔍 Integrität prüfen", self.check_database_integrity),
            ("🗑️ Duplikate entfernen", self.remove_duplicate_entries),
            ("🗜️ Datenbank komprimieren", self.compact_database)
        ]
        
        for text, command in cleanup_buttons:
            btn = tk.Button(cleanup_container, text=text,
                           command=command,
                           bg="#666666", fg="white", font=('Segoe UI', 10, 'normal'),
                           relief='flat', bd=0, padx=15, pady=8)
            btn.pack(fill='x', pady=3)
            self._create_button_hover(btn, "#666666", "#555555")
        
        danger_frame = create_classic_label_frame(maintenance_frame, "⚠️ Gefährliche Aktionen")
        danger_frame.pack(fill='x', padx=15, pady=15)
        
        danger_container = create_classic_frame(danger_frame, WindowsClassicColors.WINDOW_BG)
        danger_container.pack(fill='x', padx=15, pady=15)
        
        delete_db_btn = tk.Button(danger_container, text="🗑️ Datenbank löschen",
                                 command=self.delete_database,
                                 bg="#d32f2f", fg="white", font=('Segoe UI', 10, 'bold'),
                                 relief='flat', bd=0, padx=15, pady=8)
        delete_db_btn.pack(fill='x', pady=3)
        self._create_button_hover(delete_db_btn, "#d32f2f", "#c62828")
    
    def create_button_area(self, parent):
        button_frame = create_classic_frame(parent, WindowsClassicColors.DIALOG_BG)
        button_frame.pack(fill='x')
        
        refresh_btn = tk.Button(button_frame, text="🔄 Aktualisieren",
                               command=self.load_database_info,
                               bg="#6ba644", fg="white", font=('Segoe UI', 10, 'normal'),
                               relief='flat', bd=0, padx=20, pady=10)
        refresh_btn.pack(side='left')
        
        close_btn = tk.Button(button_frame, text="Schließen",
                             command=self.dialog.destroy,
                             bg="#666666", fg="white", font=('Segoe UI', 10, 'normal'),
                             relief='flat', bd=0, padx=20, pady=10, width=12)
        close_btn.pack(side='right')
        
        self._create_button_hover(refresh_btn, "#6ba644", "#5a9137")
        self._create_button_hover(close_btn, "#666666", "#555555")
    
    def _create_button_hover(self, button, normal_color, hover_color):
        def on_enter(event):
            button.config(bg=hover_color)
        def on_leave(event):
            button.config(bg=normal_color)
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
    
    def load_database_info(self):
        if not self.pm.is_unlocked:
            return
        
        try:
            db_path = Path(self.pm.database_file)
            stat = db_path.stat()
            
            self.info_labels['filename'].config(text=db_path.name)
            self.info_labels['path'].config(text=str(db_path.parent))
            self.info_labels['size'].config(text=f"{round(stat.st_size / 1024, 2)} KB")
            self.info_labels['created'].config(text=datetime.fromtimestamp(stat.st_ctime).strftime("%d.%m.%Y %H:%M"))
            self.info_labels['modified'].config(text=datetime.fromtimestamp(stat.st_mtime).strftime("%d.%m.%Y %H:%M"))
            
            entries = self.pm.list_entries()
            self.info_labels['entries'].config(text=str(len(entries)))
            
            totp_count = sum(1 for entry in entries if entry.has_totp())
            self.info_labels['totp_entries'].config(text=str(totp_count))
            
            categories = self.pm.get_categories_with_counts()
            self.info_labels['categories'].config(text=str(len(categories)))
            
            self._calculate_password_stats(entries)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Datenbank-Informationen nicht laden:\n{str(e)}")
    
    def _calculate_password_stats(self, entries):
        if not entries:
            return
        
        strong_count = 0
        weak_count = 0
        passwords = []
        lengths = []
        dates = []
        
        for entry in entries:
            passwords.append(entry.password)
            lengths.append(len(entry.password))
            
            try:
                date = datetime.fromisoformat(entry.created.replace('Z', '+00:00'))
                dates.append(date)
            except:
                pass
            
            try:
                from core.password_generator import PasswordGenerator
                pg = PasswordGenerator()
                _, score = pg.calculate_password_strength(entry.password)
                if score >= 70:
                    strong_count += 1
                else:
                    weak_count += 1
            except:
                pass
        
        duplicate_count = len(passwords) - len(set(passwords))
        avg_length = round(sum(lengths) / len(lengths), 1) if lengths else 0
        
        self.info_labels['strong_passwords'].config(text=str(strong_count))
        self.info_labels['weak_passwords'].config(text=str(weak_count))
        self.info_labels['duplicate_passwords'].config(text=str(duplicate_count))
        self.info_labels['avg_length'].config(text=f"{avg_length} Zeichen")
        
        if dates:
            oldest = min(dates).strftime("%d.%m.%Y")
            newest = max(dates).strftime("%d.%m.%Y")
            self.info_labels['oldest_entry'].config(text=oldest)
            self.info_labels['newest_entry'].config(text=newest)
    
    def change_master_password(self):
        from gui.change_password_dialog import ChangePasswordDialog
        
        dialog = ChangePasswordDialog(self.dialog, self.pm)
        
        if dialog.result:
            messagebox.showinfo("Erfolg", "Master-Passwort erfolgreich geändert!")
            self.load_database_info()
    
    def copy_database(self):
        target_path = filedialog.asksaveasfilename(
            title="Datenbank kopieren",
            defaultextension=".enc",
            filetypes=[("Verschlüsselte Dateien", "*.enc"), ("Alle Dateien", "*.*")]
        )
        
        if target_path:
            try:
                shutil.copy2(self.pm.database_file, target_path)
                messagebox.showinfo("Erfolg", f"Datenbank kopiert nach:\n{target_path}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Konnte Datenbank nicht kopieren:\n{str(e)}")
    
    def move_database(self):
        target_path = filedialog.asksaveasfilename(
            title="Datenbank verschieben",
            defaultextension=".enc",
            filetypes=[("Verschlüsselte Dateien", "*.enc"), ("Alle Dateien", "*.*")]
        )
        
        if target_path:
            if messagebox.askyesno("Datenbank verschieben", 
                                  f"Datenbank nach '{target_path}' verschieben?\n\n"
                                  "Die Anwendung wird danach beendet."):
                try:
                    shutil.move(self.pm.database_file, target_path)
                    messagebox.showinfo("Erfolg", f"Datenbank verschoben nach:\n{target_path}\n\nAnwendung wird beendet.")
                    self.dialog.destroy()
                    self.pm.root.quit()
                except Exception as e:
                    messagebox.showerror("Fehler", f"Konnte Datenbank nicht verschieben:\n{str(e)}")
    
    def rename_database(self):
        current_path = Path(self.pm.database_file)
        current_name = current_path.stem
        
        new_name = self._ask_string("Datenbank umbenennen", 
                                   "Neuer Name für die Datenbank:", 
                                   initialvalue=current_name)
        
        if new_name and new_name != current_name:
            new_path = current_path.parent / f"{new_name}.enc"
            
            if new_path.exists():
                messagebox.showerror("Fehler", "Eine Datenbank mit diesem Namen existiert bereits!")
                return
            
            try:
                shutil.move(str(current_path), str(new_path))
                self.pm.database_file = str(new_path)
                messagebox.showinfo("Erfolg", f"Datenbank umbenannt zu '{new_name}'")
                self.load_database_info()
            except Exception as e:
                messagebox.showerror("Fehler", f"Konnte Datenbank nicht umbenennen:\n{str(e)}")
    
    def check_database_integrity(self):
        try:
            entries = self.pm.list_entries()
            
            issues = []
            
            for i, entry in enumerate(entries):
                if not entry.title.strip():
                    issues.append(f"Eintrag {i+1}: Kein Titel")
                if not entry.password:
                    issues.append(f"Eintrag '{entry.title}': Kein Passwort")
            
            if issues:
                issue_text = "\n".join(issues[:10])
                if len(issues) > 10:
                    issue_text += f"\n... und {len(issues) - 10} weitere Probleme"
                
                messagebox.showwarning("Integritätsprobleme gefunden", 
                                      f"Probleme gefunden:\n\n{issue_text}")
            else:
                messagebox.showinfo("Integrität", "Keine Probleme gefunden. Datenbank ist in Ordnung.")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Integrität nicht prüfen:\n{str(e)}")
    
    def remove_duplicate_entries(self):
        try:
            entries = self.pm.list_entries()
            seen_titles = set()
            duplicates = []
            
            for entry in entries:
                if entry.title in seen_titles:
                    duplicates.append(entry.title)
                else:
                    seen_titles.add(entry.title)
            
            if duplicates:
                if messagebox.askyesno("Duplikate gefunden", 
                                      f"{len(duplicates)} doppelte Einträge gefunden.\n\n"
                                      "Duplikate entfernen? (Kann nicht rückgängig gemacht werden)"):
                    
                    for title in duplicates:
                        self.pm.delete_entry(title)
                    
                    messagebox.showinfo("Erfolg", f"{len(duplicates)} doppelte Einträge entfernt.")
                    self.load_database_info()
            else:
                messagebox.showinfo("Keine Duplikate", "Keine doppelten Einträge gefunden.")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Duplikate nicht entfernen:\n{str(e)}")
    
    def compact_database(self):
        if messagebox.askyesno("Datenbank komprimieren", 
                              "Datenbank komprimieren und optimieren?\n\n"
                              "Dies erstellt eine bereinigte Version der Datenbank."):
            try:
                self.pm.save_database()
                messagebox.showinfo("Erfolg", "Datenbank wurde komprimiert und optimiert.")
                self.load_database_info()
            except Exception as e:
                messagebox.showerror("Fehler", f"Konnte Datenbank nicht komprimieren:\n{str(e)}")
    
    def delete_database(self):
        if messagebox.askyesno("⚠️ WARNUNG", 
                              "Datenbank PERMANENT löschen?\n\n"
                              "⚠️ DIES KANN NICHT RÜCKGÄNGIG GEMACHT WERDEN!\n\n"
                              "Alle Passwörter gehen verloren!"):
            
            if messagebox.askyesno("Letzte Bestätigung", 
                                  "Sind Sie ABSOLUT SICHER?\n\n"
                                  "Datenbank wird unwiderruflich gelöscht!"):
                try:
                    db_path = self.pm.database_file
                    self.pm.lock_database()
                    Path(db_path).unlink()
                    
                    messagebox.showinfo("Gelöscht", "Datenbank wurde gelöscht.\nAnwendung wird beendet.")
                    self.dialog.destroy()
                    self.pm.root.quit()
                    
                except Exception as e:
                    messagebox.showerror("Fehler", f"Konnte Datenbank nicht löschen:\n{str(e)}")
    
    def _ask_string(self, title, prompt, initialvalue=""):
        dialog = tk.Toplevel(self.dialog)
        dialog.title(title)
        dialog.geometry("500x280")
        dialog.configure(bg=WindowsClassicColors.WINDOW_BG)
        dialog.transient(self.dialog)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        dialog.geometry("+%d+%d" % (
            self.dialog.winfo_rootx() + 125, 
            self.dialog.winfo_rooty() + 150
        ))
        
        result = [None]
        
        main_frame = create_classic_frame(dialog)
        main_frame.pack(expand=True, fill='both')
        
        header_frame = create_classic_frame(main_frame, "#6ba644")
        header_frame.pack(fill='x')
        
        header_content = create_classic_frame(header_frame, "#6ba644")
        header_content.pack(expand=True, fill='x', padx=30, pady=20)
        
        icon_frame = create_classic_frame(header_content, "#5a9137")
        icon_frame.configure(width=40, height=40)
        icon_frame.pack_propagate(False)
        icon_frame.pack(pady=(0, 8))
        
        icon_label = tk.Label(icon_frame, text="✏️", 
                             bg="#5a9137", fg="white", 
                             font=('Segoe UI', 16, 'normal'))
        icon_label.place(relx=0.5, rely=0.5, anchor='center')

        title_label = tk.Label(header_content, text=title,
                               font=('Segoe UI', 14, 'bold'),
                               bg="#6ba644", fg="white")
        title_label.pack()
        
        content_frame = create_classic_frame(main_frame, WindowsClassicColors.DIALOG_BG)
        content_frame.pack(expand=True, fill='both', padx=30, pady=30)
        
        prompt_label = tk.Label(content_frame, text=prompt,
                               bg=WindowsClassicColors.DIALOG_BG,
                               fg=WindowsClassicColors.TEXT_PRIMARY,
                               font=('Segoe UI', 10, 'normal'))
        prompt_label.pack(pady=(0, 15))
        
        entry = create_classic_entry(content_frame)
        entry.pack(fill='x', pady=(0, 25))
        
        if initialvalue:
            entry.insert(0, initialvalue)
            entry.select_range(0, tk.END)
        
        button_frame = create_classic_frame(content_frame, WindowsClassicColors.DIALOG_BG)
        button_frame.pack()
        
        def on_ok():
            result[0] = entry.get().strip()
            dialog.destroy()
        
        def on_cancel():
            result[0] = None
            dialog.destroy()
        
        cancel_btn = tk.Button(button_frame, text="Abbrechen", command=on_cancel,
                              bg="#666666", fg="white", font=('Segoe UI', 10, 'normal'),
                              relief='flat', bd=0, padx=20, pady=8, width=10)
        cancel_btn.pack(side='left', padx=(0, 15))
        
        ok_btn = tk.Button(button_frame, text="OK", command=on_ok,
                          bg="#6ba644", fg="white", font=('Segoe UI', 10, 'bold'),
                          relief='flat', bd=0, padx=20, pady=8, width=10)
        ok_btn.pack(side='left')
        
        self._create_button_hover(cancel_btn, "#666666", "#555555")
        self._create_button_hover(ok_btn, "#6ba644", "#5a9137")
        
        entry.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())
        
        dialog.after(100, lambda: entry.focus_set())
        dialog.wait_window()
        
        return result[0]