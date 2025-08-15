import tkinter as tk
from tkinter import messagebox


class KeyboardShortcutManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.shortcuts = {}
        self._setup_shortcuts()
    
    def _setup_shortcuts(self):
        self.shortcuts = {
            '<F5>': {'action': self._refresh, 'description': 'Aktualisieren/Refresh'},
            '<Control-n>': {'action': self._new_password, 'description': 'Neues Passwort hinzufügen'},
            '<Control-o>': {'action': self._switch_database, 'description': 'Datenbank öffnen'},
            '<Control-e>': {'action': self._edit_password, 'description': 'Ausgewähltes Passwort bearbeiten'},
            '<Control-k>': {'action': self._duplicate_password, 'description': 'Ausgewähltes Passwort duplizieren'},
            '<Delete>': {'action': self._delete_password, 'description': 'Ausgewähltes Passwort löschen'},
            '<Control-c>': {'action': self._copy_password, 'description': 'Passwort kopieren'},
            '<Control-b>': {'action': self._copy_username, 'description': 'Benutzername kopieren'},
            '<Control-s>': {'action': self._create_backup, 'description': 'Backup erstellen'},
            '<Control-f>': {'action': self._focus_search, 'description': 'Fokus auf Suchfeld'},
            '<Escape>': {'action': self._clear_search, 'description': 'Suche löschen'},
            '<Control-a>': {'action': self._select_all, 'description': 'Alle Einträge auswählen'},
            '<Control-g>': {'action': self._open_generator, 'description': 'Passwort-Generator öffnen'},
            '<Control-l>': {'action': self._logout, 'description': 'Abmelden'},
            '<Control-d>': {'action': self._switch_database, 'description': 'Datenbank wechseln'},
            '<Control-comma>': {'action': self._open_settings, 'description': 'Einstellungen öffnen'},
            '<Control-q>': {'action': self._quit_application, 'description': 'Anwendung beenden'},
            '<F1>': {'action': self._show_help, 'description': 'Hilfe anzeigen'}
        }
    
    def bind_shortcuts(self, widget):
        for shortcut, config in self.shortcuts.items():
            try:
                widget.bind_all(shortcut, lambda event, action=config['action']: self._handle_shortcut(action))
            except Exception as e:
                print(f"Konnte Shortcut {shortcut} nicht binden: {e}")
    
    def _handle_shortcut(self, action):
        try:
            action_name = action.__name__
            
            global_shortcuts = ['_show_help', '_refresh']
            main_window_only = ['_new_password', '_edit_password', '_delete_password', '_duplicate_password',
                              '_copy_password', '_copy_username', '_open_generator', '_focus_search', 
                              '_select_all', '_logout', '_switch_database', '_quit_application']
            
            if action_name == '_clear_search':
                if self._has_open_dialog():
                    self._close_top_dialog()
                    return 'break'
                elif self._is_main_window_active():
                    action()
                    return 'break'
                return
            
            if action_name in global_shortcuts:
                action()
                return 'break'
            
            if action_name in main_window_only:
                if self._is_main_window_active():
                    action()
                    return 'break'
                else:
                    return
            
            if self._is_main_window_active():
                action()
                return 'break'
                
        except Exception as e:
            print(f"Fehler beim Ausführen des Shortcuts: {e}")
    
    def _is_main_window_active(self):
        try:
            return not self._has_open_dialog()
        except:
            return True
    
    def _has_open_dialog(self):
        try:
            toplevels = [child for child in self.main_window.root.winfo_children() 
                        if isinstance(child, tk.Toplevel)]
            return len(toplevels) > 0
        except:
            return False
    
    def _close_top_dialog(self):
        try:
            toplevels = [child for child in self.main_window.root.winfo_children() 
                        if isinstance(child, tk.Toplevel)]
            if toplevels:
                toplevels[-1].destroy()
        except Exception as e:
            print(f"Konnte Dialog nicht schließen: {e}")
    
    def _refresh(self):
        if hasattr(self.main_window, 'refresh_password_list'):
            self.main_window.refresh_password_list()
            if self.main_window.status_label:
                from gui.modern_styles import update_status_bar
                update_status_bar(self.main_window.status_label, "📄 Liste aktualisiert", "info")
    
    def _new_password(self):
        if hasattr(self.main_window, 'add_password'):
            self.main_window.add_password()
    
    def _edit_password(self):
        if hasattr(self.main_window, 'get_selected_entry'):
            if self.main_window.get_selected_entry():
                self.main_window.edit_password()
            else:
                if self.main_window.status_label:
                    from gui.modern_styles import update_status_bar
                    update_status_bar(self.main_window.status_label, "⚠️ Kein Eintrag ausgewählt", "warning")
    
    def _duplicate_password(self):
        if hasattr(self.main_window, 'get_selected_entry'):
            entry = self.main_window.get_selected_entry()
            if entry:
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
            else:
                if self.main_window.status_label:
                    from gui.modern_styles import update_status_bar
                    update_status_bar(self.main_window.status_label, "⚠️ Kein Eintrag ausgewählt", "warning")
    
    def _delete_password(self):
        if hasattr(self.main_window, 'get_selected_entry'):
            if self.main_window.get_selected_entry():
                self.main_window.delete_password()
            else:
                if self.main_window.status_label:
                    from gui.modern_styles import update_status_bar
                    update_status_bar(self.main_window.status_label, "⚠️ Kein Eintrag ausgewählt", "warning")
    
    def _copy_password(self):
        if hasattr(self.main_window, 'get_selected_entry'):
            if self.main_window.get_selected_entry():
                self.main_window.copy_password()
            else:
                if self.main_window.status_label:
                    from gui.modern_styles import update_status_bar
                    update_status_bar(self.main_window.status_label, "⚠️ Kein Eintrag ausgewählt", "warning")
    
    def _copy_username(self):
        if hasattr(self.main_window, 'toolbar_manager'):
            self.main_window.toolbar_manager._copy_username()
    
    def _select_all(self):
        if hasattr(self.main_window, 'table_manager') and self.main_window.table_manager.tree:
            tree = self.main_window.table_manager.tree
            tree.selection_set(tree.get_children())
            if self.main_window.status_label:
                from gui.modern_styles import update_status_bar
                update_status_bar(self.main_window.status_label, f"✅ Alle {len(tree.get_children())} Einträge ausgewählt", "info")
    
    def _open_generator(self):
        if hasattr(self.main_window, 'open_password_generator'):
            self.main_window.open_password_generator()
    
    def _create_backup(self):
        if hasattr(self.main_window, 'backup_manager'):
            success, message = self.main_window.backup_manager.create_encrypted_backup()
            if success:
                if self.main_window.status_label:
                    from gui.modern_styles import update_status_bar
                    update_status_bar(self.main_window.status_label, "💾 Backup erstellt", "success")
            else:
                messagebox.showerror("Backup-Fehler", message)
    
    def _focus_search(self):
        if (hasattr(self.main_window, 'toolbar_manager') and 
            self.main_window.toolbar_manager):
            self.main_window.toolbar_manager.focus_search()
            if self.main_window.status_label:
                from gui.modern_styles import update_status_bar
                update_status_bar(self.main_window.status_label, "🔍 Suchfeld aktiviert", "info")
    
    def _clear_search(self):
        if (hasattr(self.main_window, 'toolbar_manager') and 
            self.main_window.toolbar_manager):
            if hasattr(self.main_window.toolbar_manager, 'search_entry'):
                search_entry = self.main_window.toolbar_manager.search_entry
                if search_entry and search_entry.get().strip():
                    search_entry.delete(0, tk.END)
                    self.main_window.toolbar_manager._set_search_placeholder()
                    if hasattr(self.main_window, 'refresh_password_list'):
                        self.main_window.refresh_password_list()
                    if self.main_window.status_label:
                        from gui.modern_styles import update_status_bar
                        update_status_bar(self.main_window.status_label, "🧹 Suche gelöscht", "info")
    
    def _logout(self):
        if messagebox.askyesno("Abmelden", "Wirklich abmelden?"):
            self.main_window.logout()
    
    def _switch_database(self):
        if messagebox.askyesno("Datenbank wechseln", "Datenbank wechseln? Aktuelle Sitzung wird beendet."):
            self.main_window.switch_database()
    
    def _open_settings(self):
        if hasattr(self.main_window, 'open_settings'):
            self.main_window.open_settings()
    
    def _quit_application(self):
        if messagebox.askyesno("Beenden", "Anwendung wirklich beenden?"):
            self.main_window.on_closing()
    
    def _show_help(self):
        self._show_shortcuts_help()
    
    def _show_shortcuts_help(self):
        from gui.modern_styles import (WindowsClassicStyles, WindowsClassicColors, 
                                     create_classic_frame, create_classic_label_frame)
        
        WindowsClassicStyles.setup_windows_classic_theme()
        
        help_dialog = tk.Toplevel(self.main_window.root)
        help_dialog.title("Keyboard Shortcuts")
        help_dialog.geometry("550x650")
        help_dialog.configure(bg=WindowsClassicColors.WINDOW_BG)
        help_dialog.transient(self.main_window.root)
        help_dialog.grab_set()
        help_dialog.resizable(False, False)
        
        help_dialog.geometry("+%d+%d" % (
            self.main_window.root.winfo_rootx() + 125, 
            self.main_window.root.winfo_rooty() + 25
        ))
        
        help_dialog.focus_set()
        help_dialog.focus_force()
        
        main_frame = create_classic_frame(help_dialog, WindowsClassicColors.DIALOG_BG)
        main_frame.pack(expand=True, fill='both', padx=12, pady=12)
        
        title_frame = create_classic_frame(main_frame, WindowsClassicColors.DIALOG_BG)
        title_frame.pack(fill='x', pady=(0, 16))
        
        icon_label = tk.Label(title_frame, text="⌨️", 
                             bg=WindowsClassicColors.DIALOG_BG, 
                             fg=WindowsClassicColors.ACCENT,
                             font=('Segoe UI', 16, 'normal'))
        icon_label.pack(side='left', padx=(0, 8))
        
        title_label = tk.Label(title_frame, text="Keyboard Shortcuts", 
                              bg=WindowsClassicColors.DIALOG_BG, 
                              fg=WindowsClassicColors.TEXT_PRIMARY,
                              font=('Segoe UI', 14, 'bold'))
        title_label.pack(side='left')
        
        content_frame = create_classic_label_frame(main_frame, "Verfügbare Tastenkürzel")
        content_frame.pack(expand=True, fill='both', pady=(0, 16))
        
        scroll_container = create_classic_frame(content_frame, WindowsClassicColors.WINDOW_BG, relief='sunken')
        scroll_container.pack(expand=True, fill='both', padx=8, pady=8)
        
        canvas = tk.Canvas(scroll_container, 
                          bg=WindowsClassicColors.INPUT_BG, 
                          highlightthickness=0,
                          relief='flat', bd=0)
        scrollbar = tk.Scrollbar(scroll_container, orient='vertical', command=canvas.yview)
        scrollable_frame = create_classic_frame(canvas, WindowsClassicColors.INPUT_BG)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        groups = {
            "🔧 Hauptfunktionen": [
                ('F5', 'Aktualisieren/Refresh'),
                ('Ctrl+N', 'Neues Passwort hinzufügen'),
                ('Ctrl+O', 'Datenbank öffnen'),
                ('Ctrl+E', 'Ausgewähltes Passwort bearbeiten'),
                ('Ctrl+K', 'Ausgewähltes Passwort duplizieren'),
                ('Delete', 'Ausgewähltes Passwort löschen'),
                ('Ctrl+C', 'Passwort kopieren'),
                ('Ctrl+B', 'Benutzername kopieren'),
                ('Ctrl+S', 'Backup erstellen')
            ],
            "🔍 Suche & Navigation": [
                ('Ctrl+F', 'Fokus auf Suchfeld'),
                ('Escape', 'Suche löschen'),
                ('Ctrl+A', 'Alle Einträge auswählen')
            ],
            "🛠️ Tools": [
                ('Ctrl+G', 'Passwort-Generator öffnen')
            ],
            "⚙️ System": [
                ('Ctrl+L', 'Abmelden'),
                ('Ctrl+D', 'Datenbank wechseln'),
                ('Ctrl+,', 'Einstellungen öffnen'),
                ('Ctrl+Q', 'Anwendung beenden')
            ],
            "❓ Hilfe": [
                ('F1', 'Diese Hilfe anzeigen')
            ]
        }
        
        for group_name, shortcuts in groups.items():
            group_frame = create_classic_frame(scrollable_frame, WindowsClassicColors.INPUT_BG)
            group_frame.pack(fill='x', pady=(12, 4))
            
            group_label = tk.Label(group_frame, text=group_name,
                                  bg=WindowsClassicColors.INPUT_BG,
                                  fg=WindowsClassicColors.ACCENT,
                                  font=('Segoe UI', 10, 'bold'))
            group_label.pack(anchor='w', padx=8)
            
            separator = tk.Frame(group_frame, height=1, bg=WindowsClassicColors.BORDER)
            separator.pack(fill='x', padx=8, pady=(2, 0))
            
            for shortcut, description in shortcuts:
                shortcut_frame = create_classic_frame(scrollable_frame, WindowsClassicColors.INPUT_BG)
                shortcut_frame.pack(fill='x', pady=1)
                
                key_frame = create_classic_frame(shortcut_frame, WindowsClassicColors.BUTTON_BG, relief='raised')
                key_frame.pack(side='left', padx=(16, 12), pady=2)
                
                key_label = tk.Label(key_frame, text=shortcut,
                                    bg=WindowsClassicColors.BUTTON_BG,
                                    fg=WindowsClassicColors.TEXT_PRIMARY,
                                    font=('Consolas', 8, 'bold'),
                                    padx=8, pady=2)
                key_label.pack()
                
                desc_label = tk.Label(shortcut_frame, text=description,
                                     bg=WindowsClassicColors.INPUT_BG,
                                     fg=WindowsClassicColors.TEXT_PRIMARY,
                                     font=('Segoe UI', 9, 'normal'),
                                     anchor='w')
                desc_label.pack(side='left', fill='x', expand=True, padx=(0, 16))
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        button_frame = create_classic_frame(main_frame, WindowsClassicColors.DIALOG_BG)
        button_frame.pack(fill='x', pady=(0, 4))
        
        button_container = create_classic_frame(button_frame, WindowsClassicColors.DIALOG_BG)
        button_container.pack(side='right')
        
        close_btn = tk.Button(button_container, text="Schließen", 
                             command=help_dialog.destroy,
                             bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                             relief='raised', bd=1, padx=20, pady=6,
                             width=10)
        close_btn.pack()
        
        def on_enter(event):
            close_btn.config(bg='#d5d5d5')
        def on_leave(event):
            close_btn.config(bg='#e1e1e1')
        close_btn.bind('<Enter>', on_enter)
        close_btn.bind('<Leave>', on_leave)
        
        info_label = tk.Label(button_frame, 
                             text="Tipp: F1/F5 funktionieren überall, andere nur im Hauptfenster",
                             bg=WindowsClassicColors.DIALOG_BG,
                             fg=WindowsClassicColors.TEXT_SECONDARY,
                             font=('Segoe UI', 8, 'italic'))
        info_label.pack(side='left', anchor='w')
        
        help_dialog.bind('<Return>', lambda e: help_dialog.destroy())
        help_dialog.bind('<Escape>', lambda e: help_dialog.destroy())
        
        def _on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass
        
        def bind_mousewheel():
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def unbind_mousewheel():
            canvas.unbind_all("<MouseWheel>")
        
        bind_mousewheel()
        
        def on_dialog_close():
            unbind_mousewheel()
            help_dialog.destroy()
        
        help_dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
    
    def get_shortcuts_list(self):
        shortcuts_list = []
        for shortcut, config in self.shortcuts.items():
            shortcuts_list.append({
                'shortcut': shortcut,
                'description': config['description']
            })
        return shortcuts_list