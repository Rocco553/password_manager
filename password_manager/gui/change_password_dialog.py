import tkinter as tk
from tkinter import messagebox
import threading
from gui.modern_styles import (
    WindowsClassicStyles, WindowsClassicColors, 
    create_classic_frame, create_classic_label_frame, 
    create_classic_entry, ClassicSpacing
)


class ChangePasswordDialog:
    def __init__(self, parent, password_manager):
        self.pm = password_manager
        self.result = None
        self.password_visible = [False, False, False]
        
        WindowsClassicStyles.setup_windows_classic_theme()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Master-Passwort ändern")
        self.dialog.geometry("650x800")
        self.dialog.configure(bg=WindowsClassicColors.WINDOW_BG)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50, 
            parent.winfo_rooty() + 50
        ))
        
        self.dialog.focus_set()
        self.dialog.focus_force()

        self.create_change_password_ui()
        
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
        
        self.dialog.wait_window()
    
    def create_change_password_ui(self):
        main_frame = create_classic_frame(self.dialog, WindowsClassicColors.DIALOG_BG)
        main_frame.pack(expand=True, fill='both')
        
        header_frame = create_classic_frame(main_frame, "#6ba644")
        header_frame.pack(fill='x')
        
        header_content = create_classic_frame(header_frame, "#6ba644")
        header_content.pack(expand=True, fill='x', padx=40, pady=30)
        
        icon_frame = create_classic_frame(header_content, "#5a9137")
        icon_frame.configure(width=60, height=60)
        icon_frame.pack_propagate(False)
        icon_frame.pack(pady=(0, 15))
        
        icon_label = tk.Label(icon_frame, text="🔐", 
                             bg="#5a9137", fg="white", 
                             font=('Segoe UI', 24, 'normal'))
        icon_label.place(relx=0.5, rely=0.5, anchor='center')

        title_label = tk.Label(header_content, text="Master-Passwort ändern",
                               font=('Segoe UI', 18, 'bold'),
                               bg="#6ba644", fg="white")
        title_label.pack()
        
        content_frame = create_classic_frame(main_frame, WindowsClassicColors.DIALOG_BG)
        content_frame.pack(expand=True, fill='both', padx=40, pady=40)
        
        warning_frame = create_classic_frame(content_frame, "#fff3cd")
        warning_frame.configure(relief='solid', bd=1)
        warning_frame.pack(fill='x', pady=(0, 25))
        
        warning_content = create_classic_frame(warning_frame, "#fff3cd")
        warning_content.pack(fill='x', padx=15, pady=15)
        
        warning_icon = tk.Label(warning_content, text="⚠️",
                               bg="#fff3cd", fg="#856404",
                               font=('Segoe UI', 14, 'normal'))
        warning_icon.pack(side='left', padx=(0, 10))
        
        warning_text = tk.Label(warning_content, 
                               text="Wichtig: Nach der Änderung des Master-Passworts müssen Sie sich\n"
                                    "mit dem neuen Passwort erneut anmelden.",
                               bg="#fff3cd", fg="#856404",
                               font=('Segoe UI', 10, 'normal'),
                               justify='left')
        warning_text.pack(side='left')
        
        form_frame = create_classic_label_frame(content_frame, "🔐 Passwort-Änderung")
        form_frame.pack(fill='x', pady=(0, 25))
        
        form_container = create_classic_frame(form_frame, WindowsClassicColors.WINDOW_BG)
        form_container.pack(fill='x', padx=15, pady=15)
        
        self.current_password_entry = self._create_password_field(
            form_container, "Aktuelles Master-Passwort:", 0
        )
        
        separator1 = tk.Frame(form_container, bg=WindowsClassicColors.BORDER, height=1)
        separator1.pack(fill='x', pady=20)
        
        self.new_password_entry = self._create_password_field(
            form_container, "Neues Master-Passwort:", 1
        )
        
        self.confirm_password_entry = self._create_password_field(
            form_container, "Neues Passwort bestätigen:", 2
        )
        
        self.new_password_entry.bind('<KeyRelease>', self._on_password_change)
        self.confirm_password_entry.bind('<KeyRelease>', self._on_password_change)
        
        strength_frame = create_classic_label_frame(content_frame, "📊 Passwort-Stärke")
        strength_frame.pack(fill='x', pady=(0, 25))
        
        self.strength_container = create_classic_frame(strength_frame, WindowsClassicColors.WINDOW_BG)
        self.strength_container.pack(fill='x', padx=15, pady=15)
        
        self._create_strength_visualization()
        
        button_frame = create_classic_frame(content_frame, WindowsClassicColors.DIALOG_BG)
        button_frame.pack(fill='x')
        
        cancel_btn = tk.Button(button_frame, text="Abbrechen",
                              command=self.dialog.destroy,
                              bg="#666666", fg="white", font=('Segoe UI', 11, 'normal'),
                              relief='flat', bd=0, padx=25, pady=12)
        cancel_btn.pack(side='left')
        
        self.change_btn = tk.Button(button_frame, text="🔐 Passwort ändern",
                                   command=self.change_password,
                                   bg="#6ba644", fg="white", font=('Segoe UI', 11, 'bold'),
                                   relief='flat', bd=0, padx=25, pady=12,
                                   state='disabled')
        self.change_btn.pack(side='right')
        
        def create_hover_effect(button, normal_bg, hover_bg):
            def on_enter(event):
                if button['state'] != 'disabled':
                    button.config(bg=hover_bg)
            def on_leave(event):
                if button['state'] != 'disabled':
                    button.config(bg=normal_bg)
            button.bind('<Enter>', on_enter)
            button.bind('<Leave>', on_leave)
        
        create_hover_effect(cancel_btn, "#666666", "#555555")
        create_hover_effect(self.change_btn, "#6ba644", "#5a9137")
        
        self.current_password_entry.focus_set()
    
    def _create_password_field(self, parent, label_text, index):
        field_frame = create_classic_frame(parent, WindowsClassicColors.WINDOW_BG)
        field_frame.pack(fill='x', pady=10)
        
        label = tk.Label(field_frame, text=label_text,
                        bg=WindowsClassicColors.WINDOW_BG,
                        fg=WindowsClassicColors.TEXT_PRIMARY,
                        font=('Segoe UI', 11, 'bold'))
        label.pack(anchor='w', pady=(0, 8))
        
        entry_frame = create_classic_frame(field_frame, WindowsClassicColors.WINDOW_BG)
        entry_frame.pack(fill='x')
        
        entry_container = create_classic_frame(entry_frame, WindowsClassicColors.INPUT_BG)
        entry_container.configure(relief='solid', bd=2)
        entry_container.pack(side='left', fill='x', expand=True)
        
        entry = tk.Entry(entry_container, show='*', 
                        font=('Segoe UI', 12, 'normal'),
                        bg=WindowsClassicColors.INPUT_BG,
                        fg=WindowsClassicColors.TEXT_PRIMARY,
                        relief='flat', bd=0)
        entry.pack(side='left', fill='x', expand=True, padx=8, pady=8)
        
        toggle_container = create_classic_frame(entry_frame, WindowsClassicColors.INPUT_BG)
        toggle_container.configure(width=40, height=40, relief='solid', bd=2)
        toggle_container.pack_propagate(False)
        toggle_container.pack(side='right', padx=(4, 0))
        
        toggle_btn = tk.Button(toggle_container, text="👁️",
                              command=lambda: self._toggle_password_visibility(index, entry),
                              bg=WindowsClassicColors.INPUT_BG, fg=WindowsClassicColors.TEXT_PRIMARY, 
                              font=('Segoe UI', 12, 'normal'),
                              relief='flat', bd=0, cursor='hand2')
        toggle_btn.pack(fill='both', expand=True)
        
        def toggle_hover(event):
            toggle_btn.config(bg='#f0f0f0')
        def toggle_leave(event):
            toggle_btn.config(bg=WindowsClassicColors.INPUT_BG)
        toggle_btn.bind('<Enter>', toggle_hover)
        toggle_btn.bind('<Leave>', toggle_leave)
        
        return entry
    
    def _toggle_password_visibility(self, index, entry):
        if self.password_visible[index]:
            entry.config(show='*')
            self.password_visible[index] = False
        else:
            entry.config(show='')
            self.password_visible[index] = True
            
            timer = threading.Timer(5.0, lambda: self._hide_password_after_timer(index, entry))
            timer.start()
    
    def _hide_password_after_timer(self, index, entry):
        try:
            entry.config(show='*')
            self.password_visible[index] = False
        except:
            pass
    
    def _create_strength_visualization(self):
        strength_info_frame = create_classic_frame(self.strength_container, WindowsClassicColors.WINDOW_BG)
        strength_info_frame.pack(fill='x', pady=(0, 15))
        
        self.strength_label = tk.Label(strength_info_frame, text="Geben Sie ein neues Passwort ein",
                                      bg=WindowsClassicColors.WINDOW_BG,
                                      fg=WindowsClassicColors.TEXT_SECONDARY,
                                      font=('Segoe UI', 11, 'normal'))
        self.strength_label.pack(side='left')
        
        self.score_label = tk.Label(strength_info_frame, text="",
                                   bg=WindowsClassicColors.WINDOW_BG,
                                   fg=WindowsClassicColors.TEXT_SECONDARY,
                                   font=('Segoe UI', 11, 'bold'))
        self.score_label.pack(side='right')
        
        progress_frame = create_classic_frame(self.strength_container, WindowsClassicColors.WINDOW_BG)
        progress_frame.pack(fill='x', pady=(0, 15))
        
        self.progress_bg = tk.Frame(progress_frame, bg='#e9ecef', height=10)
        self.progress_bg.pack(fill='x')
        
        self.progress_fill = tk.Frame(self.progress_bg, bg='#6c757d', height=10)
        self.progress_fill.place(x=0, y=0, width=0, height=10)
        
        requirements_frame = create_classic_frame(self.strength_container, "#f8f9fa")
        requirements_frame.configure(relief='solid', bd=1)
        requirements_frame.pack(fill='x')
        
        req_title = tk.Label(requirements_frame, text="📋 Anforderungen:",
                            bg="#f8f9fa", fg=WindowsClassicColors.TEXT_PRIMARY,
                            font=('Segoe UI', 10, 'bold'))
        req_title.pack(anchor='w', padx=12, pady=(10, 8))
        
        self.requirement_widgets = []
        requirements = [
            "Mindestens 8 Zeichen",
            "Großbuchstaben (A-Z)",
            "Kleinbuchstaben (a-z)",
            "Zahlen (0-9)",
            "Symbole (!@#$%...)"
        ]
        
        for req_text in requirements:
            req_frame = create_classic_frame(requirements_frame, "#f8f9fa")
            req_frame.pack(fill='x', padx=12, pady=2)
            
            check_label = tk.Label(req_frame, text="○",
                                  bg="#f8f9fa", fg="#ccc",
                                  font=('Segoe UI', 12, 'normal'))
            check_label.pack(side='left', padx=(0, 10))
            
            text_label = tk.Label(req_frame, text=req_text,
                                 bg="#f8f9fa", fg="#999",
                                 font=('Segoe UI', 9, 'normal'))
            text_label.pack(side='left')
            
            self.requirement_widgets.append((check_label, text_label))
        
        tk.Frame(requirements_frame, bg="#f8f9fa", height=10).pack()
    
    def _on_password_change(self, event=None):
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        self._update_strength_display(new_password)
        self._update_button_state(new_password, confirm_password)
    
    def _update_strength_display(self, password):
        if not password:
            self.strength_label.config(text="Geben Sie ein neues Passwort ein", 
                                      fg=WindowsClassicColors.TEXT_SECONDARY)
            self.score_label.config(text="")
            self._update_progress_bar(0, '#6c757d')
            self._update_requirements(password)
            return
        
        score = self._calculate_password_strength(password)
        strength_text, color = self._get_strength_info(score)
        
        self.strength_label.config(text=f"Stärke: {strength_text}", fg=color)
        self.score_label.config(text=f"{score}/100", fg=color)
        
        self._update_progress_bar(score, color)
        self._update_requirements(password)
    
    def _calculate_password_strength(self, password):
        if not password:
            return 0
        
        score = 0
        
        if len(password) >= 12:
            score += 25
        elif len(password) >= 8:
            score += 15
        elif len(password) >= 6:
            score += 8
        
        if any(c.islower() for c in password):
            score += 15
        if any(c.isupper() for c in password):
            score += 15
        if any(c.isdigit() for c in password):
            score += 15
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 20
        
        unique_ratio = len(set(password)) / len(password) if password else 0
        if unique_ratio > 0.7:
            score += 10
        
        return min(score, 100)
    
    def _get_strength_info(self, score):
        if score >= 85:
            return "Sehr stark", "#27ae60"
        elif score >= 70:
            return "Stark", "#2ecc71"
        elif score >= 50:
            return "Mittel", "#f39c12"
        elif score >= 30:
            return "Schwach", "#e67e22"
        else:
            return "Sehr schwach", "#e74c3c"
    
    def _update_progress_bar(self, score, color):
        try:
            self.progress_bg.update_idletasks()
            bg_width = self.progress_bg.winfo_width()
            fill_width = int(bg_width * score / 100)
            
            self.progress_fill.config(bg=color)
            self.progress_fill.place(x=0, y=0, width=fill_width, height=10)
        except:
            pass
    
    def _update_requirements(self, password):
        checks = [
            len(password) >= 8,
            any(c.isupper() for c in password),
            any(c.islower() for c in password),
            any(c.isdigit() for c in password),
            any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        ]
        
        for (check_label, text_label), is_met in zip(self.requirement_widgets, checks):
            if is_met:
                check_label.config(text="✓", fg="#27ae60")
                text_label.config(fg="#2c3e50")
            else:
                check_label.config(text="○", fg="#ccc")
                text_label.config(fg="#999")
    
    def _update_button_state(self, new_password, confirm_password):
        current_password = self.current_password_entry.get()
        
        can_change = (
            len(current_password) > 0 and
            len(new_password) >= 8 and
            new_password == confirm_password and
            new_password != current_password
        )
        
        if can_change:
            self.change_btn.config(state='normal', bg='#6ba644')
        else:
            self.change_btn.config(state='disabled', bg='#cccccc')
    
    def change_password(self):
        current_password = self.current_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        if not current_password:
            messagebox.showerror("Fehler", "Bitte geben Sie das aktuelle Master-Passwort ein!")
            return
        
        if len(new_password) < 8:
            messagebox.showerror("Fehler", "Das neue Passwort muss mindestens 8 Zeichen haben!")
            return
        
        if new_password != confirm_password:
            messagebox.showerror("Fehler", "Die neuen Passwörter stimmen nicht überein!")
            return
        
        if new_password == current_password:
            messagebox.showerror("Fehler", "Das neue Passwort muss sich vom aktuellen unterscheiden!")
            return
        
        try:
            temp_pm = type(self.pm)(self.pm.database_file)
            
            if not temp_pm.unlock_database(current_password):
                messagebox.showerror("Fehler", "Das aktuelle Master-Passwort ist falsch!")
                return
            
            from core.encryption import PasswordEncryption
            import json
            import os
            
            entries_data = []
            for entry in temp_pm.list_entries():
                entries_data.append(entry.to_dict())
            
            data = {
                'version': '1.0',
                'entries': entries_data
            }
            
            new_encryptor = PasswordEncryption()
            new_encryptor.setup_encryption(new_password)
            
            json_string = json.dumps(data, indent=2)
            encrypted_data = new_encryptor.encrypt_data(json_string)
            
            backup_file = self.pm.database_file + '.backup_before_password_change'
            import shutil
            shutil.copy2(self.pm.database_file, backup_file)
            
            with open(self.pm.database_file, 'wb') as f:
                f.write(new_encryptor.get_salt())
                f.write(encrypted_data)
            
            self.result = True
            
            messagebox.showinfo("Erfolg", 
                               "Master-Passwort wurde erfolgreich geändert!\n\n"
                               f"Ein Backup der alten Datei wurde erstellt:\n{backup_file}\n\n"
                               "Sie müssen sich jetzt mit dem neuen Passwort anmelden.")
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Master-Passwort nicht ändern:\n{str(e)}")