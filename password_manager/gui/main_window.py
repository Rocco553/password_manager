import tkinter as tk
from tkinter import messagebox
import pyperclip
import threading

from core.password_storage import PasswordManager
from core.password_generator import PasswordGenerator
from core.totp_manager import TOTPManager

from gui.login_window import LoginWindow
from gui.password_dialog import PasswordDialog
from gui.generator_dialog import PasswordGeneratorDialog
from gui.database_selector import DatabaseSelector
from gui.auto_lock_manager import AutoLockTimer
from gui.keyboard_shortcuts import KeyboardShortcutManager
from gui.settings_manager import SettingsManager
from gui.settings_dialog import SettingsDialog
from gui.backup_manager import BackupManager
from gui.backup_dialog import BackupDialog
from gui.totp_dialog import TOTPDialog
from gui.security_dashboard_manager import SecurityDashboardManager
from gui.category_manager import CategoryManager
from gui.details_panel import DetailsPanel

from gui.modern_styles import (
    ModernStyles, ModernColors, create_modern_frame,
    create_status_bar, update_status_bar, ModernSpacing
)
from gui.toolbar_manager import ToolbarManager
from gui.table_manager import TableManager
from gui.enhanced_search_manager import EnhancedSearchManager
from gui.enhanced_context_menu import EnhancedContextMenu
from gui.menu_manager import MenuManager
from gui.localization import _, LanguageManager


class PasswordManagerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(_("app_title"))
        self.root.configure(bg=ModernColors.WINDOW_BG)
        
        self.pm = PasswordManager()
        self.password_generator = PasswordGenerator()
        self.totp_manager = TOTPManager()
        self.current_database_path = None
        
        self.settings_manager = SettingsManager()
        self.backup_manager = BackupManager(self.pm, self.settings_manager)
        self.security_dashboard = None
        
        self.clipboard_timer = None
        self.totp_timer = None
        self.status_label = None
        
        self.toolbar_manager = ToolbarManager(self)
        self.table_manager = TableManager(self)
        self.search_manager = EnhancedSearchManager(self)
        self.context_menu_manager = EnhancedContextMenu(self)
        self.menu_manager = MenuManager(self)
        self.category_manager = CategoryManager(self)
        self.details_panel = DetailsPanel(self)
        
        timeout_minutes = self.settings_manager.get("auto_lock_timeout_minutes", 0.75)
        self.auto_lock_timer = AutoLockTimer(self, timeout_minutes=timeout_minutes)
        self.keyboard_manager = KeyboardShortcutManager(self)
        
        ModernStyles.setup_modern_theme()
        self.keyboard_manager.bind_shortcuts(self.root)
        self.show_database_selector()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._setup_activity_tracking()
    
    def _setup_activity_tracking(self):
        def on_activity(event=None):
            if hasattr(self, 'auto_lock_timer') and self.auto_lock_timer.is_running:
                self.auto_lock_timer.reset_activity()
        
        events = ['<Motion>', '<Button>', '<Key>', '<MouseWheel>']
        for event in events:
            self.root.bind(event, on_activity, add='+')
        
        def bind_to_children(widget):
            try:
                for event in events:
                    widget.bind(event, on_activity, add='+')
                for child in widget.winfo_children():
                    bind_to_children(child)
            except:
                pass
        
        self.root.after(500, lambda: bind_to_children(self.root))
    
    def show_database_selector(self):
        if hasattr(self, 'auto_lock_timer'):
            self.auto_lock_timer.stop()
        if self.totp_timer:
            self.root.after_cancel(self.totp_timer)
        
        self.database_selector = DatabaseSelector(self.root, self.on_database_selected)
    
    def on_database_selected(self, database_path):
        self.current_database_path = database_path
        self.pm.database_file = database_path
        self.show_login_screen()
    
    def show_login_screen(self):
        if hasattr(self, 'auto_lock_timer'):
            self.auto_lock_timer.stop()
        if self.totp_timer:
            self.root.after_cancel(self.totp_timer)
        
        db_path = self.pm.database_file or self.current_database_path
        self.login_window = LoginWindow(self.root, self.pm, self.on_login_success, db_path)
    
    def on_login_success(self):
        self.setup_main_screen()
        if hasattr(self, 'auto_lock_timer'):
            self.auto_lock_timer.start()
        self._start_totp_timer()
    
    def _handle_auto_lock(self):
        self.pm.lock_database()
        if self.clipboard_timer:
            self.clipboard_timer.cancel()
        if self.totp_timer:
            self.root.after_cancel(self.totp_timer)
        pyperclip.copy("")
        self.show_login_screen()
        messagebox.showinfo("🔒 Auto-Lock", _("info_auto_lock"))
    
    def setup_main_screen(self):
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
        self.root.configure(bg=ModernColors.WINDOW_BG)
        
        if hasattr(self, 'login_window'):
            self.login_window.clear_screen()
        
        main_frame = create_modern_frame(self.root)
        main_frame.pack(expand=True, fill='both')
        
        self._create_menu_bar()
        self._create_toolbar(main_frame)
        self._create_main_content_with_layout(main_frame)
        self._create_status_bar(main_frame)
        
        self.refresh_password_list()
        self.root.after(200, lambda: self._setup_activity_tracking())
    
    def _create_menu_bar(self):
        self.menu_manager.create_menu_bar(self.root)
    
    def _create_toolbar(self, parent):
        self.toolbar_frame = self.toolbar_manager.create_toolbar(parent)
        self.toolbar_frame.pack(fill='x')
    
    def _create_main_content_with_layout(self, parent):
        content_frame = create_modern_frame(parent, ModernColors.PANEL_BG)
        content_frame.pack(expand=True, fill='both', padx=1, pady=1)
        
        paned_window = tk.PanedWindow(content_frame, orient='horizontal', 
                                     bg=ModernColors.PANEL_BG, 
                                     sashwidth=4, sashrelief='flat')
        paned_window.pack(expand=True, fill='both')
        
        sidebar_frame = self.category_manager.create_sidebar(paned_window)
        paned_window.add(sidebar_frame, minsize=200, width=220, sticky='ns')
        
        main_content_container = create_modern_frame(paned_window, ModernColors.PANEL_BG)
        paned_window.add(main_content_container, minsize=600, sticky='nsew')
        
        table_and_dashboard_paned = tk.PanedWindow(main_content_container, orient='horizontal',
                                                  bg=ModernColors.PANEL_BG,
                                                  sashwidth=4, sashrelief='flat')
        table_and_dashboard_paned.pack(expand=True, fill='both')
        
        table_and_details_container = create_modern_frame(table_and_dashboard_paned, ModernColors.PANEL_BG)
        table_and_dashboard_paned.add(table_and_details_container, minsize=400, sticky='nsew')
        
        table_details_paned = tk.PanedWindow(table_and_details_container, orient='vertical',
                                           bg=ModernColors.PANEL_BG,
                                           sashwidth=4, sashrelief='flat')
        table_details_paned.pack(expand=True, fill='both')
        
        self.table_frame = self.table_manager.create_table(table_details_paned)
        table_details_paned.add(self.table_frame, minsize=300, sticky='nsew')
        
        details_frame = self.details_panel.create_panel(table_details_paned)
        table_details_paned.add(details_frame, minsize=150, height=180, sticky='ew')
        
        self.security_dashboard = SecurityDashboardManager(self)
        dashboard_frame = self.security_dashboard.create_dashboard(table_and_dashboard_paned)
        table_and_dashboard_paned.add(dashboard_frame, minsize=220, width=220, sticky='ns')
        
        self.context_menu_manager.setup_context_menu(self.table_manager.tree)
        
        self.table_manager.tree.bind('<<TreeviewSelect>>', self._on_entry_selection_change)
    
    def _on_entry_selection_change(self, event=None):
        selection = self.table_manager.tree.selection()
        
        if not selection:
            self.details_panel.show_empty_state()
        elif len(selection) == 1:
            entry = self.get_selected_entry()
            self.details_panel.update_entry(entry)
        else:
            self.details_panel.show_multiple_selection(len(selection))
    
    def _create_status_bar(self, parent):
        if self.settings_manager.get("show_status_bar", True):
            status_frame, self.status_label = create_status_bar(parent, _("status_ready"))
            status_frame.pack(fill='x')
        else:
            self.status_label = None
    
    def _start_totp_timer(self):
        self._update_totp_codes()
    
    def _update_totp_codes(self):
        if not self.pm.is_unlocked:
            return
        
        if hasattr(self.table_manager, 'refresh_totp_codes'):
            self.table_manager.refresh_totp_codes()
        
        if hasattr(self.details_panel, 'refresh_totp_codes'):
            self.details_panel.refresh_totp_codes()
        
        self.totp_timer = self.root.after(1000, self._update_totp_codes)
    
    def refresh_password_list(self):
        current_category = self.category_manager.get_current_category()
        
        if current_category == "All":
            all_entries = self.pm.list_entries()
        else:
            all_entries = self.pm.get_entries_by_category(current_category)
        
        self.search_manager.refresh_entries_cache(all_entries)
        
        if hasattr(self.toolbar_manager, 'get_search_term'):
            search_term = self.toolbar_manager.get_search_term()
            if search_term:
                self.perform_search(search_term)
            else:
                self.table_manager.update_table(all_entries)
        else:
            self.table_manager.update_table(all_entries)
        
        self.category_manager.refresh_categories()
        
        if self.security_dashboard:
            self.security_dashboard.refresh_metrics()
        
        self.details_panel.show_empty_state()
    
    def perform_search(self, search_term):
        current_category = self.category_manager.get_current_category()
        
        if current_category == "All":
            entries = self.pm.list_entries()
        else:
            entries = self.pm.get_entries_by_category(current_category)
        
        self.search_manager.refresh_entries_cache(entries)
        self.search_manager.perform_search(search_term)
    
    def get_selected_entry(self):
        if hasattr(self.table_manager, 'get_selected_entry'):
            return self.table_manager.get_selected_entry()
        return None
        
        title = self.table_manager.get_selected_entry_title()
        if not title:
            return None
        
        return self.pm.get_entry(title)
    
    def add_password(self):
        current_category = self.category_manager.get_current_category()
        default_category = current_category if current_category != "All" else "Other"
        
        dialog = PasswordDialog(self.root, _("dialog_add_password"), 
                               password_generator=self.password_generator,
                               category_manager=self.category_manager)
        
        if dialog.result:
            dialog.result['category'] = dialog.result.get('category', default_category)
        
        if hasattr(self.auto_lock_timer, 'register_dialog'):
            self.auto_lock_timer.register_dialog(dialog.dialog)
        
        if dialog.result:
            success = self.pm.add_entry(**dialog.result)
            if success:
                self.refresh_password_list()
                self.create_auto_backup()
                
                if self.status_label:
                    update_status_bar(self.status_label, 
                                    f"✅ {_('status_entry_added')}: {dialog.result['title']}", "success")
            else:
                messagebox.showerror(_("error_title"), 
                                   f"{_('error_title_exists')}")
    
    def edit_password(self):
        entry = self.get_selected_entry()
        if not entry:
            messagebox.showwarning(_("error_warning"), _("error_no_entry_selected"))
            return
        
        dialog = PasswordDialog(self.root, _("dialog_edit_password"), entry, 
                               password_generator=self.password_generator,
                               category_manager=self.category_manager)
        
        if hasattr(self.auto_lock_timer, 'register_dialog'):
            self.auto_lock_timer.register_dialog(dialog.dialog)
        
        if dialog.result:
            entry.update(**dialog.result)
            self.pm.save_database()
            self.refresh_password_list()
            self.create_auto_backup()
            
            if self.status_label:
                update_status_bar(self.status_label, 
                                f"✅ {_('status_entry_updated')}: {dialog.result['title']}", "success")
    
    def delete_password(self):
        entry = self.get_selected_entry()
        if not entry:
            messagebox.showwarning(_("error_warning"), _("error_no_entry_selected"))
            return
        
        if messagebox.askyesno(_("confirm_delete_entry"), 
                              f"{_('confirm_delete_entry')} '{entry.title}'?\n\n{_('confirm_cannot_be_undone')}"):
            if self.pm.delete_entry(entry.title):
                self.refresh_password_list()
                self.create_auto_backup()
                
                if self.status_label:
                    update_status_bar(self.status_label, 
                                    f"🗑️ {_('status_entry_deleted')}: {entry.title}", "info")
    
    def copy_password(self):
        entry = self.get_selected_entry()
        if not entry:
            messagebox.showwarning("Warning", "Please select an entry!")
            return
        
        pyperclip.copy(entry.password)
        
        clear_seconds = self.settings_manager.get("clipboard_clear_seconds", 10)
        clipboard_enabled = self.settings_manager.get("clipboard_clear_enabled", True)
        
        if self.status_label:
            if clipboard_enabled:
                update_status_bar(self.status_label, 
                                f"📋 Password copied - will clear in {clear_seconds}s", "info")
            else:
                update_status_bar(self.status_label, 
                                f"📋 Password copied: {entry.title}", "info")
        
        if clipboard_enabled:
            if self.clipboard_timer:
                self.clipboard_timer.cancel()
            self.clipboard_timer = threading.Timer(clear_seconds, self.clear_clipboard)
            self.clipboard_timer.start()
    
    def clear_clipboard(self):
        pyperclip.copy("")
        if self.status_label:
            update_status_bar(self.status_label, "🧹 Clipboard cleared", "normal")
    
    def open_password_generator(self):
        generator = PasswordGeneratorDialog(self.root, self.password_generator)
        
        if hasattr(self.auto_lock_timer, 'register_dialog'):
            self.auto_lock_timer.register_dialog(generator.dialog)
        
        if generator.result:
            pyperclip.copy(generator.result)
            if self.status_label:
                update_status_bar(self.status_label, 
                                "🎲 Generated password copied to clipboard", "success")
    
    def open_totp_manager(self):
        totp_dialog = TOTPDialog(self.root, self.pm, self.totp_manager)
        
        if hasattr(self.auto_lock_timer, 'register_dialog'):
            self.auto_lock_timer.register_dialog(totp_dialog.dialog)
    
    def open_backup_dialog(self):
        backup_dialog = BackupDialog(self.root, self.backup_manager)
        
        if hasattr(self.auto_lock_timer, 'register_dialog'):
            self.auto_lock_timer.register_dialog(backup_dialog.dialog)
    
    def create_auto_backup(self):
        if self.settings_manager.get("backup_on_save", False):
            success, message = self.backup_manager.create_auto_backup()
            if success and "deaktiviert" not in message:
                if self.status_label:
                    update_status_bar(self.status_label, "💾 Auto-backup created", "success")
    
    def open_settings(self):
        settings_dialog = SettingsDialog(self.root, self.settings_manager, self.on_settings_changed)
        
        if hasattr(self.auto_lock_timer, 'register_dialog'):
            self.auto_lock_timer.register_dialog(settings_dialog.dialog)
    
    def on_settings_changed(self):
        if hasattr(self, 'auto_lock_timer'):
            was_running = self.auto_lock_timer.is_running
            self.auto_lock_timer.stop()
            
            timeout_minutes = self.settings_manager.get("auto_lock_timeout_minutes", 0.75)
            warning_seconds = self.settings_manager.get("auto_lock_warning_seconds", 15)
            
            self.auto_lock_timer = AutoLockTimer(self, timeout_minutes=timeout_minutes)
            self.auto_lock_timer.warning_seconds = warning_seconds
            
            if was_running and self.settings_manager.get("auto_lock_enabled", True):
                self.auto_lock_timer.start()
        
        language_changed = getattr(self, '_language_changed', False)
        if language_changed:
            self._language_changed = False
            messagebox.showinfo(_("settings_title"), 
                               _("settings_restart_required"))
            
            if self.status_label:
                update_status_bar(self.status_label, _("settings_saved"), "success")
        else:
            messagebox.showinfo(_("settings_title"), _("settings_saved"))
            
            if self.status_label:
                update_status_bar(self.status_label, _("settings_saved"), "success")
    
    def switch_database(self):
        self.pm.lock_database()
        if self.clipboard_timer:
            self.clipboard_timer.cancel()
        if self.totp_timer:
            self.root.after_cancel(self.totp_timer)
        pyperclip.copy("")
        self.show_database_selector()
    
    def logout(self):
        current_db = self.pm.database_file
        self.pm.lock_database()
        if self.clipboard_timer:
            self.clipboard_timer.cancel()
        if self.totp_timer:
            self.root.after_cancel(self.totp_timer)
        pyperclip.copy("")
        
        if current_db:
            self.pm.database_file = current_db
            self.current_database_path = current_db
            self.show_login_screen()
        else:
            self.show_database_selector()
    
    def on_closing(self):
        if hasattr(self, 'auto_lock_timer'):
            self.auto_lock_timer.stop()
        
        if self.clipboard_timer:
            self.clipboard_timer.cancel()
        if self.totp_timer:
            self.root.after_cancel(self.totp_timer)
        
        if hasattr(self, 'security_dashboard') and self.security_dashboard:
            self.security_dashboard.destroy()
        
        pyperclip.copy("")
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()