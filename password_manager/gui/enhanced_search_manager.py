import tkinter as tk
from gui.modern_styles import ModernColors, update_status_bar


class EnhancedSearchManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.all_entries = []
        self.current_search_term = ""
        self.search_filters = {
            'title': True,
            'username': True,
            'url': True,
            'notes': True
        }
        
    def perform_search(self, search_term):
        self.current_search_term = search_term.strip()
        
        if not self.current_search_term:
            self.show_all_entries()
            return
        
        filtered_entries = self._filter_entries(self.current_search_term)
        
        if hasattr(self.main_window, 'table_manager'):
            self.main_window.table_manager.update_table(filtered_entries)
        
        self._update_search_status(filtered_entries)
    
    def _filter_entries(self, search_term):
        if not self.all_entries:
            return []
        
        search_term_lower = search_term.lower()
        filtered_entries = []
        
        for entry in self.all_entries:
            if self._entry_matches_search(entry, search_term_lower):
                filtered_entries.append(entry)
        
        return filtered_entries
    
    def _entry_matches_search(self, entry, search_term_lower):
        if self.search_filters.get('title', True):
            if search_term_lower in entry.title.lower():
                return True
        
        if self.search_filters.get('username', True):
            if search_term_lower in entry.username.lower():
                return True
        
        if self.search_filters.get('url', True):
            if search_term_lower in entry.url.lower():
                return True
        
        if self.search_filters.get('notes', True):
            if search_term_lower in entry.notes.lower():
                return True
        
        return False
    
    def show_all_entries(self):
        if hasattr(self.main_window, 'table_manager'):
            self.main_window.table_manager.update_table(self.all_entries)
        
        if hasattr(self.main_window, 'status_label') and self.main_window.status_label:
            update_status_bar(self.main_window.status_label, 
                            f"Showing all {len(self.all_entries)} entries", "normal")
    
    def refresh_entries_cache(self, entries):
        self.all_entries = entries.copy()
    
    def _update_search_status(self, filtered_entries):
        if not hasattr(self.main_window, 'status_label') or not self.main_window.status_label:
            return
        
        total_count = len(self.all_entries)
        filtered_count = len(filtered_entries)
        
        if filtered_count == 0:
            status_text = f"No matches for '{self.current_search_term}'"
            status_type = "warning"
        elif filtered_count == total_count:
            status_text = f"All {total_count} entries match '{self.current_search_term}'"
            status_type = "info"
        else:
            status_text = f"Found {filtered_count} of {total_count} entries"
            status_type = "info"
        
        update_status_bar(self.main_window.status_label, status_text, status_type)
    
    def has_active_search(self):
        return bool(self.current_search_term)
    
    def get_current_search_term(self):
        return self.current_search_term
    
    def clear_search(self):
        self.current_search_term = ""
        self.show_all_entries()
    
    def highlight_search_results(self, search_term):
        pass
    
    def search_in_category(self, category, search_term):
        old_filters = self.search_filters.copy()
        
        self.search_filters = {key: False for key in self.search_filters}
        self.search_filters[category] = True
        
        filtered_entries = self._filter_entries(search_term)
        
        self.search_filters = old_filters
        
        return filtered_entries
    
    def get_search_suggestions(self, partial_term):
        if len(partial_term) < 2:
            return []
        
        suggestions = set()
        partial_lower = partial_term.lower()
        
        for entry in self.all_entries:
            title_words = entry.title.lower().split()
            for word in title_words:
                if word.startswith(partial_lower) and len(word) > len(partial_term):
                    suggestions.add(word)
            
            if entry.username and entry.username.lower().startswith(partial_lower):
                suggestions.add(entry.username.lower())
        
        return sorted(list(suggestions))[:5]
    
    def create_search_filter_menu(self, parent):
        filter_frame = tk.Frame(parent, bg=ModernColors.WINDOW_BG)
        
        tk.Label(filter_frame, text="Search in:", 
                bg=ModernColors.WINDOW_BG, fg=ModernColors.TEXT_SECONDARY,
                font=('Segoe UI', 8, 'normal')).pack(side='left', padx=(0, 8))
        
        for filter_name, display_name in [
            ('title', 'Title'),
            ('username', 'Username'), 
            ('url', 'URL'),
            ('notes', 'Notes')
        ]:
            var = tk.BooleanVar(value=self.search_filters[filter_name])
            
            cb = tk.Checkbutton(filter_frame, text=display_name, variable=var,
                               bg=ModernColors.WINDOW_BG, fg=ModernColors.TEXT_PRIMARY,
                               font=('Segoe UI', 8, 'normal'),
                               activebackground=ModernColors.WINDOW_BG,
                               selectcolor=ModernColors.INPUT_BG,
                               command=lambda fn=filter_name, v=var: self._update_filter(fn, v))
            cb.pack(side='left', padx=4)
        
        return filter_frame
    
    def _update_filter(self, filter_name, var):
        self.search_filters[filter_name] = var.get()
        
        if self.current_search_term:
            self.perform_search(self.current_search_term)


class AdvancedSearchDialog:
    def __init__(self, parent, search_manager):
        self.search_manager = search_manager
        self.result = None
        
        from gui.modern_styles import ModernStyles
        ModernStyles.setup_modern_theme()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Advanced Search")
        self.dialog.geometry("500x400")
        self.dialog.configure(bg=ModernColors.WINDOW_BG)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 100, 
            parent.winfo_rooty() + 100
        ))
        
        self._create_search_ui()
        self.dialog.wait_window()
    
    def _create_search_ui(self):
        from gui.modern_styles import create_modern_frame, ModernSpacing
        
        main_frame = create_modern_frame(self.dialog)
        main_frame.pack(expand=True, fill='both', padx=ModernSpacing.DIALOG_PADDING, 
                       pady=ModernSpacing.DIALOG_PADDING)
        
        title_label = tk.Label(main_frame, text="🔍 Advanced Search",
                              bg=ModernColors.WINDOW_BG, fg=ModernColors.TEXT_PRIMARY,
                              font=('Segoe UI', 12, 'bold'))
        title_label.pack(pady=(0, ModernSpacing.GROUP_SPACING))
        
        search_frame = create_modern_frame(main_frame)
        search_frame.pack(fill='x', pady=(0, ModernSpacing.GROUP_SPACING))
        
        tk.Label(search_frame, text="Search term:",
                bg=ModernColors.WINDOW_BG, fg=ModernColors.TEXT_PRIMARY,
                font=('Segoe UI', 9, 'normal')).pack(anchor='w')
        
        from gui.modern_styles import create_modern_entry
        self.search_entry = create_modern_entry(search_frame)
        self.search_entry.pack(fill='x', pady=(2, 0))
        
        filters_frame = self.search_manager.create_search_filter_menu(main_frame)
        filters_frame.pack(fill='x', pady=(0, ModernSpacing.GROUP_SPACING))
        
        results_frame = create_modern_frame(main_frame)
        results_frame.pack(fill='both', expand=True, pady=(0, ModernSpacing.GROUP_SPACING))
        
        tk.Label(results_frame, text="Search Results:",
                bg=ModernColors.WINDOW_BG, fg=ModernColors.TEXT_PRIMARY,
                font=('Segoe UI', 9, 'bold')).pack(anchor='w')
        
        self.results_listbox = tk.Listbox(results_frame,
                                         bg=ModernColors.INPUT_BG,
                                         fg=ModernColors.TEXT_PRIMARY,
                                         font=('Segoe UI', 9, 'normal'),
                                         selectbackground=ModernColors.ACCENT_BLUE,
                                         height=10)
        self.results_listbox.pack(fill='both', expand=True, pady=(4, 0))
        
        button_frame = create_modern_frame(main_frame)
        button_frame.pack(fill='x')
        
        from gui.modern_styles import create_toolbar_button
        
        search_btn = tk.Button(button_frame, text="Search",
                              command=self._perform_search,
                              bg=ModernColors.ACCENT_GREEN, fg="white",
                              font=('Segoe UI', 9, 'bold'),
                              relief='raised', bd=1, padx=15, pady=4)
        search_btn.pack(side='left')
        
        close_btn = tk.Button(button_frame, text="Close",
                             command=self.dialog.destroy,
                             bg=ModernColors.BUTTON_BG, fg=ModernColors.TEXT_PRIMARY,
                             font=('Segoe UI', 9, 'normal'),
                             relief='raised', bd=1, padx=15, pady=4)
        close_btn.pack(side='right')
        
        self.search_entry.bind('<KeyRelease>', self._on_search_change)
        self.search_entry.bind('<Return>', lambda e: self._perform_search())
    
    def _on_search_change(self, event):
        search_term = self.search_entry.get()
        if len(search_term) >= 2:
            self._perform_search()
    
    def _perform_search(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            return
        
        results = self.search_manager._filter_entries(search_term)
        
        self.results_listbox.delete(0, tk.END)
        for entry in results:
            display_text = f"{entry.title} - {entry.username}"
            self.results_listbox.insert(tk.END, display_text)