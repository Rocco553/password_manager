import tkinter as tk
from tkinter import messagebox
import webbrowser
import pyperclip
from gui.modern_styles import ModernColors
from gui.localization import _


class EnhancedContextMenu:
    def __init__(self, main_window):
        self.main_window = main_window
        self.context_menu = None
        self.selected_entry = None
        
    def setup_context_menu(self, widget):
        widget.bind('<Button-3>', self._on_right_click)
        widget.bind('<Control-Button-1>', self._on_right_click)
    
    def setup_treeview_context_menu(self, widget):
        self.setup_context_menu(widget)
    
    def _on_right_click(self, event):
        if hasattr(self.main_window, 'table_manager') and self.main_window.table_manager.tree:
            item = self.main_window.table_manager.tree.identify_row(event.y)
            
            if item:
                self.main_window.table_manager.tree.selection_set(item)
                self.main_window.table_manager.tree.focus(item)
                
                self.selected_entry = self.main_window.get_selected_entry()
                
                if self.selected_entry:
                    self._create_context_menu()
                    
                    try:
                        self.context_menu.tk_popup(event.x_root, event.y_root)
                    finally:
                        self.context_menu.grab_release()
    
    def _create_context_menu(self):
        if self.context_menu:
            self.context_menu.destroy()
        
        self.context_menu = tk.Menu(self.main_window.root, tearoff=0)
        
        self.context_menu.configure(
            bg=ModernColors.PANEL_BG,
            fg=ModernColors.TEXT_PRIMARY,
            activebackground=ModernColors.ACCENT_BLUE,
            activeforeground='#ffffff',
            font=('Segoe UI', 9, 'normal'),
            relief='flat',
            bd=1,
            borderwidth=1
        )
        
        self._add_primary_actions()
        self.context_menu.add_separator()
        self._add_copy_actions()
        self.context_menu.add_separator()
        self._add_navigation_actions()
        self.context_menu.add_separator()
        self._add_management_actions()
        self.context_menu.add_separator()
        self._add_info_actions()
    
    def _add_primary_actions(self):
        self.context_menu.add_command(
            label=_("context_edit_entry"),
            command=self._edit_entry,
            accelerator="Ctrl+E"
        )
        
        self.context_menu.add_command(
            label=_("context_copy_password"),
            command=self._copy_password,
            accelerator="Ctrl+C"
        )
    
    def _add_copy_actions(self):
        self.context_menu.add_command(
            label=_("context_copy_username"),
            command=self._copy_username
        )
        
        if self.selected_entry.has_totp():
            self.context_menu.add_command(
                label=_("context_copy_2fa"),
                command=self._copy_totp_code
            )
        
        if self.selected_entry.url.strip():
            self.context_menu.add_command(
                label=_("context_copy_url"),
                command=self._copy_url
            )
    
    def _add_navigation_actions(self):
        if self.selected_entry.url.strip():
            domain = self._get_domain_from_url(self.selected_entry.url)
            self.context_menu.add_command(
                label=f"{_('context_open_website')} {domain}",
                command=self._open_website
            )
        
        self.context_menu.add_command(
            label=_("context_search_similar"),
            command=self._search_similar
        )
    
    def _add_management_actions(self):
        self.context_menu.add_command(
            label=_("context_duplicate_entry"),
            command=self._duplicate_entry
        )
        
        if hasattr(self.main_window, 'category_manager'):
            category_menu = tk.Menu(self.context_menu, tearoff=0)
            category_menu.configure(
                bg=ModernColors.PANEL_BG,
                fg=ModernColors.TEXT_PRIMARY,
                activebackground=ModernColors.ACCENT_BLUE,
                activeforeground='#ffffff',
                font=('Segoe UI', 8, 'normal')
            )
            
            categories = self.main_window.category_manager.get_categories_list()
            current_category = self.selected_entry.category if self.selected_entry else "Other"
            
            for category in categories:
                if category != current_category:
                    category_menu.add_command(
                        label=f"Move to {category}",
                        command=lambda cat=category: self._change_category(cat)
                    )
            
            self.context_menu.add_cascade(label="📂 Change Category", menu=category_menu)
        
        self.context_menu.add_command(
            label=_("context_delete_entry"),
            command=self._delete_entry,
            accelerator="Delete"
        )
    
    def _add_info_actions(self):
        self.context_menu.add_command(
            label=_("context_entry_details"),
            command=self._show_entry_details
        )
        
        self.context_menu.add_command(
            label=_("context_password_strength"),
            command=self._show_password_strength
        )
    
    def _edit_entry(self):
        if hasattr(self.main_window, 'edit_password'):
            self.main_window.edit_password()
    
    def _copy_password(self):
        if self.selected_entry:
            pyperclip.copy(self.selected_entry.password)
            self._update_status(f"{_('status_password_copied')}: {self.selected_entry.title}", "info")
            self._start_clipboard_timer()
    
    def _copy_username(self):
        if self.selected_entry and self.selected_entry.username.strip():
            pyperclip.copy(self.selected_entry.username)
            self._update_status(f"{_('status_username_copied')}: {self.selected_entry.title}", "info")
        else:
            self._update_status(_("error_no_username_available"), "warning")
    
    def _copy_totp_code(self):
        if self.selected_entry and self.selected_entry.has_totp():
            if hasattr(self.main_window, 'totp_manager'):
                current_code, remaining_time = self.main_window.totp_manager.get_current_totp(
                    self.selected_entry.totp_secret)
                if current_code:
                    pyperclip.copy(current_code)
                    self._update_status(f"2FA code copied ({remaining_time}s remaining)", "info")
                else:
                    self._update_status("Could not generate 2FA code", "error")
    
    def _copy_url(self):
        if self.selected_entry and self.selected_entry.url.strip():
            pyperclip.copy(self.selected_entry.url)
            self._update_status(f"URL copied: {self.selected_entry.title}", "info")
    
    def _open_website(self):
        if self.selected_entry and self.selected_entry.url.strip():
            url = self.selected_entry.url.strip()
            
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            try:
                webbrowser.open(url)
                self._update_status(f"Website opened: {self.selected_entry.title}", "info")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open website:\n{str(e)}")
    
    def _search_similar(self):
        if self.selected_entry and hasattr(self.main_window, 'toolbar_manager'):
            search_term = self.selected_entry.title.split()[0]
            
            if hasattr(self.main_window.toolbar_manager, 'search_entry'):
                self.main_window.toolbar_manager.search_entry.delete(0, tk.END)
                self.main_window.toolbar_manager.search_entry.insert(0, search_term)
                self.main_window.toolbar_manager._clear_search_placeholder()
                
                if hasattr(self.main_window, 'perform_search'):
                    self.main_window.perform_search(search_term)
    
    def _duplicate_entry(self):
        if self.selected_entry:
            from gui.password_dialog import PasswordDialog
            
            dialog = PasswordDialog(
                self.main_window.root, 
                "Duplicate Entry",
                self.selected_entry,
                self.main_window.password_generator,
                self.main_window.category_manager
            )
            
            if dialog.result:
                original_title = dialog.result['title']
                dialog.result['title'] = f"{original_title} (Copy)"
                
                success = self.main_window.pm.add_entry(**dialog.result)
                if success:
                    if hasattr(self.main_window, 'refresh_password_list'):
                        self.main_window.refresh_password_list()
                    self._update_status(f"Entry duplicated: {dialog.result['title']}", "success")
                else:
                    messagebox.showerror("Error", "Could not duplicate entry. Title already exists?")
    
    def _delete_entry(self):
        if hasattr(self.main_window, 'delete_password'):
            self.main_window.delete_password()
    
    def _show_entry_details(self):
        if not self.selected_entry:
            return
        
        self._create_details_dialog()
    
    def _show_password_strength(self):
        if self.selected_entry and hasattr(self.main_window, 'password_generator'):
            strength, score = self.main_window.password_generator.calculate_password_strength(
                self.selected_entry.password)
            
            messagebox.showinfo(
                "Password Strength",
                f"Password strength for '{self.selected_entry.title}':\n\n"
                f"Strength: {strength}\n"
                f"Score: {score}/100\n\n"
                f"Length: {len(self.selected_entry.password)} characters"
            )
    
    def _create_details_dialog(self):
        from gui.modern_styles import ModernStyles, create_modern_frame, ModernSpacing
        
        ModernStyles.setup_modern_theme()
        
        details_dialog = tk.Toplevel(self.main_window.root)
        details_dialog.title(f"Entry Details - {self.selected_entry.title}")
        details_dialog.geometry("500x450")
        details_dialog.configure(bg=ModernColors.WINDOW_BG)
        details_dialog.transient(self.main_window.root)
        details_dialog.grab_set()
        details_dialog.resizable(False, False)
        
        details_dialog.geometry("+%d+%d" % (
            self.main_window.root.winfo_rootx() + 150, 
            self.main_window.root.winfo_rooty() + 100
        ))
        
        main_frame = create_modern_frame(details_dialog)
        main_frame.pack(expand=True, fill='both', padx=ModernSpacing.DIALOG_PADDING, 
                       pady=ModernSpacing.DIALOG_PADDING)
        
        title_label = tk.Label(main_frame, text=f"ℹ️ {self.selected_entry.title}",
                              bg=ModernColors.WINDOW_BG, fg=ModernColors.TEXT_PRIMARY,
                              font=('Segoe UI', 12, 'bold'))
        title_label.pack(pady=(0, ModernSpacing.GROUP_SPACING))
        
        details_frame = create_modern_frame(main_frame, ModernColors.PANEL_BG, relief='solid')
        details_frame.pack(fill='both', expand=True, pady=(0, ModernSpacing.GROUP_SPACING))
        
        self._add_detail_row(details_frame, "Title:", self.selected_entry.title)
        self._add_detail_row(details_frame, "Username:", self.selected_entry.username or "(none)")
        self._add_detail_row(details_frame, "Password:", "•" * len(self.selected_entry.password))
        self._add_detail_row(details_frame, "URL:", self.selected_entry.url or "(none)")
        self._add_detail_row(details_frame, "Category:", self.selected_entry.category or "Other")
        self._add_detail_row(details_frame, "2FA:", "Enabled" if self.selected_entry.has_totp() else "Disabled")
        self._add_detail_row(details_frame, "Created:", self._format_date(self.selected_entry.created))
        self._add_detail_row(details_frame, "Modified:", self._format_date(self.selected_entry.modified))
        
        if self.selected_entry.notes.strip():
            notes_label = tk.Label(details_frame, text="Notes:",
                                  bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_PRIMARY,
                                  font=('Segoe UI', 9, 'bold'), anchor='nw')
            notes_label.pack(anchor='w', padx=8, pady=(8, 2))
            
            from gui.modern_styles import create_modern_text
            notes_text = create_modern_text(details_frame, height=4)
            notes_text.pack(fill='x', padx=8, pady=(0, 8))
            notes_text.insert('1.0', self.selected_entry.notes)
            notes_text.config(state='disabled')
        
        button_frame = create_modern_frame(main_frame)
        button_frame.pack(fill='x')
        
        close_btn = tk.Button(button_frame, text="Close",
                             command=details_dialog.destroy,
                             bg=ModernColors.BUTTON_BG, fg=ModernColors.TEXT_PRIMARY,
                             font=('Segoe UI', 9, 'normal'),
                             relief='raised', bd=1, padx=20, pady=6)
        close_btn.pack(side='right')
        
        details_dialog.bind('<Escape>', lambda e: details_dialog.destroy())

        details_dialog.focus_set()
        details_dialog.focus_force()
    
    def _add_detail_row(self, parent, label_text, value):
        row_frame = tk.Frame(parent, bg=ModernColors.PANEL_BG)
        row_frame.pack(fill='x', padx=8, pady=2)
        
        label = tk.Label(row_frame, text=label_text,
                        bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_PRIMARY,
                        font=('Segoe UI', 9, 'bold'), width=12, anchor='w')
        label.pack(side='left')
        
        value_label = tk.Label(row_frame, text=value,
                              bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_SECONDARY,
                              font=('Segoe UI', 9, 'normal'), anchor='w')
        value_label.pack(side='left', fill='x', expand=True)
    
    def _get_domain_from_url(self, url):
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            if domain.startswith('www.'):
                domain = domain[4:]
            
            if len(domain) > 20:
                domain = domain[:17] + "..."
            
            return domain
        except:
            return "Website"
    
    def _format_date(self, date_str):
        if not date_str:
            return "Unknown"
        
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%d.%m.%Y %H:%M")
        except:
            return date_str[:19].replace('T', ' ') if len(date_str) >= 19 else date_str
    
    def _update_status(self, message, status_type):
        if hasattr(self.main_window, 'status_label') and self.main_window.status_label:
            from gui.modern_styles import update_status_bar
            update_status_bar(self.main_window.status_label, message, status_type)
    
    def _start_clipboard_timer(self):
        if hasattr(self.main_window, 'settings_manager'):
            clear_seconds = self.main_window.settings_manager.get("clipboard_clear_seconds", 10)
            clipboard_enabled = self.main_window.settings_manager.get("clipboard_clear_enabled", True)
            
            if clipboard_enabled and hasattr(self.main_window, 'clipboard_timer'):
                if self.main_window.clipboard_timer:
                    self.main_window.clipboard_timer.cancel()
                
                import threading
                self.main_window.clipboard_timer = threading.Timer(clear_seconds, self._clear_clipboard)
                self.main_window.clipboard_timer.start()
    
    def _clear_clipboard(self):
        pyperclip.copy("")
        self._update_status("Clipboard cleared", "normal")
    
    def _change_category(self, new_category):
        if self.selected_entry and self.selected_entry.category != new_category:
            self.selected_entry.category = new_category
            self.main_window.pm.save_database()
            
            if hasattr(self.main_window, 'refresh_password_list'):
                self.main_window.refresh_password_list()
            
            self._update_status(f"Entry moved to {new_category}", "success")