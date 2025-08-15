import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import shutil
from pathlib import Path
from gui.modern_styles import WindowsClassicStyles, WindowsClassicColors, create_classic_frame, create_classic_label_frame, create_status_bar, ClassicSpacing


class DatabaseSelector:
    def __init__(self, root, on_database_selected):
        self.root = root
        self.on_database_selected = on_database_selected
        self.selected_database = None
        
        self.databases_dir = Path("data")
        self.databases_dir.mkdir(exist_ok=True)
        
        WindowsClassicStyles.setup_windows_classic_theme()
        self.setup_selector_screen()
    
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def setup_selector_screen(self):
        self.clear_screen()
        self.root.geometry("900x700")
        self.root.minsize(900, 700)
        self.root.configure(bg=WindowsClassicColors.WINDOW_BG)
        
        main_frame = create_classic_frame(self.root, WindowsClassicColors.DIALOG_BG)
        main_frame.pack(expand=True, fill='both')
        
        hero_frame = create_classic_frame(main_frame, "#6ba644")
        hero_frame.pack(fill='x', pady=0)
        
        hero_content = create_classic_frame(hero_frame, "#6ba644")
        hero_content.pack(expand=True, fill='x', padx=40, pady=40)
        
        hero_icon_frame = create_classic_frame(hero_content, "#5a9137")
        hero_icon_frame.configure(width=80, height=80)
        hero_icon_frame.pack_propagate(False)
        hero_icon_frame.pack(pady=(0, 20))
        
        hero_icon = tk.Label(hero_icon_frame, text="🗄", 
                            bg="#5a9137", fg="white", 
                            font=('Segoe UI', 28, 'normal'))
        hero_icon.place(relx=0.5, rely=0.5, anchor='center')
        
        hero_title = tk.Label(hero_content, text="🗄️ Datenbank-Manager", 
                             bg="#6ba644", fg="white", 
                             font=('Segoe UI', 24, 'normal'))
        hero_title.pack(pady=(0, 8))
        
        hero_subtitle = tk.Label(hero_content, 
                               text="Wähle eine Passwort-Datenbank aus oder erstelle eine neue",
                               bg="#6ba644", fg="white", 
                               font=('Segoe UI', 12, 'normal'))
        hero_subtitle.pack()
        
        content_frame = create_classic_frame(main_frame, WindowsClassicColors.DIALOG_BG)
        content_frame.pack(expand=True, fill='both', padx=30, pady=30)
        
        actions_frame = create_classic_frame(content_frame, WindowsClassicColors.DIALOG_BG)
        actions_frame.pack(fill='x', pady=(0, 30))
        
        action_buttons_frame = create_classic_frame(actions_frame, WindowsClassicColors.DIALOG_BG)
        action_buttons_frame.pack()
        
        new_btn = tk.Button(action_buttons_frame, text="➕ Neue Datenbank", 
                           command=self.create_new_database,
                           bg="#6ba644", fg="white", font=('Segoe UI', 11, 'bold'),
                           relief='flat', bd=0, padx=20, pady=12,
                           cursor='hand2')
        new_btn.pack(side='left', padx=(0, 15))
        
        browse_btn = tk.Button(action_buttons_frame, text="🔍 Durchsuchen", 
                              command=self.browse_for_database,
                              bg="#4a90e2", fg="white", font=('Segoe UI', 11, 'bold'),
                              relief='flat', bd=0, padx=20, pady=12,
                              cursor='hand2')
        browse_btn.pack(side='left', padx=(0, 15))
        
        import_btn = tk.Button(action_buttons_frame, text="📦 Backup importieren", 
                              command=self.import_backup,
                              bg="#666666", fg="white", font=('Segoe UI', 11, 'bold'),
                              relief='flat', bd=0, padx=20, pady=12,
                              cursor='hand2')
        import_btn.pack(side='left')
        
        def create_action_hover(button, normal_color, hover_color):
            def on_enter(event):
                button.config(bg=hover_color)
            def on_leave(event):
                button.config(bg=normal_color)
            button.bind('<Enter>', on_enter)
            button.bind('<Leave>', on_leave)
        
        create_action_hover(new_btn, "#6ba644", "#5a9137")
        create_action_hover(browse_btn, "#4a90e2", "#357abd")
        create_action_hover(import_btn, "#666666", "#555555")
        
        list_frame = create_classic_label_frame(content_frame, "📂 Verfügbare Datenbanken")
        list_frame.pack(expand=True, fill='both', pady=(0, 20))
        
        self.databases_container = create_classic_frame(list_frame, WindowsClassicColors.WINDOW_BG)
        self.databases_container.pack(expand=True, fill='both', padx=15, pady=15)
        
        canvas = tk.Canvas(self.databases_container, bg=WindowsClassicColors.WINDOW_BG, 
                          highlightthickness=0, relief='flat')
        scrollbar = ttk.Scrollbar(self.databases_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = create_classic_frame(canvas, WindowsClassicColors.WINDOW_BG)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        bottom_frame = create_classic_frame(content_frame, WindowsClassicColors.DIALOG_BG)
        bottom_frame.pack(fill='x')
        
        bottom_buttons = create_classic_frame(bottom_frame, WindowsClassicColors.DIALOG_BG)
        bottom_buttons.pack(side='right')
        
        refresh_btn = tk.Button(bottom_buttons, text="🔄 Aktualisieren", 
                               command=self.refresh_database_list,
                               bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                               relief='raised', bd=1, padx=12, pady=4)
        refresh_btn.pack(side='left', padx=(0, 8))
        
        delete_btn = tk.Button(bottom_buttons, text="🗑️ Löschen", 
                              command=self.delete_database,
                              bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                              relief='raised', bd=1, padx=12, pady=4)
        delete_btn.pack(side='left')
        
        def create_hover_effect(button):
            def on_enter(event):
                button.config(bg='#d5d5d5')
            def on_leave(event):
                button.config(bg='#e1e1e1')
            button.bind('<Enter>', on_enter)
            button.bind('<Leave>', on_leave)
        
        create_hover_effect(refresh_btn)
        create_hover_effect(delete_btn)
        
        status_frame, self.status_label = create_status_bar(content_frame, "Bereit")
        status_frame.pack(fill='x', pady=(10, 0))
        
        self.refresh_database_list()
    
    def browse_for_database(self):
        file_path = filedialog.askopenfilename(
            title="Datenbank-Datei auswählen",
            filetypes=[("Verschlüsselte Dateien", "*.enc"), ("Backup-Dateien", "*.bak"), ("Alle Dateien", "*.*")],
            initialdir=str(self.databases_dir)
        )
        
        if file_path:
            source_file = Path(file_path)
            
            if source_file.suffix == '.bak':
                self._import_backup_as_database(file_path)
            else:
                target_file = self.databases_dir / source_file.name
                
                if target_file.exists():
                    if not messagebox.askyesno("Datenbank existiert", 
                                             f"Datenbank '{source_file.name}' existiert bereits im data-Ordner.\n"
                                             "Möchten Sie direkt öffnen ohne zu kopieren?"):
                        return
                else:
                    if messagebox.askyesno("Datenbank kopieren", 
                                         f"Datenbank '{source_file.name}' in den data-Ordner kopieren?"):
                        try:
                            shutil.copy2(source_file, target_file)
                            self.refresh_database_list()
                        except Exception as e:
                            messagebox.showerror("Fehler", f"Konnte Datenbank nicht kopieren:\n{str(e)}")
                            return
                
                self.selected_database = str(target_file if target_file.exists() else source_file)
                self.on_database_selected(self.selected_database)
    
    def _import_backup_as_database(self, backup_path):
        backup_file = Path(backup_path)
        suggested_name = backup_file.stem.replace('_backup_', '_').replace('_auto', '')
        
        db_name = self._ask_string_with_focus("Backup als Datenbank", 
                                             "Name für die Datenbank:",
                                             initialvalue=suggested_name)
        
        if not db_name:
            return
        
        db_name = "".join(c for c in db_name if c.isalnum() or c in (' ', '-', '_')).strip()
        
        if not db_name:
            messagebox.showerror("Fehler", "Ungültiger Datenbankname!")
            return
        
        target_file = self.databases_dir / f"{db_name}.enc"
        
        if target_file.exists():
            if not messagebox.askyesno("Warnung", 
                                     f"Datenbank '{db_name}' existiert bereits.\n"
                                     "Überschreiben?"):
                return
        
        try:
            shutil.copy2(backup_path, target_file)
            messagebox.showinfo("Erfolg", f"Backup als '{db_name}' importiert!")
            self.refresh_database_list()
            
            if messagebox.askyesno("Datenbank öffnen", 
                                  f"Möchten Sie die Datenbank '{db_name}' jetzt öffnen?"):
                self.selected_database = str(target_file)
                self.on_database_selected(str(target_file))
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Backup konnte nicht importiert werden:\n{str(e)}")
    
    def refresh_database_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        database_files = list(self.databases_dir.glob("*.enc"))
        
        if not database_files:
            empty_frame = create_classic_frame(self.scrollable_frame, WindowsClassicColors.WINDOW_BG)
            empty_frame.pack(fill='x', pady=20)
            
            empty_icon = tk.Label(empty_frame, text="📂", 
                                 bg=WindowsClassicColors.WINDOW_BG, 
                                 fg=WindowsClassicColors.TEXT_SECONDARY,
                                 font=('Segoe UI', 48, 'normal'))
            empty_icon.pack(pady=(0, 10))
            
            empty_text = tk.Label(empty_frame, text="Keine Datenbanken gefunden", 
                                 bg=WindowsClassicColors.WINDOW_BG, 
                                 fg=WindowsClassicColors.TEXT_SECONDARY,
                                 font=('Segoe UI', 14, 'normal'))
            empty_text.pack(pady=(0, 5))
            
            empty_subtitle = tk.Label(empty_frame, text="Erstelle eine neue Datenbank!", 
                                     bg=WindowsClassicColors.WINDOW_BG, 
                                     fg=WindowsClassicColors.TEXT_DISABLED,
                                     font=('Segoe UI', 10, 'normal'))
            empty_subtitle.pack()
            
            self.status_label.config(text="Keine Datenbanken gefunden - erstelle eine neue!")
            return
        
        for i, db_file in enumerate(database_files):
            try:
                stat = db_file.stat()
                size_kb = round(stat.st_size / 1024, 1)
                size_str = f"{size_kb} KB" if size_kb > 0 else "< 1 KB"
                
                import datetime
                modified = datetime.datetime.fromtimestamp(stat.st_mtime)
                modified_str = modified.strftime("%d.%m.%Y %H:%M")
                
                display_name = db_file.stem
                
                card = self._create_database_card(display_name, size_str, modified_str, db_file)
                card.pack(fill='x', pady=5, padx=10)
                
            except Exception as e:
                error_card = self._create_error_card(db_file.name, str(e))
                error_card.pack(fill='x', pady=5, padx=10)
        
        count = len(database_files)
        from gui.modern_styles import update_status_bar
        update_status_bar(self.status_label, f"{count} Datenbank{'en' if count != 1 else ''} gefunden")
    
    def _create_database_card(self, name, size, modified, db_file):
        card_frame = create_classic_frame(self.scrollable_frame, "#f8f9fa")
        card_frame.configure(relief='solid', bd=1)
        
        card_content = create_classic_frame(card_frame, "#f8f9fa")
        card_content.pack(fill='x', padx=15, pady=15)
        
        left_section = create_classic_frame(card_content, "#f8f9fa")
        left_section.pack(side='left', fill='x', expand=True)
        
        icon_frame = create_classic_frame(left_section, "#6ba644")
        icon_frame.configure(width=40, height=40)
        icon_frame.pack_propagate(False)
        icon_frame.pack(side='left')
        
        icon_label = tk.Label(icon_frame, text="🔐", 
                             bg="#6ba644", fg="white", 
                             font=('Segoe UI', 18, 'normal'))
        icon_label.place(relx=0.5, rely=0.5, anchor='center')
        
        info_section = create_classic_frame(left_section, "#f8f9fa")
        info_section.pack(side='left', fill='x', expand=True, padx=(15, 0))
        
        name_label = tk.Label(info_section, text=name, 
                             bg="#f8f9fa", fg=WindowsClassicColors.TEXT_PRIMARY,
                             font=('Segoe UI', 12, 'bold'), anchor='w')
        name_label.pack(fill='x')
        
        details_label = tk.Label(info_section, text=f"{size} • {modified}", 
                               bg="#f8f9fa", fg=WindowsClassicColors.TEXT_SECONDARY,
                               font=('Segoe UI', 9, 'normal'), anchor='w')
        details_label.pack(fill='x', pady=(2, 0))
        
        def on_card_click(event):
            self.selected_database = str(db_file)
            self.on_database_selected(str(db_file))
        
        def on_enter(event):
            card_frame.config(bg="#e9ecef")
            card_content.config(bg="#e9ecef")
            left_section.config(bg="#e9ecef")
            info_section.config(bg="#e9ecef")
            name_label.config(bg="#e9ecef")
            details_label.config(bg="#e9ecef")
            
        def on_leave(event):
            card_frame.config(bg="#f8f9fa")
            card_content.config(bg="#f8f9fa")
            left_section.config(bg="#f8f9fa")
            info_section.config(bg="#f8f9fa")
            name_label.config(bg="#f8f9fa")
            details_label.config(bg="#f8f9fa")
        
        for widget in [card_frame, card_content, left_section, info_section, name_label, details_label]:
            widget.bind('<Button-1>', on_card_click)
            widget.bind('<Double-Button-1>', on_card_click)
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
            widget.configure(cursor='hand2')
        
        return card_frame
    
    def _create_error_card(self, name, error):
        card_frame = create_classic_frame(self.scrollable_frame, "#fff5f5")
        card_frame.configure(relief='solid', bd=1, borderwidth=1)
        
        card_content = create_classic_frame(card_frame, "#fff5f5")
        card_content.pack(fill='x', padx=15, pady=15)
        
        icon_frame = create_classic_frame(card_content, "#e53e3e")
        icon_frame.configure(width=40, height=40)
        icon_frame.pack_propagate(False)
        icon_frame.pack(side='left')
        
        icon_label = tk.Label(icon_frame, text="⚠️", 
                             bg="#e53e3e", fg="white", 
                             font=('Segoe UI', 18, 'normal'))
        icon_label.place(relx=0.5, rely=0.5, anchor='center')
        
        info_section = create_classic_frame(card_content, "#fff5f5")
        info_section.pack(side='left', fill='x', expand=True, padx=(15, 0))
        
        name_label = tk.Label(info_section, text=name, 
                             bg="#fff5f5", fg="#e53e3e",
                             font=('Segoe UI', 12, 'bold'), anchor='w')
        name_label.pack(fill='x')
        
        error_label = tk.Label(info_section, text=f"Fehler: {error[:50]}...", 
                              bg="#fff5f5", fg="#e53e3e",
                              font=('Segoe UI', 9, 'normal'), anchor='w')
        error_label.pack(fill='x', pady=(2, 0))
        
        return card_frame
    
    def get_selected_database_file(self):
        messagebox.showwarning("Warnung", "Bitte auf eine Datenbank-Karte klicken!")
        return None
    
    def open_selected_database(self):
        database_files = list(self.databases_dir.glob("*.enc"))
        if not database_files:
            messagebox.showwarning("Warnung", "Keine Datenbanken gefunden!")
            return
        
        if len(database_files) == 1:
            db_file = database_files[0]
            self.selected_database = str(db_file)
            self.on_database_selected(str(db_file))
        else:
            messagebox.showinfo("Info", "Klicken Sie auf eine Datenbank-Karte zum Öffnen!")
    
    def create_new_database(self):
        db_name = self._ask_string_with_focus("Neue Datenbank", 
                                             "Name für die neue Datenbank:",
                                             initialvalue="Meine_Passwoerter")
        
        if not db_name:
            return
        
        db_name = "".join(c for c in db_name if c.isalnum() or c in (' ', '-', '_')).strip()
        
        if not db_name:
            messagebox.showerror("Fehler", "Ungültiger Datenbankname!")
            return
        
        db_file = self.databases_dir / f"{db_name}.enc"
        if db_file.exists():
            if not messagebox.askyesno("Warnung", 
                                     f"Datenbank '{db_name}' existiert bereits.\n"
                                     "Trotzdem überschreiben?"):
                return
        
        password = self._ask_string_with_focus("Master-Passwort", 
                                              f"Master-Passwort für '{db_name}':",
                                              show='*', show_strength=True)
        if not password:
            return
        
        if len(password) < 8:
            messagebox.showerror("Fehler", "Master-Passwort muss mindestens 8 Zeichen haben!")
            return
        
        confirm = self._ask_string_with_focus("Bestätigung", 
                                             "Master-Passwort wiederholen:",
                                             show='*', show_strength=True)
        if password != confirm:
            messagebox.showerror("Fehler", "Passwörter stimmen nicht überein!")
            return
        
        try:
            from core.password_storage import PasswordManager
            temp_pm = PasswordManager(str(db_file))
            temp_pm.create_new_database(password)
            
            messagebox.showinfo("Erfolg", f"Datenbank '{db_name}' erfolgreich erstellt!")
            self.refresh_database_list()
            
            self.selected_database = str(db_file)
            self.on_database_selected(str(db_file))
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Datenbank konnte nicht erstellt werden:\n{str(e)}")
    
    def import_backup(self):
        file_path = filedialog.askopenfilename(
            title="Backup importieren",
            filetypes=[("Backup-Dateien", "*.bak"), ("Verschlüsselte Dateien", "*.enc"), ("Alle Dateien", "*.*")],
            initialdir=str(self.databases_dir.parent / "backups") if (self.databases_dir.parent / "backups").exists() else str(self.databases_dir)
        )
        
        if not file_path:
            return
        
        import_file = Path(file_path)
        
        if import_file.suffix == '.bak':
            base_name = import_file.stem
            if '_backup_' in base_name:
                base_name = base_name.split('_backup_')[0]
            suggested_name = base_name
        else:
            suggested_name = import_file.stem
        
        db_name = self._ask_string_with_focus("Backup importieren", 
                                             "Name für die importierte Datenbank:",
                                             initialvalue=suggested_name)
        
        if not db_name:
            return
        
        db_name = "".join(c for c in db_name if c.isalnum() or c in (' ', '-', '_')).strip()
        
        if not db_name:
            messagebox.showerror("Fehler", "Ungültiger Datenbankname!")
            return
        
        target_file = self.databases_dir / f"{db_name}.enc"
        
        if target_file.exists():
            if not messagebox.askyesno("Warnung", 
                                     f"Datenbank '{db_name}' existiert bereits.\n"
                                     "Überschreiben?"):
                return
        
        try:
            print(f"📄 Kopiere Backup von {import_file} nach {target_file}")
            shutil.copy2(import_file, target_file)
            
            from core.password_storage import PasswordManager
            test_pm = PasswordManager(str(target_file))
            
            if target_file.stat().st_size < 100:
                target_file.unlink()
                messagebox.showerror("Fehler", "Das Backup scheint beschädigt zu sein (Datei zu klein).")
                return
            
            messagebox.showinfo("Erfolg", 
                               f"Backup erfolgreich als '{db_name}' importiert!\n\n"
                               f"Die Datenbank wurde im data-Ordner gespeichert.\n"
                               f"Sie können sich jetzt mit dem ursprünglichen Master-Passwort anmelden.")
            
            self.refresh_database_list()
            
            if messagebox.askyesno("Datenbank öffnen", 
                                  f"Möchten Sie die importierte Datenbank '{db_name}' jetzt öffnen?"):
                self.selected_database = str(target_file)
                self.on_database_selected(str(target_file))
            
        except Exception as e:
            if target_file.exists():
                try:
                    target_file.unlink()
                except:
                    pass
            messagebox.showerror("Fehler", f"Backup konnte nicht importiert werden:\n{str(e)}")
    
    def delete_database(self):
        messagebox.showwarning("Info", "Klicken Sie auf eine Datenbank-Karte und verwenden Sie das Kontextmenü zum Löschen!")
    
    def _ask_string_with_focus(self, title, prompt, initialvalue="", show=None, show_strength=False):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("500x400" if show_strength else "400x250")
        dialog.configure(bg=WindowsClassicColors.WINDOW_BG)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 200, 
            self.root.winfo_rooty() + 200
        ))
        
        result = [None]
        
        main_frame = create_classic_frame(dialog)
        main_frame.pack(expand=True, fill='both', padx=25, pady=25)
        
        if show_strength:
            title_frame = create_classic_frame(main_frame)
            title_frame.pack(fill='x', pady=(0, 15))
            
            title_icon = tk.Label(title_frame, text="🔐", 
                                 bg=WindowsClassicColors.WINDOW_BG, 
                                 fg="#6ba644",
                                 font=('Segoe UI', 16, 'normal'))
            title_icon.pack(side='left', padx=(0, 8))
            
            title_label = tk.Label(title_frame, text=title, 
                                  bg=WindowsClassicColors.WINDOW_BG, 
                                  fg=WindowsClassicColors.TEXT_PRIMARY,
                                  font=('Segoe UI', 14, 'bold'))
            title_label.pack(side='left')
        
        prompt_label = tk.Label(main_frame, text=prompt,
                               bg=WindowsClassicColors.WINDOW_BG,
                               fg=WindowsClassicColors.TEXT_PRIMARY,
                               font=('Segoe UI', 10, 'normal'))
        prompt_label.pack(pady=(0, 10))
        
        entry = tk.Entry(main_frame, show=show, font=('Segoe UI', 10, 'normal'),
                        bg=WindowsClassicColors.INPUT_BG,
                        fg=WindowsClassicColors.TEXT_PRIMARY,
                        relief='solid', bd=2, width=40)
        entry.pack(pady=(0, 15 if not show_strength else 10))
        
        if initialvalue:
            entry.insert(0, initialvalue)
            entry.select_range(0, tk.END)
        
        if show_strength:
            strength_frame = self._create_strength_visualizer(main_frame, entry)
            strength_frame.pack(fill='x', pady=(0, 15))
        
        button_frame = create_classic_frame(main_frame)
        button_frame.pack()
        
        def on_ok():
            result[0] = entry.get()
            dialog.destroy()
        
        def on_cancel():
            result[0] = None
            dialog.destroy()
        
        cancel_btn = tk.Button(button_frame, text="Abbrechen", command=on_cancel,
                              bg='#e1e1e1', fg='#000000', font=('Segoe UI', 10, 'normal'),
                              relief='raised', bd=1, padx=15, pady=6)
        cancel_btn.pack(side='left', padx=(0, 10))
        
        ok_btn = tk.Button(button_frame, text="OK", command=on_ok,
                          bg='#6ba644', fg='white', font=('Segoe UI', 10, 'bold'),
                          relief='flat', bd=0, padx=15, pady=6)
        ok_btn.pack(side='left')
        
        def create_hover_effect(button, normal_bg, hover_bg):
            def on_enter(event):
                button.config(bg=hover_bg)
            def on_leave(event):
                button.config(bg=normal_bg)
            button.bind('<Enter>', on_enter)
            button.bind('<Leave>', on_leave)
        
        create_hover_effect(cancel_btn, '#e1e1e1', '#d5d5d5')
        create_hover_effect(ok_btn, '#6ba644', '#5a9137')
        
        entry.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())
        
        dialog.after(150, lambda: entry.focus_set())
        dialog.after(200, lambda: entry.focus_force())
        
        dialog.wait_window()
        
        return result[0]
    
    def _create_strength_visualizer(self, parent, entry_widget):
        container = create_classic_frame(parent)
        
        left_frame = create_classic_frame(container)
        left_frame.pack(side='left', fill='both', expand=True)
        
        right_frame = create_classic_frame(container)
        right_frame.pack(side='right', padx=(20, 0))
        
        ring_canvas = tk.Canvas(right_frame, width=80, height=80, 
                               bg=WindowsClassicColors.WINDOW_BG, highlightthickness=0)
        ring_canvas.pack()
        
        strength_text = tk.Label(right_frame, text="SCHWACH",
                                bg=WindowsClassicColors.WINDOW_BG, 
                                fg="#e74c3c",
                                font=('Segoe UI', 8, 'bold'))
        strength_text.pack(pady=(5, 0))
        
        requirements_frame = create_classic_frame(left_frame, "#f8f9fa")
        requirements_frame.configure(relief='solid', bd=1)
        requirements_frame.pack(fill='both', expand=True, padx=(0, 10))
        
        req_title = tk.Label(requirements_frame, text="Anforderungen:",
                            bg="#f8f9fa", fg=WindowsClassicColors.TEXT_PRIMARY,
                            font=('Segoe UI', 9, 'bold'))
        req_title.pack(anchor='w', padx=10, pady=(8, 5))
        
        requirements = [
            "Mindestens 8 Zeichen",
            "Großbuchstaben (A-Z)",
            "Kleinbuchstaben (a-z)",
            "Zahlen (0-9)",
            "Symbole (!@#$%...)"
        ]
        
        req_widgets = []
        for req_text in requirements:
            req_frame = create_classic_frame(requirements_frame, "#f8f9fa")
            req_frame.pack(fill='x', padx=10, pady=1)
            
            check_label = tk.Label(req_frame, text="○",
                                  bg="#f8f9fa", fg="#ccc",
                                  font=('Segoe UI', 10, 'normal'))
            check_label.pack(side='left', padx=(0, 8))
            
            text_label = tk.Label(req_frame, text=req_text,
                                 bg="#f8f9fa", fg="#999",
                                 font=('Segoe UI', 8, 'normal'))
            text_label.pack(side='left')
            
            req_widgets.append((check_label, text_label))
        
        def update_strength(event=None):
            password = entry_widget.get()
            score = calculate_master_password_strength(password)[1]
            
            angle = min(score * 3.6, 360)
            
            ring_canvas.delete("all")
            
            ring_canvas.create_oval(10, 10, 70, 70, outline="#e9ecef", width=6, fill="")
            
            if score > 0:
                if score >= 80:
                    color = "#27ae60"
                    icon = "🛡️"
                    text = "SEHR STARK"
                elif score >= 60:
                    color = "#2ecc71"
                    icon = "🔒"
                    text = "STARK"
                elif score >= 40:
                    color = "#f39c12"
                    icon = "🔓"
                    text = "MITTEL"
                elif score >= 20:
                    color = "#e67e22"
                    icon = "🔒"
                    text = "SCHWACH"
                else:
                    color = "#e74c3c"
                    icon = "⚠️"
                    text = "SCHWACH"
                
                if angle > 0:
                    ring_canvas.create_arc(10, 10, 70, 70, start=90, extent=-angle, 
                                         outline=color, width=6, style="arc")
                
                ring_canvas.create_text(40, 35, text=icon, font=('Segoe UI', 16, 'normal'))
                strength_text.config(text=text, fg=color)
            else:
                ring_canvas.create_text(40, 35, text="🔒", font=('Segoe UI', 16, 'normal'))
                strength_text.config(text="SCHWACH", fg="#e74c3c")
            
            checks = [
                len(password) >= 8,
                any(c.isupper() for c in password),
                any(c.islower() for c in password),
                any(c.isdigit() for c in password),
                any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
            ]
            
            for (check_label, text_label), is_met in zip(req_widgets, checks):
                if is_met:
                    check_label.config(text="✓", fg="#27ae60")
                    text_label.config(fg="#2c3e50")
                else:
                    check_label.config(text="○", fg="#ccc")
                    text_label.config(fg="#999")
        
        entry_widget.bind('<KeyRelease>', update_strength)
        update_strength()
        
        return container


def calculate_master_password_strength(password):
    if not password:
        return "Sehr schwach", 0
    
    score = 0
    
    length = len(password)
    if length >= 12:
        score += 30
    elif length >= 8:
        score += 20
    else:
        score += 5
    
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    if has_lower:
        score += 15
    if has_upper:
        score += 15
    if has_digit:
        score += 15
    if has_symbol:
        score += 20
    
    unique_chars = len(set(password))
    if unique_chars / length > 0.7:
        score += 10
    
    if length >= 16:
        score += 10
    elif length >= 20:
        score += 15
    
    if score >= 85:
        return "Sehr stark", min(score, 100)
    elif score >= 70:
        return "Stark", score
    elif score >= 50:
        return "Mittel", score
    elif score >= 30:
        return "Schwach", score
    else:
        return "Sehr schwach", score