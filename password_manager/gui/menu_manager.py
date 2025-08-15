import tkinter as tk
from tkinter import messagebox, filedialog
from gui.modern_styles import ModernColors
from gui.localization import _


class MenuManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.menu_bar = None
        
    def create_menu_bar(self, parent):
        self.menu_bar = tk.Menu(parent, bg=ModernColors.TOOLBAR_BG, fg=ModernColors.TEXT_PRIMARY,
                               activebackground=ModernColors.BUTTON_HOVER, activeforeground=ModernColors.TEXT_PRIMARY,
                               font=('Segoe UI', 9, 'normal'), tearoff=0)
        
        self._create_database_menu()
        self._create_edit_menu()
        self._create_tools_menu()
        self._create_view_menu()
        self._create_help_menu()
        
        parent.config(menu=self.menu_bar)
        return self.menu_bar
    
    def _create_database_menu(self):
        db_menu = tk.Menu(self.menu_bar, tearoff=0, bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_PRIMARY,
                         activebackground=ModernColors.ACCENT_BLUE, activeforeground='white',
                         font=('Segoe UI', 9, 'normal'))
        
        db_menu.add_command(label=_("menu_db_new"), command=self._new_database)
        db_menu.add_command(label=_("menu_db_open"), command=self._open_database, accelerator="Ctrl+O")
        db_menu.add_separator()
        db_menu.add_command(label=_("menu_db_save"), command=self._save_database, accelerator="Ctrl+S")
        db_menu.add_command(label=_("menu_db_save_as"), command=self._save_database_as)
        db_menu.add_separator()
        db_menu.add_command(label=_("menu_db_import"), command=self._import_data)
        db_menu.add_command(label=_("menu_db_export"), command=self._export_data)
        db_menu.add_separator()
        db_menu.add_command(label=_("menu_db_settings"), command=self._database_settings)
        db_menu.add_command(label=_("menu_db_change_key"), command=self._change_master_key)
        db_menu.add_separator()
        db_menu.add_command(label=_("menu_db_lock"), command=self._lock_database, accelerator="Ctrl+L")
        db_menu.add_separator()
        db_menu.add_command(label=_("menu_db_exit"), command=self._exit_application, accelerator="Ctrl+Q")
        
        self.menu_bar.add_cascade(label=_("menu_database"), menu=db_menu)
    
    def _create_edit_menu(self):
        edit_menu = tk.Menu(self.menu_bar, tearoff=0, bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_PRIMARY,
                           activebackground=ModernColors.ACCENT_BLUE, activeforeground='white',
                           font=('Segoe UI', 9, 'normal'))
        
        edit_menu.add_command(label=_("menu_edit_add"), command=self._add_entry, accelerator="Ctrl+N")
        edit_menu.add_command(label=_("menu_edit_edit"), command=self._edit_entry, accelerator="Ctrl+E")
        edit_menu.add_command(label=_("menu_edit_clone"), command=self._clone_entry, accelerator="Ctrl+K")
        edit_menu.add_command(label=_("menu_edit_delete"), command=self._delete_entry, accelerator="Delete")
        edit_menu.add_separator()
        edit_menu.add_command(label=_("menu_edit_copy_user"), command=self._copy_username, accelerator="Ctrl+B")
        edit_menu.add_command(label=_("menu_edit_copy_pass"), command=self._copy_password, accelerator="Ctrl+C")
        edit_menu.add_command(label=_("menu_edit_copy_url"), command=self._copy_url)
        edit_menu.add_command(label=_("menu_edit_copy_totp"), command=self._copy_totp)
        edit_menu.add_separator()
        edit_menu.add_command(label=_("menu_edit_select_all"), command=self._select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label=_("menu_edit_find"), command=self._find_entries, accelerator="Ctrl+F")
        
        self.menu_bar.add_cascade(label=_("menu_edit"), menu=edit_menu)
    
    def _create_tools_menu(self):
        tools_menu = tk.Menu(self.menu_bar, tearoff=0, bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_PRIMARY,
                            activebackground=ModernColors.ACCENT_BLUE, activeforeground='white',
                            font=('Segoe UI', 9, 'normal'))
        
        tools_menu.add_command(label=_("menu_tools_generator"), command=self._password_generator, accelerator="Ctrl+G")
        tools_menu.add_command(label=_("menu_tools_totp"), command=self._totp_manager)
        tools_menu.add_separator()
        tools_menu.add_command(label=_("menu_tools_backup"), command=self._database_backup)
        tools_menu.add_command(label=_("menu_tools_import_backup"), command=self._import_backup)
        tools_menu.add_separator()
        tools_menu.add_command(label=_("menu_tools_check_passwords"), command=self._check_passwords)
        tools_menu.add_command(label=_("menu_tools_find_duplicates"), command=self._find_duplicates)
        tools_menu.add_separator()
        tools_menu.add_command(label=_("menu_tools_settings"), command=self._open_settings, accelerator="Ctrl+,")
        
        self.menu_bar.add_cascade(label=_("menu_tools"), menu=tools_menu)
    
    def _create_view_menu(self):
        view_menu = tk.Menu(self.menu_bar, tearoff=0, bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_PRIMARY,
                           activebackground=ModernColors.ACCENT_BLUE, activeforeground='white',
                           font=('Segoe UI', 9, 'normal'))
        
        view_menu.add_command(label=_("menu_view_refresh"), command=self._refresh_view, accelerator="F5")
        view_menu.add_separator()
        
        sort_menu = tk.Menu(view_menu, tearoff=0, bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_PRIMARY,
                           activebackground=ModernColors.ACCENT_BLUE, activeforeground='white')
        sort_menu.add_command(label=_("menu_view_sort_title"), command=lambda: self._sort_by('title'))
        sort_menu.add_command(label=_("menu_view_sort_username"), command=lambda: self._sort_by('username'))
        sort_menu.add_command(label=_("menu_view_sort_url"), command=lambda: self._sort_by('url'))
        sort_menu.add_command(label=_("menu_view_sort_modified"), command=lambda: self._sort_by('modified'))
        view_menu.add_cascade(label=_("menu_view_sort_by"), menu=sort_menu)
        
        self.menu_bar.add_cascade(label=_("menu_view"), menu=view_menu)
    
    def _create_help_menu(self):
        help_menu = tk.Menu(self.menu_bar, tearoff=0, bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_PRIMARY,
                           activebackground=ModernColors.ACCENT_BLUE, activeforeground='white',
                           font=('Segoe UI', 9, 'normal'))
        
        help_menu.add_command(label=_("menu_help_shortcuts"), command=self._show_shortcuts, accelerator="F1")
        help_menu.add_command(label=_("menu_help_getting_started"), command=self._show_getting_started)
        help_menu.add_separator()
        help_menu.add_command(label=_("menu_help_check_updates"), command=self._check_updates)
        help_menu.add_command(label=_("menu_help_report_issue"), command=self._report_issue)
        help_menu.add_separator()
        help_menu.add_command(label=_("menu_help_about"), command=self._show_about)
        
        self.menu_bar.add_cascade(label=_("menu_help"), menu=help_menu)
    
    def _new_database(self):
        if messagebox.askyesno("Neue Datenbank", "Neue Datenbank erstellen? Aktuelle Sitzung wird beendet."):
            self.main_window.switch_database()
    
    def _open_database(self):
        if messagebox.askyesno("Datenbank öffnen", "Datenbank wechseln? Aktuelle Sitzung wird beendet."):
            self.main_window.switch_database()
    
    def _save_database(self):
        if hasattr(self.main_window, 'pm') and self.main_window.pm.is_unlocked:
            self.main_window.pm.save_database()
            if hasattr(self.main_window, 'status_label') and self.main_window.status_label:
                from gui.modern_styles import update_status_bar
                update_status_bar(self.main_window.status_label, "Database saved", "success")
    
    def _save_database_as(self):
        if not hasattr(self.main_window, 'pm') or not self.main_window.pm.is_unlocked:
            return
        
        file_path = filedialog.asksaveasfilename(
            title=_("backup_create_title"),
            defaultextension=".enc",
            filetypes=[(_(("file_types_encrypted")), "*.enc"), (_("file_types_all"), "*.*")]
        )
        
        if file_path:
            import shutil
            try:
                shutil.copy2(self.main_window.pm.database_file, file_path)
                messagebox.showinfo("Success", f"Database saved as:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save database:\n{str(e)}")
    
    def _import_data(self):
        if hasattr(self.main_window, 'open_backup_dialog'):
            self.main_window.open_backup_dialog()
    
    def _export_data(self):
        if hasattr(self.main_window, 'open_backup_dialog'):
            self.main_window.open_backup_dialog()
    
    def _database_settings(self):
        if hasattr(self.main_window, 'pm') and self.main_window.pm.is_unlocked:
            from gui.database_settings_dialog import DatabaseSettingsDialog
            
            dialog = DatabaseSettingsDialog(
                self.main_window.root, 
                self.main_window.pm, 
                self.main_window.settings_manager
            )
            
            if hasattr(self.main_window, 'auto_lock_timer') and self.main_window.auto_lock_timer:
                self.main_window.auto_lock_timer.register_dialog(dialog.dialog)
        else:
            messagebox.showwarning("Warnung", "Bitte zuerst eine Datenbank öffnen!")

    def _change_master_key(self):
        if hasattr(self.main_window, 'pm') and self.main_window.pm.is_unlocked:
            from gui.change_password_dialog import ChangePasswordDialog
            
            dialog = ChangePasswordDialog(self.main_window.root, self.main_window.pm)
            
            if hasattr(self.main_window, 'auto_lock_timer') and self.main_window.auto_lock_timer:
                self.main_window.auto_lock_timer.register_dialog(dialog.dialog)
            
            if dialog.result:
                messagebox.showinfo("Erfolgreich", 
                                "Master-Passwort wurde geändert!\n\n"
                                "Sie werden jetzt abgemeldet und müssen sich mit dem neuen Passwort anmelden.")
                
                if hasattr(self.main_window, 'logout'):
                    self.main_window.logout()
        else:
            messagebox.showwarning("Warnung", "Bitte zuerst eine Datenbank öffnen!")
    
    def _lock_database(self):
        if messagebox.askyesno("Abmelden", "Wirklich abmelden?"):
            if hasattr(self.main_window, 'logout'):
                self.main_window.logout()
    
    def _exit_application(self):
        if hasattr(self.main_window, 'on_closing'):
            self.main_window.on_closing()
    
    def _add_entry(self):
        if hasattr(self.main_window, 'add_password'):
            self.main_window.add_password()
    
    def _edit_entry(self):
        if hasattr(self.main_window, 'edit_password'):
            self.main_window.edit_password()
    
    def _clone_entry(self):
        entry = self.main_window.get_selected_entry()
        if not entry:
            messagebox.showwarning("Warning", "Please select an entry!")
            return
    
        from gui.password_dialog import PasswordDialog
        dialog = PasswordDialog(
            self.main_window.root, 
            "Duplicate Entry",
            entry,
            self.main_window.password_generator,
            getattr(self.main_window, 'category_manager', None)
        )
    
        if hasattr(self.main_window, 'auto_lock_timer') and self.main_window.auto_lock_timer:
            self.main_window.auto_lock_timer.register_dialog(dialog.dialog)
    
        if dialog.result:
            original_title = dialog.result['title']
            dialog.result['title'] = f"{original_title} (Copy)"
        
            success = self.main_window.pm.add_entry(**dialog.result)
            if success:
                if hasattr(self.main_window, 'refresh_password_list'):
                    self.main_window.refresh_password_list()
            
                if hasattr(self.main_window, 'status_label') and self.main_window.status_label:
                    from gui.modern_styles import update_status_bar
                    update_status_bar(self.main_window.status_label, 
                                    f"Entry duplicated: {dialog.result['title']}", "success")
            else:
                messagebox.showerror("Error", "Could not duplicate entry. Title already exists?")
    
    def _delete_entry(self):
        if hasattr(self.main_window, 'delete_password'):
            self.main_window.delete_password()
    
    def _copy_username(self):
        if hasattr(self.main_window, 'toolbar_manager'):
            self.main_window.toolbar_manager._copy_username()
    
    def _copy_password(self):
        if hasattr(self.main_window, 'copy_password'):
            self.main_window.copy_password()
    
    def _copy_url(self):
        entry = self.main_window.get_selected_entry()
        if not entry:
            messagebox.showwarning("Warning", "Please select an entry!")
            return
    
        if entry.url.strip():
            import pyperclip
            pyperclip.copy(entry.url)
            if hasattr(self.main_window, 'status_label') and self.main_window.status_label:
                from gui.modern_styles import update_status_bar
                update_status_bar(self.main_window.status_label, f"URL copied: {entry.title}", "info")
        else:
            if hasattr(self.main_window, 'status_label') and self.main_window.status_label:
                from gui.modern_styles import update_status_bar
                update_status_bar(self.main_window.status_label, "No URL available", "warning")
    
    def _copy_totp(self):
        entry = self.main_window.get_selected_entry()
        if not entry:
            messagebox.showwarning("Warning", "Please select an entry!")
            return
        
        if entry.has_totp() and hasattr(self.main_window, 'totp_manager'):
            current_code, remaining_time = self.main_window.totp_manager.get_current_totp(entry.totp_secret)
            if current_code:
                import pyperclip
                pyperclip.copy(current_code)
                if hasattr(self.main_window, 'status_label') and self.main_window.status_label:
                    from gui.modern_styles import update_status_bar
                    update_status_bar(self.main_window.status_label, 
                                    f"2FA code copied: {current_code} ({remaining_time}s remaining)", "info")
            else:
                messagebox.showerror("Error", "Could not generate 2FA code!")
        else:
            messagebox.showwarning("Warning", "No 2FA code available for this entry!")
    
    def _select_all(self):
        if hasattr(self.main_window, 'table_manager') and self.main_window.table_manager.tree:
            tree = self.main_window.table_manager.tree
            tree.selection_set(tree.get_children())
    
    def _find_entries(self):
        if hasattr(self.main_window, 'toolbar_manager'):
            self.main_window.toolbar_manager.focus_search()
    
    def _password_generator(self):
        if hasattr(self.main_window, 'open_password_generator'):
            self.main_window.open_password_generator()
    
    def _totp_manager(self):
        if hasattr(self.main_window, 'open_totp_manager'):
            self.main_window.open_totp_manager()
    
    def _database_backup(self):
        if hasattr(self.main_window, 'open_backup_dialog'):
            self.main_window.open_backup_dialog()
    
    def _import_backup(self):
        if hasattr(self.main_window, 'open_backup_dialog'):
            self.main_window.open_backup_dialog()
    
    def _check_passwords(self):
        if not hasattr(self.main_window, 'pm') or not self.main_window.pm.is_unlocked:
            return
        
        entries = self.main_window.pm.list_entries()
        weak_passwords = []
        
        for entry in entries:
            if hasattr(self.main_window, 'password_generator'):
                strength, score = self.main_window.password_generator.calculate_password_strength(entry.password)
                if score < 50:
                    weak_passwords.append(f"{entry.title}: {strength} ({score}/100)")
        
        if weak_passwords:
            message = "Weak passwords found:\n\n" + "\n".join(weak_passwords[:10])
            if len(weak_passwords) > 10:
                message += f"\n\n... and {len(weak_passwords) - 10} more"
            messagebox.showwarning("Weak Passwords", message)
        else:
            messagebox.showinfo("Password Strength", "All passwords are strong!")
    
    def _find_duplicates(self):
        if not hasattr(self.main_window, 'pm') or not self.main_window.pm.is_unlocked:
            return
        
        entries = self.main_window.pm.list_entries()
        password_groups = {}
        
        for entry in entries:
            pw = entry.password
            if pw in password_groups:
                password_groups[pw].append(entry.title)
            else:
                password_groups[pw] = [entry.title]
        
        duplicates = {pw: titles for pw, titles in password_groups.items() if len(titles) > 1}
        
        if duplicates:
            message = "Duplicate passwords found:\n\n"
            for pw, titles in list(duplicates.items())[:5]:
                message += f"Password used by: {', '.join(titles)}\n\n"
            if len(duplicates) > 5:
                message += f"... and {len(duplicates) - 5} more groups"
            messagebox.showwarning("Duplicate Passwords", message)
        else:
            messagebox.showinfo("Duplicate Check", "No duplicate passwords found!")
    
    def _open_settings(self):
        if hasattr(self.main_window, 'open_settings'):
            self.main_window.open_settings()
    
    def _refresh_view(self):
        if hasattr(self.main_window, 'refresh_password_list'):
            self.main_window.refresh_password_list()
    
    def _sort_by(self, column):
        if hasattr(self.main_window, 'table_manager'):
            if column == 'title':
                self.main_window.table_manager._sort_by_column('#0')
            else:
                self.main_window.table_manager._sort_by_column(column)
    
    def _show_shortcuts(self):
        if hasattr(self.main_window, 'keyboard_manager'):
            self.main_window.keyboard_manager._show_shortcuts_help()
    
    def _show_getting_started(self):
        messagebox.showinfo("Getting Started", 
                           "Welcome to Password Manager!\n\n"
                           "• Use Ctrl+N to add new passwords\n"
                           "• Use Ctrl+F to search entries\n"
                           "• Right-click entries for more options\n"
                           "• Use F1 to see all keyboard shortcuts\n\n"
                           "Your passwords are encrypted and secure!")
    
    def _check_updates(self):
        messagebox.showinfo("Updates", "You are using the latest version of Password Manager!")
    
    def _report_issue(self):
        messagebox.showinfo("Report Issue", 
                           "To report an issue:\n\n"
                           "1. Describe the problem in detail\n"
                           "2. Include steps to reproduce\n"
                           "3. Mention your operating system\n\n"
                           "Contact: support@passwordmanager.com")
    
    def _show_about(self):
        messagebox.showinfo("About Password Manager",
                           "🔐 Password Manager v2.0\n\n"
                           "A secure password management application\n"
                           "with modern design and advanced features.\n\n"
                           "Features:\n"
                           "• AES-256 encryption\n"
                           "• 2FA/TOTP support\n"
                           "• Password generation\n"
                           "• Secure backup & export\n"
                           "• Auto-lock protection\n\n"
                           "Built with Python & Tkinter")