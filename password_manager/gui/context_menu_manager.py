"""
Context-Menü Manager für den Passwort-Manager
Rechtsklick-Menüs für bessere Benutzerfreundlichkeit - KOMPLETT NEU
"""

import tkinter as tk
from tkinter import messagebox
import webbrowser
import pyperclip
from gui.modern_styles import WindowsClassicColors


class ContextMenuManager:
    """Manager für Context-Menüs (Rechtsklick)"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.context_menu = None
        self.selected_entry = None
        
    def setup_treeview_context_menu(self, treeview):
        """Richtet Context-Menü für die TreeView ein"""
        # Rechtsklick-Event binden
        treeview.bind('<Button-3>', self._on_right_click)  # Windows: Button-3
        treeview.bind('<Control-Button-1>', self._on_right_click)  # Mac: Ctrl+Click
    
    def _on_right_click(self, event):
        """Behandelt Rechtsklick auf TreeView"""
        # Finde das angeklickte Element
        item = self.main_window.tree.identify_row(event.y)
        
        if item:
            # Wähle das Element aus
            self.main_window.tree.selection_set(item)
            self.main_window.tree.focus(item)
            
            # Hole den Eintrag
            self.selected_entry = self.main_window.get_selected_entry()
            
            if self.selected_entry:
                # Erstelle Menü dynamisch
                self._create_dynamic_menu()
                
                # Zeige Context-Menü
                try:
                    self.context_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    self.context_menu.grab_release()
    
    def _create_dynamic_menu(self):
        """Erstellt das Context-Menü dynamisch basierend auf dem Eintrag"""
        # Zerstöre altes Menü falls vorhanden
        if self.context_menu:
            self.context_menu.destroy()
        
        # Erstelle neues Menü
        self.context_menu = tk.Menu(self.main_window.root, tearoff=0)
        
        # Windows-klassisches Design
        self.context_menu.configure(
            bg=WindowsClassicColors.WINDOW_BG,
            fg=WindowsClassicColors.TEXT_PRIMARY,
            activebackground=WindowsClassicColors.ACCENT,
            activeforeground='#ffffff',
            font=('Segoe UI', 9, 'normal'),
            relief='raised',
            bd=1
        )
        
        # Menüeinträge hinzufügen
        self.context_menu.add_command(
            label="📋 Passwort kopieren",
            command=self._copy_password,
            accelerator="Ctrl+C"
        )
        
        self.context_menu.add_command(
            label="👤 Benutzername kopieren", 
            command=self._copy_username
        )
        
        self.context_menu.add_separator()
        
        # Website-Eintrag: Dynamisch je nach URL
        has_url = bool(self.selected_entry.url.strip())
        if has_url:
            domain = self._get_domain_from_url(self.selected_entry.url)
            self.context_menu.add_command(
                label=f"🌐 {domain} öffnen",
                command=self._open_website
            )
        else:
            # Deaktivierte Version mit grauem Text
            self.context_menu.add_command(
                label="🌐 Website öffnen (keine URL)",
                command=lambda: None,
                foreground='#808080'
            )
        
        self.context_menu.add_separator()
        
        self.context_menu.add_command(
            label="✏️ Bearbeiten",
            command=self._edit_entry,
            accelerator="Ctrl+E"
        )
        
        self.context_menu.add_command(
            label="🗑️ Löschen",
            command=self._delete_entry,
            accelerator="Delete"
        )
        
        self.context_menu.add_separator()
        
        self.context_menu.add_command(
            label="ℹ️ Details anzeigen",
            command=self._show_details
        )
    
    def _get_domain_from_url(self, url):
        """Extrahiert Domain aus URL für bessere Anzeige"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Entferne www. für saubere Anzeige
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Kürze sehr lange Domains
            if len(domain) > 20:
                domain = domain[:17] + "..."
            
            return domain
        except:
            return "Website"
    
    # CONTEXT-MENÜ AKTIONEN
    
    def _copy_password(self):
        """Kopiert das Passwort des ausgewählten Eintrags"""
        if self.selected_entry:
            pyperclip.copy(self.selected_entry.password)
            
            # Status-Update
            if self.main_window.status_label:
                from gui.modern_styles import update_status_bar
                update_status_bar(self.main_window.status_label, 
                                f"📋 Passwort von '{self.selected_entry.title}' kopiert", "info")
            
            # Auto-Clear Timer starten
            if self.main_window.clipboard_timer:
                self.main_window.clipboard_timer.cancel()
            
            import threading
            self.main_window.clipboard_timer = threading.Timer(10.0, self.main_window.clear_clipboard)
            self.main_window.clipboard_timer.start()
    
    def _copy_username(self):
        """Kopiert den Benutzernamen des ausgewählten Eintrags"""
        if self.selected_entry:
            if self.selected_entry.username.strip():
                pyperclip.copy(self.selected_entry.username)
                
                # Status-Update
                if self.main_window.status_label:
                    from gui.modern_styles import update_status_bar
                    update_status_bar(self.main_window.status_label, 
                                    f"👤 Benutzername von '{self.selected_entry.title}' kopiert", "info")
            else:
                messagebox.showinfo("Info", f"Kein Benutzername für '{self.selected_entry.title}' vorhanden.")
    
    def _open_website(self):
        """Öffnet die Website des ausgewählten Eintrags"""
        if self.selected_entry and self.selected_entry.url.strip():
            url = self.selected_entry.url.strip()
            
            # Stelle sicher, dass URL ein Protokoll hat
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            try:
                webbrowser.open(url)
                
                # Status-Update
                if self.main_window.status_label:
                    from gui.modern_styles import update_status_bar
                    update_status_bar(self.main_window.status_label, 
                                    f"🌐 Website für '{self.selected_entry.title}' geöffnet", "info")
            except Exception as e:
                messagebox.showerror("Fehler", f"Website konnte nicht geöffnet werden:\n{str(e)}")
    
    def _edit_entry(self):
        """Bearbeitet den ausgewählten Eintrag"""
        if self.selected_entry:
            self.main_window.edit_password()
    
    def _delete_entry(self):
        """Löscht den ausgewählten Eintrag"""
        if self.selected_entry:
            self.main_window.delete_password()
    
    def _show_details(self):
        """Zeigt Details des ausgewählten Eintrags in einem schönen Dialog"""
        if not self.selected_entry:
            return
        
        # Erstelle Details-Dialog im Windows-klassischen Stil
        from gui.modern_styles import (WindowsClassicStyles, create_classic_frame, 
                                     create_classic_label_frame, ClassicSpacing)
        
        WindowsClassicStyles.setup_windows_classic_theme()
        
        details_dialog = tk.Toplevel(self.main_window.root)
        details_dialog.title(f"Details - {self.selected_entry.title}")
        details_dialog.geometry("450x400")
        details_dialog.configure(bg=WindowsClassicColors.WINDOW_BG)
        details_dialog.transient(self.main_window.root)
        details_dialog.grab_set()
        details_dialog.resizable(False, False)
        
        # Zentrieren
        details_dialog.geometry("+%d+%d" % (
            self.main_window.root.winfo_rootx() + 175, 
            self.main_window.root.winfo_rooty() + 100
        ))
        
        # Hauptframe
        main_frame = create_classic_frame(details_dialog, WindowsClassicColors.DIALOG_BG)
        main_frame.pack(expand=True, fill='both', padx=12, pady=12)
        
        # Titel
        title_frame = create_classic_frame(main_frame, WindowsClassicColors.DIALOG_BG)
        title_frame.pack(fill='x', pady=(0, 16))
        
        icon_label = tk.Label(title_frame, text="ℹ️", 
                             bg=WindowsClassicColors.DIALOG_BG, 
                             fg=WindowsClassicColors.ACCENT,
                             font=('Segoe UI', 16, 'normal'))
        icon_label.pack(side='left', padx=(0, 8))
        
        title_label = tk.Label(title_frame, text=f"Details für '{self.selected_entry.title}'", 
                              bg=WindowsClassicColors.DIALOG_BG, 
                              fg=WindowsClassicColors.TEXT_PRIMARY,
                              font=('Segoe UI', 12, 'bold'))
        title_label.pack(side='left')
        
        # Details-Container
        details_frame = create_classic_label_frame(main_frame, "Eintrag-Informationen")
        details_frame.pack(expand=True, fill='both', pady=(0, 16))
        
        details_container = create_classic_frame(details_frame, WindowsClassicColors.WINDOW_BG)
        details_container.pack(expand=True, fill='both', padx=8, pady=8)
        
        # Details-Felder
        details = [
            ("📝 Titel:", self.selected_entry.title),
            ("👤 Benutzername:", self.selected_entry.username or "(nicht angegeben)"),
            ("🔑 Passwort:", "•" * len(self.selected_entry.password) if self.selected_entry.password else "(leer)"),
            ("🌐 URL:", self.selected_entry.url or "(nicht angegeben)"),
            ("📅 Erstellt:", self.selected_entry.created[:19].replace('T', ' ') if self.selected_entry.created else "Unbekannt"),
            ("✏️ Geändert:", self.selected_entry.modified[:19].replace('T', ' ') if self.selected_entry.modified else "Unbekannt"),
        ]
        
        for label_text, value in details:
            detail_frame = create_classic_frame(details_container, WindowsClassicColors.WINDOW_BG)
            detail_frame.pack(fill='x', pady=2)
            
            # Label (links, fett)
            label = tk.Label(detail_frame, text=label_text,
                           bg=WindowsClassicColors.WINDOW_BG,
                           fg=WindowsClassicColors.TEXT_PRIMARY,
                           font=('Segoe UI', 9, 'bold'),
                           width=15, anchor='w')
            label.pack(side='left', padx=(4, 8))
            
            # Wert (rechts)
            value_label = tk.Label(detail_frame, text=value,
                                 bg=WindowsClassicColors.WINDOW_BG,
                                 fg=WindowsClassicColors.TEXT_SECONDARY,
                                 font=('Segoe UI', 9, 'normal'),
                                 anchor='w', wraplength=300)
            value_label.pack(side='left', fill='x', expand=True)
        
        # Notizen separat (falls vorhanden)
        if self.selected_entry.notes.strip():
            notes_frame = create_classic_label_frame(main_frame, "📋 Notizen")
            notes_frame.pack(fill='x', pady=(0, 16))
            
            notes_container = create_classic_frame(notes_frame, WindowsClassicColors.INPUT_BG, relief='sunken')
            notes_container.pack(fill='x', padx=8, pady=8)
            
            notes_text = tk.Text(notes_container, 
                                bg=WindowsClassicColors.INPUT_BG,
                                fg=WindowsClassicColors.TEXT_PRIMARY,
                                font=('Segoe UI', 9, 'normal'),
                                height=4, wrap='word',
                                relief='flat', bd=0,
                                state='normal')
            notes_text.pack(fill='x', padx=4, pady=4)
            
            notes_text.insert('1.0', self.selected_entry.notes)
            notes_text.config(state='disabled')  # Read-only
        
        # Button-Bereich
        button_frame = create_classic_frame(main_frame, WindowsClassicColors.DIALOG_BG)
        button_frame.pack(fill='x')
        
        # Schließen-Button (rechts)
        close_btn = tk.Button(button_frame, text="Schließen", 
                             command=details_dialog.destroy,
                             bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                             relief='raised', bd=1, padx=20, pady=6,
                             width=10)
        close_btn.pack(side='right')
        
        # Schnell-Aktionen (links)
        quick_actions = create_classic_frame(button_frame, WindowsClassicColors.DIALOG_BG)
        quick_actions.pack(side='left')
        
        copy_pw_btn = tk.Button(quick_actions, text="📋 Passwort", 
                               command=lambda: [self._copy_password(), details_dialog.destroy()],
                               bg='#e1e1e1', fg='#000000', font=('Segoe UI', 8, 'normal'),
                               relief='raised', bd=1, padx=8, pady=4)
        copy_pw_btn.pack(side='left', padx=(0, 4))
        
        if self.selected_entry.username.strip():
            copy_user_btn = tk.Button(quick_actions, text="👤 Benutzer", 
                                     command=lambda: [self._copy_username(), details_dialog.destroy()],
                                     bg='#e1e1e1', fg='#000000', font=('Segoe UI', 8, 'normal'),
                                     relief='raised', bd=1, padx=8, pady=4)
            copy_user_btn.pack(side='left', padx=4)
        
        if self.selected_entry.url.strip():
            open_url_btn = tk.Button(quick_actions, text="🌐 Öffnen", 
                                   command=lambda: [self._open_website(), details_dialog.destroy()],
                                   bg='#e1e1e1', fg='#000000', font=('Segoe UI', 8, 'normal'),
                                   relief='raised', bd=1, padx=8, pady=4)
            open_url_btn.pack(side='left', padx=4)
        
        # Hover-Effekte
        def create_hover_effect(button):
            def on_enter(event):
                button.config(bg='#d5d5d5')
            def on_leave(event):
                button.config(bg='#e1e1e1')
            button.bind('<Enter>', on_enter)
            button.bind('<Leave>', on_leave)
        
        # Hover-Effekte anwenden
        buttons = [close_btn, copy_pw_btn]
        if self.selected_entry.username.strip():
            buttons.append(copy_user_btn)
        if self.selected_entry.url.strip():
            buttons.append(open_url_btn)
        
        for btn in buttons:
            create_hover_effect(btn)
        
        # Keyboard-Navigation
        details_dialog.bind('<Return>', lambda e: details_dialog.destroy())
        details_dialog.bind('<Escape>', lambda e: details_dialog.destroy())
        
        # Fokus auf Dialog
        details_dialog.focus_set()