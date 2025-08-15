import tkinter as tk
from tkinter import ttk
from gui.modern_styles import ModernColors, ModernSpacing
from gui.localization import _


class TableManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.tree = None
        self.tree_container = None
        self.sort_column = None
        self.sort_reverse = False
        self.entry_item_mapping = {}
        
    def create_table(self, parent):
        table_frame = tk.Frame(parent, bg=ModernColors.PANEL_BG)
        
        header_frame = tk.Frame(table_frame, 
                               bg=ModernColors.ACCENT_GREEN, 
                               height=28)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame, 
                               text=_("table_header"),
                               bg=ModernColors.ACCENT_GREEN,
                               fg="white",
                               font=('Segoe UI', 9, 'bold'))
        header_label.pack(side='left', padx=12, pady=6)
        
        count_label = tk.Label(header_frame,
                              text="(0)",
                              bg=ModernColors.ACCENT_GREEN,
                              fg="white",
                              font=('Segoe UI', 8, 'normal'))
        count_label.pack(side='left', pady=6)
        
        self.header_count_label = count_label
        
        self.tree_container = tk.Frame(table_frame, bg=ModernColors.PANEL_BG)
        self.tree_container.pack(fill='both', expand=True)
        
        self._create_treeview()
        self._setup_context_menu()
        
        return table_frame
    
    def _create_treeview(self):
        columns = ('username', 'password', 'url', 'totp', 'modified')
        
        self.tree = ttk.Treeview(self.tree_container, 
                                columns=columns,
                                show='tree headings', 
                                style='Modern.Treeview')
        
        self.tree.heading('#0', text=_("table_title"), anchor='w', 
                         command=lambda: self._sort_by_column('#0'))
        self.tree.heading('username', text=_("table_username"), anchor='w',
                         command=lambda: self._sort_by_column('username'))
        self.tree.heading('password', text=_("table_password"), anchor='w',
                         command=lambda: self._sort_by_column('password'))
        self.tree.heading('url', text=_("table_url"), anchor='w',
                         command=lambda: self._sort_by_column('url'))
        self.tree.heading('totp', text=_("table_2fa"), anchor='center',
                         command=lambda: self._sort_by_column('totp'))
        self.tree.heading('modified', text=_("table_modified"), anchor='w',
                         command=lambda: self._sort_by_column('modified'))
        
        self.tree.column('#0', width=200, minwidth=150)
        self.tree.column('username', width=150, minwidth=100)
        self.tree.column('password', width=120, minwidth=80)
        self.tree.column('url', width=200, minwidth=150)
        self.tree.column('totp', width=80, minwidth=60)
        self.tree.column('modified', width=120, minwidth=100)
        
        scrollbar_v = ttk.Scrollbar(self.tree_container, orient='vertical', 
                                   command=self.tree.yview)
        scrollbar_h = ttk.Scrollbar(self.tree_container, orient='horizontal', 
                                   command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=scrollbar_v.set, 
                           xscrollcommand=scrollbar_h.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_v.grid(row=0, column=1, sticky='ns')
        scrollbar_h.grid(row=1, column=0, sticky='ew')
        
        self.tree_container.grid_rowconfigure(0, weight=1)
        self.tree_container.grid_columnconfigure(0, weight=1)
        
        self.tree.bind('<Double-Button-1>', self._on_double_click)
        self.tree.bind('<Button-1>', self._on_single_click)
        self.tree.bind('<KeyRelease>', self._on_key_press)
    
    def _setup_context_menu(self):
        if hasattr(self.main_window, 'context_menu_manager'):
            self.main_window.context_menu_manager.setup_treeview_context_menu(self.tree)
    
    def _sort_by_column(self, column):
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        entries = self._get_current_entries()
        if not entries:
            return
        
        if column == '#0':
            entries.sort(key=lambda x: x.title.lower(), reverse=self.sort_reverse)
        elif column == 'username':
            entries.sort(key=lambda x: x.username.lower(), reverse=self.sort_reverse)
        elif column == 'password':
            entries.sort(key=lambda x: len(x.password), reverse=self.sort_reverse)
        elif column == 'url':
            entries.sort(key=lambda x: x.url.lower(), reverse=self.sort_reverse)
        elif column == 'totp':
            entries.sort(key=lambda x: x.has_totp(), reverse=self.sort_reverse)
        elif column == 'modified':
            entries.sort(key=lambda x: x.modified, reverse=self.sort_reverse)
        
        self.update_table(entries)
        self._update_sort_indicators()
    
    def _update_sort_indicators(self):
        for col in ['#0', 'username', 'password', 'url', 'totp', 'modified']:
            current_text = self.tree.heading(col)['text']
            
            clean_text = current_text.replace(' ↑', '').replace(' ↓', '')
            
            if col == self.sort_column:
                indicator = ' ↓' if self.sort_reverse else ' ↑'
                self.tree.heading(col, text=clean_text + indicator)
            else:
                self.tree.heading(col, text=clean_text)
    
    def _get_current_entries(self):
        if hasattr(self.main_window, 'pm') and self.main_window.pm.is_unlocked:
            return self.main_window.pm.list_entries()
        return []
    
    def update_table(self, entries):
        selected_title = self.get_selected_entry_title()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.entry_item_mapping.clear()
        
        for entry in entries:
            item_id = self._insert_entry(entry)
            self.entry_item_mapping[entry.title] = item_id
        
        self.header_count_label.config(text=f"({len(entries)})")
        
        if selected_title and selected_title in self.entry_item_mapping:
            item_id = self.entry_item_mapping[selected_title]
            self.tree.selection_set(item_id)
            self.tree.focus(item_id)
            self.tree.see(item_id)
        
        if hasattr(self.main_window, 'status_label') and self.main_window.status_label:
            from gui.modern_styles import update_status_bar
            update_status_bar(self.main_window.status_label, 
                            f"{_('status_showing')} {len(entries)} {_('status_entries')}", "normal")
    
    def _insert_entry(self, entry):
        title_with_icon = f"🔒 {entry.title}"
        
        password_display = "•" * min(len(entry.password), 8) if entry.password else ""
        
        url_display = self._format_url(entry.url)
        
        totp_display = "🔐" if entry.has_totp() else ""
        
        modified_display = self._format_date(entry.modified)
        
        item_id = self.tree.insert('', 'end', 
                                  text=title_with_icon,
                                  values=(entry.username, 
                                         password_display,
                                         url_display, 
                                         totp_display,
                                         modified_display))
        
        self._update_totp_display(item_id, entry)
        
        return item_id
    
    def _format_url(self, url):
        if not url:
            return ""
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            if domain.startswith('www.'):
                domain = domain[4:]
            
            if len(domain) > 30:
                domain = domain[:27] + "..."
            
            return domain
        except:
            return url[:30] + "..." if len(url) > 30 else url
    
    def _format_date(self, date_str):
        if not date_str:
            return ""
        
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%d.%m.%Y")
        except:
            return date_str[:10] if len(date_str) >= 10 else date_str
    
    def _update_totp_display(self, item_id, entry):
        if not entry.has_totp():
            return
        
        if hasattr(self.main_window, 'totp_manager'):
            current_code, remaining_time = self.main_window.totp_manager.get_current_totp(entry.totp_secret)
            if current_code:
                totp_display = f"🔐 {current_code[:3]}•••• ({remaining_time}s)"
                values = list(self.tree.item(item_id)['values'])
                if len(values) >= 4:
                    values[3] = totp_display
                    self.tree.item(item_id, values=values)
    
    def _on_double_click(self, event):
        if hasattr(self.main_window, 'edit_password'):
            self.main_window.edit_password()
    
    def _on_single_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.tree.focus(item)
    
    def _on_key_press(self, event):
        if event.keysym == 'Return':
            if hasattr(self.main_window, 'edit_password'):
                self.main_window.edit_password()
        elif event.keysym == 'Delete':
            if hasattr(self.main_window, 'delete_password'):
                self.main_window.delete_password()
    
    def get_selected_entry_title(self):
        selection = self.tree.selection()
        if not selection:
            return None
        
        item = self.tree.item(selection[0])
        title_with_icon = item['text']
        
        return title_with_icon.replace('🔒 ', '')
    
    def get_selected_entry(self):
        title = self.get_selected_entry_title()
        if not title:
            return None
        
        if hasattr(self.main_window, 'pm') and self.main_window.pm.is_unlocked:
            return self.main_window.pm.get_entry(title)
        return None
    
    def refresh_totp_codes(self):
        if not hasattr(self.main_window, 'totp_manager'):
            return
        
        for item in self.tree.get_children():
            title_with_icon = self.tree.item(item)['text']
            title = title_with_icon.replace('🔒 ', '')
            
            if hasattr(self.main_window, 'pm') and self.main_window.pm.is_unlocked:
                entry = self.main_window.pm.get_entry(title)
                if entry and entry.has_totp():
                    self._update_totp_display(item, entry)
    
    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.entry_item_mapping.clear()
        self.header_count_label.config(text="(0)")
    
    def select_entry_by_title(self, title):
        if title in self.entry_item_mapping:
            item_id = self.entry_item_mapping[title]
            self.tree.selection_set(item_id)
            self.tree.focus(item_id)
            self.tree.see(item_id)
    
    def get_entry_count(self):
        return len(self.tree.get_children())