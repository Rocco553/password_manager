import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import webbrowser
import threading
from datetime import datetime
from gui.modern_styles import ModernColors, create_modern_frame, create_modern_text, ModernSpacing
from gui.localization import _

class DetailsPanel:
    def __init__(self, main_window):
        self.main_window = main_window
        self.panel_frame = None
        self.notebook = None
        self.current_entry = None
        self.panel_visible = True
        self.password_visible = False
        self.password_timer = None
        
        self.general_widgets = {}
        self.security_widgets = {}
        self.notes_widget = None
    
    def create_panel(self, parent):
        self.panel_frame = create_modern_frame(parent, ModernColors.PANEL_BG, relief='solid')
        self.panel_frame.configure(height=180, bd=1, borderwidth=1)
        
        header_frame = create_modern_frame(self.panel_frame, ModernColors.PANEL_BG)
        header_frame.pack(fill='x', padx=8, pady=(4, 0))
        
        title_label = tk.Label(header_frame, text="📋 Entry Details",
                              bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_PRIMARY,
                              font=('Segoe UI', 9, 'bold'))
        title_label.pack(side='left')
        
        self.notebook = ttk.Notebook(self.panel_frame, style='Modern.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=4, pady=4)
        
        self._create_general_tab()
        self._create_security_tab()
        self._create_notes_tab()
        
        self.show_empty_state()
        
        return self.panel_frame
    
    def _create_general_tab(self):
        general_frame = create_modern_frame(self.notebook, ModernColors.PANEL_BG)
        self.notebook.add(general_frame, text='General')
        
        content_frame = create_modern_frame(general_frame, ModernColors.PANEL_BG)
        content_frame.pack(fill='both', expand=True, padx=8, pady=4)
        
        left_frame = create_modern_frame(content_frame, ModernColors.PANEL_BG)
        left_frame.pack(side='left', fill='both', expand=True)
        
        right_frame = create_modern_frame(content_frame, ModernColors.PANEL_BG)
        right_frame.pack(side='right', fill='y', padx=(8, 0))
        
        self._create_field_row(left_frame, "👤 Username:", "username")
        self._create_field_row(left_frame, "🌐 URL:", "url")
        self._create_field_row(left_frame, "🔑 Password:", "password", is_password=True)
        self._create_field_row(left_frame, "🔐 2FA:", "totp")
        
        self._create_action_buttons(right_frame)
    
    def _create_field_row(self, parent, label_text, field_name, is_password=False):
        row_frame = create_modern_frame(parent, ModernColors.PANEL_BG)
        row_frame.pack(fill='x', pady=1)
        
        label = tk.Label(row_frame, text=label_text,
                        bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_PRIMARY,
                        font=('Segoe UI', 8, 'normal'), width=12, anchor='w')
        label.pack(side='left')
        
        value_frame = create_modern_frame(row_frame, ModernColors.PANEL_BG)
        value_frame.pack(side='left', fill='x', expand=True)
        
        if is_password:
            value_label = tk.Label(value_frame, text="••••••••",
                                  bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_SECONDARY,
                                  font=('Segoe UI', 8, 'normal'), anchor='w')
            value_label.pack(side='left', fill='x', expand=True)
            
            toggle_btn = tk.Button(value_frame, text="👁️", width=3,
                                  command=self._toggle_password_visibility,
                                  bg=ModernColors.BUTTON_BG, fg=ModernColors.TEXT_PRIMARY,
                                  font=('Segoe UI', 7, 'normal'),
                                  relief='flat', bd=1, padx=2, pady=1)
            toggle_btn.pack(side='right', padx=(4, 0))
            
            self.general_widgets[field_name] = {'label': value_label, 'toggle': toggle_btn}
        else:
            value_label = tk.Label(value_frame, text="",
                                  bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_SECONDARY,
                                  font=('Segoe UI', 8, 'normal'), anchor='w')
            value_label.pack(fill='x', expand=True)
            
            self.general_widgets[field_name] = {'label': value_label}
        
        copy_btn = tk.Button(row_frame, text="📋", width=3,
                            command=lambda fn=field_name: self._copy_field(fn),
                            bg=ModernColors.BUTTON_BG, fg=ModernColors.TEXT_PRIMARY,
                            font=('Segoe UI', 7, 'normal'),
                            relief='flat', bd=1, padx=2, pady=1)
        copy_btn.pack(side='right', padx=(4, 0))
        
        self.general_widgets[field_name]['copy'] = copy_btn
    
    def _create_action_buttons(self, parent):
        buttons_frame = create_modern_frame(parent, ModernColors.PANEL_BG)
        buttons_frame.pack(fill='y')
        
        self.open_url_btn = tk.Button(buttons_frame, text="🌐\nOpen",
                                     command=self._open_url,
                                     bg=ModernColors.BUTTON_BG, fg=ModernColors.TEXT_PRIMARY,
                                     font=('Segoe UI', 7, 'normal'),
                                     relief='raised', bd=1, width=8, height=3)
        self.open_url_btn.pack(pady=2)
        
        self.edit_btn = tk.Button(buttons_frame, text="✏️\nEdit",
                                 command=self._edit_entry,
                                 bg=ModernColors.BUTTON_BG, fg=ModernColors.TEXT_PRIMARY,
                                 font=('Segoe UI', 7, 'normal'),
                                 relief='raised', bd=1, width=8, height=3)
        self.edit_btn.pack(pady=2)
        
        for btn in [self.open_url_btn, self.edit_btn]:
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=ModernColors.BUTTON_HOVER))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg=ModernColors.BUTTON_BG))
    
    def _create_security_tab(self):
        security_frame = create_modern_frame(self.notebook, ModernColors.PANEL_BG)
        self.notebook.add(security_frame, text='Security')
        
        content_frame = create_modern_frame(security_frame, ModernColors.PANEL_BG)
        content_frame.pack(fill='both', expand=True, padx=8, pady=4)
        
        strength_frame = create_modern_frame(content_frame, ModernColors.PANEL_BG)
        strength_frame.pack(fill='x', pady=2)
        
        tk.Label(strength_frame, text="🔒 Strength:",
                bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_PRIMARY,
                font=('Segoe UI', 8, 'normal'), width=12, anchor='w').pack(side='left')
        
        self.security_widgets['strength_label'] = tk.Label(strength_frame, text="",
                                                          bg=ModernColors.PANEL_BG,
                                                          font=('Segoe UI', 8, 'bold'), anchor='w')
        self.security_widgets['strength_label'].pack(side='left', fill='x', expand=True)
        
        dates_frame = create_modern_frame(content_frame, ModernColors.PANEL_BG)
        dates_frame.pack(fill='x', pady=2)
        
        tk.Label(dates_frame, text="📅 Created:",
                bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_PRIMARY,
                font=('Segoe UI', 8, 'normal'), width=12, anchor='w').pack(side='left')
        
        self.security_widgets['created_label'] = tk.Label(dates_frame, text="",
                                                         bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_SECONDARY,
                                                         font=('Segoe UI', 8, 'normal'), anchor='w')
        self.security_widgets['created_label'].pack(side='left', fill='x', expand=True)
        
        modified_frame = create_modern_frame(content_frame, ModernColors.PANEL_BG)
        modified_frame.pack(fill='x', pady=2)
        
        tk.Label(modified_frame, text="✏️ Modified:",
                bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_PRIMARY,
                font=('Segoe UI', 8, 'normal'), width=12, anchor='w').pack(side='left')
        
        self.security_widgets['modified_label'] = tk.Label(modified_frame, text="",
                                                          bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_SECONDARY,
                                                          font=('Segoe UI', 8, 'normal'), anchor='w')
        self.security_widgets['modified_label'].pack(side='left', fill='x', expand=True)
        
        age_frame = create_modern_frame(content_frame, ModernColors.PANEL_BG)
        age_frame.pack(fill='x', pady=2)
        
        tk.Label(age_frame, text="⏰ Age:",
                bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_PRIMARY,
                font=('Segoe UI', 8, 'normal'), width=12, anchor='w').pack(side='left')
        
        self.security_widgets['age_label'] = tk.Label(age_frame, text="",
                                                     bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_SECONDARY,
                                                     font=('Segoe UI', 8, 'normal'), anchor='w')
        self.security_widgets['age_label'].pack(side='left', fill='x', expand=True)
    
    def _create_notes_tab(self):
        notes_frame = create_modern_frame(self.notebook, ModernColors.PANEL_BG)
        self.notebook.add(notes_frame, text='Notes')
        
        self.notes_widget = create_modern_text(notes_frame, height=6)
        self.notes_widget.pack(fill='both', expand=True, padx=4, pady=4)
        self.notes_widget.config(state='disabled')
    
    def update_entry(self, entry):
        self.current_entry = entry
        
        if self.password_timer:
            self.password_timer.cancel()
            self.password_timer = None
            self.password_visible = False
        
        if entry is None:
            self.show_empty_state()
            return
        
        self._update_general_tab(entry)
        self._update_security_tab(entry)
        self._update_notes_tab(entry)
    
    def _update_general_tab(self, entry):
        self.general_widgets['username']['label'].config(text=entry.username or "(none)")
        self.general_widgets['url']['label'].config(text=entry.url or "(none)")
        
        if not self.password_visible:
            self.general_widgets['password']['label'].config(text="••••••••")
            self.general_widgets['password']['toggle'].config(text="👁️")
        
        if entry.has_totp():
            if hasattr(self.main_window, 'totp_manager'):
                current_code, remaining_time = self.main_window.totp_manager.get_current_totp(entry.totp_secret)
                if current_code:
                    self.general_widgets['totp']['label'].config(text=f"{current_code} ({remaining_time}s)")
                else:
                    self.general_widgets['totp']['label'].config(text="Error generating code")
            else:
                self.general_widgets['totp']['label'].config(text="Enabled")
        else:
            self.general_widgets['totp']['label'].config(text="Disabled")
        
        self.open_url_btn.config(state='normal' if entry.url.strip() else 'disabled')
    
    def _update_security_tab(self, entry):
        if hasattr(self.main_window, 'password_generator'):
            strength, score = self.main_window.password_generator.calculate_password_strength(entry.password)
            color = self._get_strength_color(score)
            self.security_widgets['strength_label'].config(text=f"{strength} ({score}/100)", fg=color)
        else:
            self.security_widgets['strength_label'].config(text="Unknown")
        
        created_date = self._format_date(entry.created)
        modified_date = self._format_date(entry.modified)
        age_days = self._calculate_age_days(entry.created)
        
        self.security_widgets['created_label'].config(text=created_date)
        self.security_widgets['modified_label'].config(text=modified_date)
        self.security_widgets['age_label'].config(text=f"{age_days} days")
    
    def _update_notes_tab(self, entry):
        self.notes_widget.config(state='normal')
        self.notes_widget.delete('1.0', tk.END)
        if entry.notes.strip():
            self.notes_widget.insert('1.0', entry.notes)
        else:
            self.notes_widget.insert('1.0', "(no notes)")
        self.notes_widget.config(state='disabled')
    
    def show_empty_state(self):
        for field_widgets in self.general_widgets.values():
            field_widgets['label'].config(text="")
        
        for widget in self.security_widgets.values():
            widget.config(text="")
        
        if self.notes_widget:
            self.notes_widget.config(state='normal')
            self.notes_widget.delete('1.0', tk.END)
            self.notes_widget.insert('1.0', "Select an entry to view details")
            self.notes_widget.config(state='disabled')
        
        if hasattr(self, 'open_url_btn'):
            self.open_url_btn.config(state='disabled')
    
    def show_multiple_selection(self, count):
        for field_widgets in self.general_widgets.values():
            field_widgets['label'].config(text="")
        
        for widget in self.security_widgets.values():
            widget.config(text="")
        
        if self.notes_widget:
            self.notes_widget.config(state='normal')
            self.notes_widget.delete('1.0', tk.END)
            self.notes_widget.insert('1.0', f"Multiple entries selected ({count})")
            self.notes_widget.config(state='disabled')
        
        if hasattr(self, 'open_url_btn'):
            self.open_url_btn.config(state='disabled')
    
    def _toggle_password_visibility(self):
        if not self.current_entry:
            return
        
        if self.password_timer:
            self.password_timer.cancel()
            self.password_timer = None
        
        if not self.password_visible:
            self.general_widgets['password']['label'].config(text=self.current_entry.password)
            self.general_widgets['password']['toggle'].config(text="🙈")
            self.password_visible = True
            
            self.password_timer = threading.Timer(5.0, self._hide_password_after_timer)
            self.password_timer.start()
        else:
            self._hide_password_after_timer()
    
    def _hide_password_after_timer(self):
        if self.current_entry:
            self.general_widgets['password']['label'].config(text="••••••••")
            self.general_widgets['password']['toggle'].config(text="👁️")
            self.password_visible = False
        
        if self.password_timer:
            self.password_timer = None
    
    def _copy_field(self, field_name):
        if not self.current_entry:
            return
        
        value = ""
        if field_name == "username":
            value = self.current_entry.username
        elif field_name == "url":
            value = self.current_entry.url
        elif field_name == "password":
            value = self.current_entry.password
        elif field_name == "totp":
            if self.current_entry.has_totp() and hasattr(self.main_window, 'totp_manager'):
                current_code, _ = self.main_window.totp_manager.get_current_totp(self.current_entry.totp_secret)
                value = current_code or ""
        
        if value:
            pyperclip.copy(value)
            
            if field_name == "password":
                self._start_clipboard_timer()
            
            if hasattr(self.main_window, 'status_label') and self.main_window.status_label:
                from gui.modern_styles import update_status_bar
                update_status_bar(self.main_window.status_label, 
                                f"{field_name.title()} copied", "info")
    
    def _start_clipboard_timer(self):
        if hasattr(self.main_window, 'settings_manager'):
            clear_seconds = self.main_window.settings_manager.get("clipboard_clear_seconds", 10)
            clipboard_enabled = self.main_window.settings_manager.get("clipboard_clear_enabled", True)
            
            if clipboard_enabled:
                if hasattr(self.main_window, 'clipboard_timer') and self.main_window.clipboard_timer:
                    self.main_window.clipboard_timer.cancel()
                
                self.main_window.clipboard_timer = threading.Timer(clear_seconds, self.main_window.clear_clipboard)
                self.main_window.clipboard_timer.start()
    
    def _open_url(self):
        if not self.current_entry or not self.current_entry.url.strip():
            return
        
        url = self.current_entry.url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open URL:\n{str(e)}")
    
    def _edit_entry(self):
        if hasattr(self.main_window, 'edit_password'):
            self.main_window.edit_password()
    
    def _format_date(self, date_str):
        if not date_str:
            return "Unknown"
        
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%d.%m.%Y %H:%M")
        except:
            return date_str[:19].replace('T', ' ') if len(date_str) >= 19 else date_str
    
    def _calculate_age_days(self, created_str):
        if not created_str:
            return 0
        
        try:
            created_dt = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
            age = datetime.now() - created_dt.replace(tzinfo=None)
            return age.days
        except:
            return 0
    
    def _get_strength_color(self, score):
        if score >= 80:
            return ModernColors.SUCCESS
        elif score >= 60:
            return ModernColors.WARNING
        elif score >= 40:
            return "#e67e22"
        else:
            return ModernColors.ERROR
    
    def toggle_panel(self):
        self.panel_visible = not self.panel_visible
        if self.panel_frame:
            if self.panel_visible:
                self.panel_frame.pack(side='bottom', fill='x')
            else:
                self.panel_frame.pack_forget()
    
    def refresh_totp_codes(self):
        if self.current_entry and self.current_entry.has_totp():
            self._update_general_tab(self.current_entry)