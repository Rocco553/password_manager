import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from gui.modern_styles import (
    WindowsClassicStyles, WindowsClassicColors, 
    create_classic_frame, create_classic_label_frame, 
    create_classic_entry, ClassicSpacing
)
from gui.localization import _, LanguageManager


class SettingsDialog:
    def __init__(self, parent, settings_manager, on_settings_changed=None):
        self.settings_manager = settings_manager
        self.on_settings_changed = on_settings_changed
        self.temp_settings = {}
        self.language_manager = LanguageManager()
        self.language_changed = False
        
        self.temp_settings = self.settings_manager.settings.copy()
        
        WindowsClassicStyles.setup_windows_classic_theme()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(_("settings_title"))
        self.dialog.geometry("600x650")
        self.dialog.configure(bg=WindowsClassicColors.WINDOW_BG)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 100, 
            parent.winfo_rooty() + 25
        ))
        
        self.dialog.focus_set()
        self.dialog.focus_force()

        self.create_settings_ui()
        self.load_current_settings()
        
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        
        self.dialog.bind('<Return>', lambda e: self.apply_settings())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        self.dialog.wait_window()
    
    def create_settings_ui(self):
        main_frame = create_classic_frame(self.dialog, WindowsClassicColors.DIALOG_BG)
        main_frame.pack(expand=True, fill='both', padx=12, pady=12)
        
        title_frame = create_classic_frame(main_frame, WindowsClassicColors.DIALOG_BG)
        title_frame.pack(fill='x', pady=(0, 16))
        
        icon_label = tk.Label(title_frame, text="⚙️", 
                             bg=WindowsClassicColors.DIALOG_BG, 
                             fg=WindowsClassicColors.ACCENT,
                             font=('Segoe UI', 16, 'normal'))
        icon_label.pack(side='left', padx=(0, 8))
        
        title_label = tk.Label(title_frame, text=_("settings_title"), 
                              bg=WindowsClassicColors.DIALOG_BG, 
                              fg=WindowsClassicColors.TEXT_PRIMARY,
                              font=('Segoe UI', 14, 'bold'))
        title_label.pack(side='left')
        
        self.notebook = ttk.Notebook(main_frame, style='Classic.TNotebook')
        self.notebook.pack(expand=True, fill='both', pady=(0, 16))
        
        self.create_security_tab()
        self.create_interface_tab()
        self.create_advanced_tab()
        
        self.create_button_area(main_frame)
    
    def create_security_tab(self):
        security_frame = create_classic_frame(self.notebook, WindowsClassicColors.WINDOW_BG)
        self.notebook.add(security_frame, text=_("settings_tab_security"))
        
        autolock_frame = create_classic_label_frame(security_frame, _("settings_auto_lock"))
        autolock_frame.pack(fill='x', padx=8, pady=8)
        
        autolock_container = create_classic_frame(autolock_frame, WindowsClassicColors.WINDOW_BG)
        autolock_container.pack(fill='x', padx=8, pady=8)
        
        self.autolock_enabled = tk.BooleanVar()
        autolock_cb = tk.Checkbutton(autolock_container, text=_("settings_auto_lock_enable"),
                                    variable=self.autolock_enabled,
                                    bg=WindowsClassicColors.WINDOW_BG,
                                    fg=WindowsClassicColors.TEXT_PRIMARY,
                                    font=('Segoe UI', 9, 'normal'),
                                    activebackground=WindowsClassicColors.WINDOW_BG,
                                    selectcolor=WindowsClassicColors.INPUT_BG)
        autolock_cb.pack(anchor='w', pady=(0, 8))
        
        timeout_frame = create_classic_frame(autolock_container, WindowsClassicColors.WINDOW_BG)
        timeout_frame.pack(fill='x', pady=4)
        
        tk.Label(timeout_frame, text=_("settings_timeout_minutes"),
                bg=WindowsClassicColors.WINDOW_BG, fg=WindowsClassicColors.TEXT_PRIMARY,
                font=('Segoe UI', 9, 'normal')).pack(side='left')
        
        self.autolock_timeout = tk.DoubleVar()
        timeout_spinbox = tk.Spinbox(timeout_frame, from_=0.25, to=30, increment=0.25,
                                    textvariable=self.autolock_timeout, width=8,
                                    bg=WindowsClassicColors.INPUT_BG, 
                                    fg=WindowsClassicColors.TEXT_PRIMARY)
        timeout_spinbox.pack(side='right')
        
        warning_frame = create_classic_frame(autolock_container, WindowsClassicColors.WINDOW_BG)
        warning_frame.pack(fill='x', pady=4)
        
        tk.Label(warning_frame, text=_("settings_warning_seconds"),
                bg=WindowsClassicColors.WINDOW_BG, fg=WindowsClassicColors.TEXT_PRIMARY,
                font=('Segoe UI', 9, 'normal')).pack(side='left')
        
        self.autolock_warning = tk.IntVar()
        warning_spinbox = tk.Spinbox(warning_frame, from_=5, to=60, increment=5,
                                    textvariable=self.autolock_warning, width=8,
                                    bg=WindowsClassicColors.INPUT_BG,
                                    fg=WindowsClassicColors.TEXT_PRIMARY)
        warning_spinbox.pack(side='right')
        
        clipboard_frame = create_classic_label_frame(security_frame, _("settings_clipboard"))
        clipboard_frame.pack(fill='x', padx=8, pady=8)
        
        clipboard_container = create_classic_frame(clipboard_frame, WindowsClassicColors.WINDOW_BG)
        clipboard_container.pack(fill='x', padx=8, pady=8)
        
        self.clipboard_enabled = tk.BooleanVar()
        clipboard_cb = tk.Checkbutton(clipboard_container, text=_("settings_clipboard_enable"),
                                     variable=self.clipboard_enabled,
                                     bg=WindowsClassicColors.WINDOW_BG,
                                     fg=WindowsClassicColors.TEXT_PRIMARY,
                                     font=('Segoe UI', 9, 'normal'),
                                     activebackground=WindowsClassicColors.WINDOW_BG,
                                     selectcolor=WindowsClassicColors.INPUT_BG)
        clipboard_cb.pack(anchor='w', pady=(0, 8))
        
        clear_frame = create_classic_frame(clipboard_container, WindowsClassicColors.WINDOW_BG)
        clear_frame.pack(fill='x', pady=4)
        
        tk.Label(clear_frame, text=_("settings_clear_after_seconds"),
                bg=WindowsClassicColors.WINDOW_BG, fg=WindowsClassicColors.TEXT_PRIMARY,
                font=('Segoe UI', 9, 'normal')).pack(side='left')
        
        self.clipboard_timer = tk.IntVar()
        clear_spinbox = tk.Spinbox(clear_frame, from_=5, to=300, increment=5,
                                  textvariable=self.clipboard_timer, width=8,
                                  bg=WindowsClassicColors.INPUT_BG,
                                  fg=WindowsClassicColors.TEXT_PRIMARY)
        clear_spinbox.pack(side='right')
    
    def create_interface_tab(self):
        interface_frame = create_classic_frame(self.notebook, WindowsClassicColors.WINDOW_BG)
        self.notebook.add(interface_frame, text=_("settings_tab_interface"))
        
        language_frame = create_classic_label_frame(interface_frame, _("settings_language"))
        language_frame.pack(fill='x', padx=8, pady=8)
        
        language_container = create_classic_frame(language_frame, WindowsClassicColors.WINDOW_BG)
        language_container.pack(fill='x', padx=8, pady=8)
        
        tk.Label(language_container, text=_("settings_select_language"),
                bg=WindowsClassicColors.WINDOW_BG, fg=WindowsClassicColors.TEXT_PRIMARY,
                font=('Segoe UI', 9, 'bold')).pack(anchor='w', pady=(0, 4))
        
        self.language_var = tk.StringVar()
        languages = self.language_manager.get_available_languages()
        
        for code, name in languages:
            rb = tk.Radiobutton(language_container, text=name, variable=self.language_var, value=code,
                               bg=WindowsClassicColors.WINDOW_BG, fg=WindowsClassicColors.TEXT_PRIMARY,
                               font=('Segoe UI', 9, 'normal'),
                               activebackground=WindowsClassicColors.WINDOW_BG,
                               selectcolor=WindowsClassicColors.INPUT_BG,
                               command=self._on_language_change)
            rb.pack(anchor='w', pady=2)
        
        theme_frame = create_classic_label_frame(interface_frame, _("settings_design"))
        theme_frame.pack(fill='x', padx=8, pady=8)
        
        theme_container = create_classic_frame(theme_frame, WindowsClassicColors.WINDOW_BG)
        theme_container.pack(fill='x', padx=8, pady=8)
        
        tk.Label(theme_container, text=_("settings_theme"),
                bg=WindowsClassicColors.WINDOW_BG, fg=WindowsClassicColors.TEXT_PRIMARY,
                font=('Segoe UI', 9, 'bold')).pack(anchor='w', pady=(0, 4))
        
        self.theme_var = tk.StringVar()
        themes = [
            ("windows_classic", _("settings_theme_windows_classic")),
            ("modern", _("settings_theme_modern")),
            ("dark", _("settings_theme_dark"))
        ]
        
        for value, text in themes:
            rb = tk.Radiobutton(theme_container, text=text, variable=self.theme_var, value=value,
                               bg=WindowsClassicColors.WINDOW_BG, fg=WindowsClassicColors.TEXT_PRIMARY,
                               font=('Segoe UI', 9, 'normal'),
                               activebackground=WindowsClassicColors.WINDOW_BG,
                               selectcolor=WindowsClassicColors.INPUT_BG)
            rb.pack(anchor='w', pady=2)
            
            if value != "windows_classic":
                rb.configure(state='disabled', fg=WindowsClassicColors.TEXT_DISABLED)
        
        ui_frame = create_classic_label_frame(interface_frame, _("settings_window"))
        ui_frame.pack(fill='x', padx=8, pady=8)
        
        ui_container = create_classic_frame(ui_frame, WindowsClassicColors.WINDOW_BG)
        ui_container.pack(fill='x', padx=8, pady=8)
        
        self.show_status_bar = tk.BooleanVar()
        self.show_toolbar_icons = tk.BooleanVar()
        self.remember_window_size = tk.BooleanVar()
        
        ui_options = [
            (_("settings_show_status_bar"), self.show_status_bar),
            (_("settings_show_toolbar_icons"), self.show_toolbar_icons),
            (_("settings_remember_window_size"), self.remember_window_size)
        ]
        
        for text, var in ui_options:
            cb = tk.Checkbutton(ui_container, text=text, variable=var,
                               bg=WindowsClassicColors.WINDOW_BG,
                               fg=WindowsClassicColors.TEXT_PRIMARY,
                               font=('Segoe UI', 9, 'normal'),
                               activebackground=WindowsClassicColors.WINDOW_BG,
                               selectcolor=WindowsClassicColors.INPUT_BG)
            cb.pack(anchor='w', pady=2)
    
    def create_advanced_tab(self):
        advanced_frame = create_classic_frame(self.notebook, WindowsClassicColors.WINDOW_BG)
        self.notebook.add(advanced_frame, text=_("settings_tab_advanced"))
        
        startup_frame = create_classic_label_frame(advanced_frame, _("settings_startup"))
        startup_frame.pack(fill='x', padx=8, pady=8)
        
        startup_container = create_classic_frame(startup_frame, WindowsClassicColors.WINDOW_BG)
        startup_container.pack(fill='x', padx=8, pady=8)
        
        self.remember_database = tk.BooleanVar()
        self.start_minimized = tk.BooleanVar()
        
        startup_options = [
            (_("settings_remember_database"), self.remember_database),
            (_("settings_start_minimized"), self.start_minimized)
        ]
        
        for text, var in startup_options:
            cb = tk.Checkbutton(startup_container, text=text, variable=var,
                               bg=WindowsClassicColors.WINDOW_BG,
                               fg=WindowsClassicColors.TEXT_PRIMARY,
                               font=('Segoe UI', 9, 'normal'),
                               activebackground=WindowsClassicColors.WINDOW_BG,
                               selectcolor=WindowsClassicColors.INPUT_BG)
            cb.pack(anchor='w', pady=2)
        
        import_export_frame = create_classic_label_frame(advanced_frame, _("settings_import_export"))
        import_export_frame.pack(fill='x', padx=8, pady=8)
        
        ie_container = create_classic_frame(import_export_frame, WindowsClassicColors.WINDOW_BG)
        ie_container.pack(fill='x', padx=8, pady=8)
        
        button_container = create_classic_frame(ie_container, WindowsClassicColors.WINDOW_BG)
        button_container.pack(fill='x', pady=4)
        
        export_btn = tk.Button(button_container, text=_("settings_export"), 
                              command=self.export_settings,
                              bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                              relief='raised', bd=1, padx=12, pady=4)
        export_btn.pack(side='left', padx=(0, 8))
        
        import_btn = tk.Button(button_container, text=_("settings_import"), 
                              command=self.import_settings,
                              bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                              relief='raised', bd=1, padx=12, pady=4)
        import_btn.pack(side='left', padx=8)
        
        reset_btn = tk.Button(button_container, text=_("settings_reset"), 
                             command=self.reset_to_defaults,
                             bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                             relief='raised', bd=1, padx=12, pady=4)
        reset_btn.pack(side='right')
        
        self._add_hover_effects([export_btn, import_btn, reset_btn])
    
    def create_button_area(self, parent):
        button_frame = create_classic_frame(parent, WindowsClassicColors.DIALOG_BG)
        button_frame.pack(fill='x')
        
        info_label = tk.Label(button_frame, 
                             text=_("settings_automatically_saved"),
                             bg=WindowsClassicColors.DIALOG_BG,
                             fg=WindowsClassicColors.TEXT_SECONDARY,
                             font=('Segoe UI', 8, 'italic'))
        info_label.pack(side='left', anchor='w')
        
        button_container = create_classic_frame(button_frame, WindowsClassicColors.DIALOG_BG)
        button_container.pack(side='right')
        
        cancel_btn = tk.Button(button_container, text=_("button_cancel"), 
                              command=self.cancel,
                              bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                              relief='raised', bd=1, padx=15, pady=6, width=10)
        cancel_btn.pack(side='left', padx=(0, 8))
        
        ok_btn = tk.Button(button_container, text=_("button_ok"), 
                          command=self.apply_settings,
                          bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'bold'),
                          relief='raised', bd=1, padx=15, pady=6, width=10)
        ok_btn.pack(side='left')
        
        self._add_hover_effects([cancel_btn, ok_btn])
    
    def _add_hover_effects(self, buttons):
        def create_hover_effect(button):
            def on_enter(event):
                button.config(bg='#d5d5d5')
            def on_leave(event):
                button.config(bg='#e1e1e1')
            button.bind('<Enter>', on_enter)
            button.bind('<Leave>', on_leave)
        
        for btn in buttons:
            create_hover_effect(btn)
    
    def _on_language_change(self):
        self.language_changed = True
    
    def load_current_settings(self):
        self.autolock_enabled.set(self.temp_settings.get("auto_lock_enabled", True))
        self.autolock_timeout.set(self.temp_settings.get("auto_lock_timeout_minutes", 0.75))
        self.autolock_warning.set(self.temp_settings.get("auto_lock_warning_seconds", 15))
        
        self.clipboard_enabled.set(self.temp_settings.get("clipboard_clear_enabled", True))
        self.clipboard_timer.set(self.temp_settings.get("clipboard_clear_seconds", 10))
        
        self.language_var.set(self.language_manager.get_current_language())
        self.theme_var.set(self.temp_settings.get("theme", "windows_classic"))
        self.show_status_bar.set(self.temp_settings.get("show_status_bar", True))
        self.show_toolbar_icons.set(self.temp_settings.get("show_toolbar_icons", True))
        self.remember_window_size.set(True)
        
        self.remember_database.set(self.temp_settings.get("remember_last_database", True))
        self.start_minimized.set(self.temp_settings.get("start_minimized", False))
    
    def apply_settings(self):
        self.temp_settings.update({
            "auto_lock_enabled": self.autolock_enabled.get(),
            "auto_lock_timeout_minutes": self.autolock_timeout.get(),
            "auto_lock_warning_seconds": self.autolock_warning.get(),
            "clipboard_clear_enabled": self.clipboard_enabled.get(),
            "clipboard_clear_seconds": self.clipboard_timer.get(),
            
            "theme": self.theme_var.get(),
            "show_status_bar": self.show_status_bar.get(),
            "show_toolbar_icons": self.show_toolbar_icons.get(),
            
            "remember_last_database": self.remember_database.get(),
            "start_minimized": self.start_minimized.get()
        })
        
        if self.language_changed:
            new_language = self.language_var.get()
            if self.language_manager.set_language(new_language):
                if hasattr(self.on_settings_changed, '__self__'):
                    self.on_settings_changed.__self__._language_changed = True
        
        self.settings_manager.settings = self.temp_settings.copy()
        self.settings_manager.save_settings()
        
        if self.on_settings_changed:
            self.on_settings_changed()
        
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()
    
    def export_settings(self):
        file_path = filedialog.asksaveasfilename(
            title=_("settings_export"),
            defaultextension=".json",
            filetypes=[(_("file_types_json"), "*.json"), (_("file_types_all"), "*.*")]
        )
        
        if file_path:
            if self.settings_manager.export_settings(file_path):
                messagebox.showinfo(_("settings_export"), _("export_json_success") + file_path)
            else:
                messagebox.showerror(_("settings_export"), _("export_json_error"))
    
    def import_settings(self):
        file_path = filedialog.askopenfilename(
            title=_("settings_import"),
            filetypes=[(_("file_types_json"), "*.json"), (_("file_types_all"), "*.*")]
        )
        
        if file_path:
            if messagebox.askyesno(_("settings_import"), _("confirm_import_backup")):
                if self.settings_manager.import_settings(file_path):
                    messagebox.showinfo(_("settings_import"), _("import_csv_success"))
                    self.load_current_settings()
                else:
                    messagebox.showerror(_("settings_import"), _("import_csv_error"))
    
    def reset_to_defaults(self):
        if messagebox.askyesno(_("settings_reset"), _("settings_reset")):
            self.settings_manager.reset_to_defaults()
            self.temp_settings = self.settings_manager.settings.copy()
            self.load_current_settings()
            messagebox.showinfo(_("settings_reset"), _("settings_reset"))