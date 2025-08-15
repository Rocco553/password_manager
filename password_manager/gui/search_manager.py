import tkinter as tk
from gui.modern_styles import (
    WindowsClassicColors, create_classic_frame, create_classic_entry,
    update_status_bar, ClassicSpacing
)


class SearchManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.search_entry = None
        self.search_placeholder = "Titel, Benutzername oder URL..."
        self.all_entries = []
        self.is_placeholder_active = True
        
    def create_search_ui(self, parent_frame):
        from gui.modern_styles import create_classic_label_frame
        
        search_frame = create_classic_label_frame(parent_frame, "🔍 Suche & Filter")
        search_frame.pack(fill='x', pady=(0, ClassicSpacing.GROUP_SPACING))

        search_container = create_classic_frame(search_frame)
        search_container.pack(fill='x', padx=ClassicSpacing.DIALOG_PADDING, pady=ClassicSpacing.SM)

        search_input_frame = create_classic_frame(search_container)
        search_input_frame.pack(side='left', fill='x', expand=True)

        search_label = tk.Label(search_input_frame, text="Suchen in:",
                               bg=WindowsClassicColors.WINDOW_BG,
                               fg=WindowsClassicColors.TEXT_PRIMARY,
                               font=('Segoe UI', 9, 'normal'))
        search_label.pack(side='left', padx=(0, ClassicSpacing.SM))

        self.search_entry = create_classic_entry(search_input_frame)
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(0, ClassicSpacing.SM))
        
        self._set_placeholder()
        
        self.search_entry.bind('<FocusIn>', self._on_search_focus_in)
        self.search_entry.bind('<FocusOut>', self._on_search_focus_out)
        self.search_entry.bind('<KeyRelease>', self._on_search_change)

        clear_btn = tk.Button(search_input_frame, text="✖", width=3,
                             command=self.clear_search,
                             bg='#e1e1e1', fg='#000000', font=('Segoe UI', 8, 'normal'),
                             relief='raised', bd=1, padx=4, pady=2)
        clear_btn.pack(side='left')

        filter_buttons = create_classic_frame(search_container)
        filter_buttons.pack(side='right')

        show_all_btn = tk.Button(filter_buttons, text="📋 Alle anzeigen", 
                                command=self.show_all_entries,
                                bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                                relief='raised', bd=1, padx=10, pady=3)
        show_all_btn.pack(side='right', padx=(ClassicSpacing.BUTTON_SPACING, 0))

        def create_hover_effect(button):
            def on_enter(event):
                button.config(bg='#d5d5d5')
            def on_leave(event):
                button.config(bg='#e1e1e1')
            button.bind('<Enter>', on_enter)
            button.bind('<Leave>', on_leave)

        create_hover_effect(clear_btn)
        create_hover_effect(show_all_btn)
        
        return search_frame

    def _set_placeholder(self):
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, self.search_placeholder)
        self.search_entry.configure(fg=WindowsClassicColors.TEXT_DISABLED)
        self.is_placeholder_active = True

    def _clear_placeholder(self):
        if self.is_placeholder_active:
            self.search_entry.delete(0, tk.END)
            self.search_entry.configure(fg=WindowsClassicColors.TEXT_PRIMARY)
            self.is_placeholder_active = False
    
    def focus_search_field(self):
        if self.search_entry:
            self.search_entry.focus_set()
            self._clear_placeholder()
    
    def _on_search_focus_in(self, event):
        self._clear_placeholder()

    def _on_search_focus_out(self, event):
        current_text = self.search_entry.get().strip()
        if not current_text:
            self._set_placeholder()
            self.show_all_entries()

    def _on_search_change(self, event):
        if self.is_placeholder_active:
            return
        
        search_term = self.search_entry.get().strip()
        self._perform_search(search_term)

    def _perform_search(self, search_term):
        if not search_term:
            self.show_all_entries()
            return
        
        search_term_lower = search_term.lower()
        filtered_entries = []
        
        for entry in self.all_entries:
            if (search_term_lower in entry.title.lower() or 
                search_term_lower in entry.username.lower() or 
                search_term_lower in entry.url.lower() or
                search_term_lower in entry.notes.lower()):
                filtered_entries.append(entry)
        
        self.main_window._update_tree_view(filtered_entries)
        
        if filtered_entries:
            if self.main_window.status_label:
                update_status_bar(self.main_window.status_label, 
                                "🔍 " + str(len(filtered_entries)) + " von " + str(len(self.all_entries)) + " Einträgen gefunden", 
                                "info")
        else:
            if self.main_window.status_label:
                update_status_bar(self.main_window.status_label, 
                                "🔍 Keine Ergebnisse für '" + search_term + "'", 
                                "warning")

    def clear_search(self):
        if self.search_entry:
            self._set_placeholder()
        
        self.show_all_entries()

    def show_all_entries(self):
        self.main_window._update_tree_view(self.all_entries)
        
        if self.main_window.status_label:
            timeout_min = self.main_window.settings_manager.get("auto_lock_timeout_minutes", 0.75)
            timeout_text = self.main_window._format_timeout_display(timeout_min)
            update_status_bar(self.main_window.status_label, 
                            "📋 Alle " + str(len(self.all_entries)) + " Einträge angezeigt – Auto-Lock aktiv (" + timeout_text + ")", 
                            "normal")
    
    def refresh_entries_cache(self, entries):
        self.all_entries = entries.copy()

    def has_active_search(self):
        if not self.search_entry or self.is_placeholder_active:
            return False
        
        search_term = self.search_entry.get().strip()
        return bool(search_term)

    def get_current_search_term(self):
        if not self.search_entry or self.is_placeholder_active:
            return ""
        
        return self.search_entry.get().strip()