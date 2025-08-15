import tkinter as tk
from gui.modern_styles import (
    ModernColors, create_toolbar_frame, create_toolbar_button, 
    create_toolbar_separator, create_search_frame, ModernSpacing
)
from gui.localization import _


class ToolbarManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.toolbar_frame = None
        self.search_frame = None
        self.search_entry = None
        self.search_clear_btn = None
        
    def create_toolbar(self, parent):
        self.toolbar_frame = create_toolbar_frame(parent)
        
        container = tk.Frame(self.toolbar_frame, bg=ModernColors.TOOLBAR_BG)
        container.pack(fill='both', expand=True, padx=ModernSpacing.TOOLBAR_PADDING, 
                      pady=ModernSpacing.TOOLBAR_PADDING)
        
        self._create_main_actions(container)
        self._create_secondary_actions(container)
        self._create_search_section(container)
        
        return self.toolbar_frame
    
    def _create_main_actions(self, parent):
        main_group = tk.Frame(parent, bg=ModernColors.TOOLBAR_BG)
        main_group.pack(side='left')
        
        new_btn = create_toolbar_button(main_group, _("toolbar_new"), 
                                       self.main_window.add_password, "➕")
        new_btn.pack(side='left', padx=(0, ModernSpacing.BUTTON_SPACING))
        
        edit_btn = create_toolbar_button(main_group, _("toolbar_edit"), 
                                        self.main_window.edit_password, "✏️")
        edit_btn.pack(side='left', padx=ModernSpacing.BUTTON_SPACING)
        
        delete_btn = create_toolbar_button(main_group, _("toolbar_delete"), 
                                          self.main_window.delete_password, "🗑️")
        delete_btn.pack(side='left', padx=ModernSpacing.BUTTON_SPACING)
        
        sep1 = create_toolbar_separator(main_group)
        sep1.pack(side='left', padx=ModernSpacing.MD)
        
        copy_btn = create_toolbar_button(main_group, _("toolbar_copy"), 
                                        self.main_window.copy_password, "📋")
        copy_btn.pack(side='left', padx=ModernSpacing.BUTTON_SPACING)
        
        copy_user_btn = create_toolbar_button(main_group, _("toolbar_user"), 
                                             self._copy_username, "👤")
        copy_user_btn.pack(side='left', padx=ModernSpacing.BUTTON_SPACING)
        
        self._add_tooltips([
            (new_btn, _("tooltip_add_entry")),
            (edit_btn, _("tooltip_edit_entry")),
            (delete_btn, _("tooltip_delete_entry")),
            (copy_btn, _("tooltip_copy_password")),
            (copy_user_btn, _("tooltip_copy_username"))
        ])
    
    def _create_secondary_actions(self, parent):
        secondary_group = tk.Frame(parent, bg=ModernColors.TOOLBAR_BG)
        secondary_group.pack(side='left', padx=(ModernSpacing.XL, 0))
        
        sep2 = create_toolbar_separator(secondary_group)
        sep2.pack(side='left', padx=(0, ModernSpacing.MD))
        
        generator_btn = create_toolbar_button(secondary_group, _("toolbar_generate"), 
                                            self.main_window.open_password_generator, "🎲")
        generator_btn.pack(side='left', padx=ModernSpacing.BUTTON_SPACING)
        
        totp_btn = create_toolbar_button(secondary_group, _("toolbar_2fa"), 
                                        self.main_window.open_totp_manager, "🔐")
        totp_btn.pack(side='left', padx=ModernSpacing.BUTTON_SPACING)
        
        sep3 = create_toolbar_separator(secondary_group)
        sep3.pack(side='left', padx=ModernSpacing.MD)
        
        backup_btn = create_toolbar_button(secondary_group, _("toolbar_backup"), 
                                          self.main_window.open_backup_dialog, "💾")
        backup_btn.pack(side='left', padx=ModernSpacing.BUTTON_SPACING)
        
        settings_btn = create_toolbar_button(secondary_group, _("toolbar_settings"), 
                                           self.main_window.open_settings, "⚙️")
        settings_btn.pack(side='left', padx=ModernSpacing.BUTTON_SPACING)
        
        self._add_tooltips([
            (generator_btn, _("tooltip_password_generator")),
            (totp_btn, _("tooltip_2fa_manager")),
            (backup_btn, _("tooltip_backup_export")),
            (settings_btn, _("tooltip_settings"))
        ])
    
    def _create_search_section(self, parent):
        search_container = tk.Frame(parent, bg=ModernColors.TOOLBAR_BG)
        search_container.pack(side='right')
        
        search_label = tk.Label(search_container, text=_("toolbar_search"),
                               bg=ModernColors.TOOLBAR_BG,
                               fg=ModernColors.TEXT_SECONDARY,
                               font=('Segoe UI', 8, 'normal'))
        search_label.pack(side='left', padx=(0, ModernSpacing.SM))
        
        self.search_frame, self.search_entry, self.search_clear_btn = create_search_frame(search_container)
        self.search_frame.pack(side='left')
        
        self._setup_search_functionality()
    
    def _setup_search_functionality(self):
        self.search_entry.bind('<KeyRelease>', self._on_search_change)
        self.search_clear_btn.bind('<Button-1>', self._clear_search)
        
        self.search_entry.bind('<FocusIn>', self._on_search_focus_in)
        self.search_entry.bind('<FocusOut>', self._on_search_focus_out)
        
        self._set_search_placeholder()
    
    def _set_search_placeholder(self):
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, _("placeholder_search_entries"))
        self.search_entry.configure(fg=ModernColors.TEXT_DISABLED)
        self.search_placeholder_active = True
    
    def _clear_search_placeholder(self):
        if hasattr(self, 'search_placeholder_active') and self.search_placeholder_active:
            self.search_entry.delete(0, tk.END)
            self.search_entry.configure(fg=ModernColors.TEXT_PRIMARY)
            self.search_placeholder_active = False
    
    def _on_search_focus_in(self, event):
        self._clear_search_placeholder()
    
    def _on_search_focus_out(self, event):
        if not self.search_entry.get().strip():
            self._set_search_placeholder()
            if hasattr(self.main_window, 'refresh_password_list'):
                self.main_window.refresh_password_list()
    
    def _on_search_change(self, event):
        if hasattr(self, 'search_placeholder_active') and self.search_placeholder_active:
            return
        
        search_term = self.search_entry.get().strip()
        if hasattr(self.main_window, 'perform_search'):
            self.main_window.perform_search(search_term)
    
    def _clear_search(self, event):
        self._set_search_placeholder()
        if hasattr(self.main_window, 'refresh_password_list'):
            self.main_window.refresh_password_list()
        if hasattr(self.main_window, 'status_label') and self.main_window.status_label:
            from gui.modern_styles import update_status_bar
            update_status_bar(self.main_window.status_label, _("status_search_cleared"), "info")
    
    def _copy_username(self):
        entry = self.main_window.get_selected_entry()
        if not entry:
            from tkinter import messagebox
            messagebox.showwarning(_("error_warning"), _("error_no_entry_selected"))
            return
        
        if entry.username.strip():
            import pyperclip
            pyperclip.copy(entry.username)
            if hasattr(self.main_window, 'status_label') and self.main_window.status_label:
                from gui.modern_styles import update_status_bar
                update_status_bar(self.main_window.status_label, 
                                f"{_('status_username_copied')}: {entry.title}", "info")
        else:
            if hasattr(self.main_window, 'status_label') and self.main_window.status_label:
                from gui.modern_styles import update_status_bar
                update_status_bar(self.main_window.status_label, 
                                _("error_no_username_available"), "warning")
    
    def _add_tooltips(self, button_tooltip_pairs):
        for button, tooltip_text in button_tooltip_pairs:
            self._create_tooltip(button, tooltip_text)
    
    def _create_tooltip(self, widget, text):
        def on_enter(event):
            if hasattr(self.main_window, 'status_label') and self.main_window.status_label:
                from gui.modern_styles import update_status_bar
                update_status_bar(self.main_window.status_label, text, "info")
        
        def on_leave(event):
            if hasattr(self.main_window, 'status_label') and self.main_window.status_label:
                self._update_default_status()
        
        widget.bind('<Enter>', on_enter, add='+')
        widget.bind('<Leave>', on_leave, add='+')
    
    def _update_default_status(self):
        if hasattr(self.main_window, 'pm') and self.main_window.pm:
            entries_count = len(self.main_window.pm.list_entries())
            from gui.modern_styles import update_status_bar
            update_status_bar(self.main_window.status_label, 
                            f"{_('status_ready')} - {entries_count} {_('status_entries')}", "normal")
    
    def focus_search(self):
        if self.search_entry:
            self.search_entry.focus_set()
            self._clear_search_placeholder()
    
    def get_search_term(self):
        if hasattr(self, 'search_placeholder_active') and self.search_placeholder_active:
            return ""
        return self.search_entry.get().strip() if self.search_entry else ""