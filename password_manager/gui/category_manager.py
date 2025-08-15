import tkinter as tk
from tkinter import ttk
from gui.modern_styles import ModernColors, create_modern_frame
from gui.localization import _

class CategoryManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.sidebar_frame = None
        self.category_buttons = {}
        self.current_category = "All"
        self.sidebar_visible = True
        
        self.categories = {
            "All": {"icon": "📋", "color": ModernColors.TEXT_PRIMARY},
            "Banking": {"icon": "🏦", "color": "#2e7d32"},
            "Shopping": {"icon": "🛒", "color": "#f57c00"},
            "Gaming": {"icon": "🎮", "color": "#7b1fa2"},
            "Social": {"icon": "👥", "color": "#1976d2"},
            "Work": {"icon": "💼", "color": "#455a64"},
            "Email": {"icon": "📧", "color": "#c62828"},
            "Cloud": {"icon": "☁", "color": "#0277bd"},
            "Development": {"icon": "💻", "color": "#388e3c"},
            "Other": {"icon": "📁", "color": "#616161"}
        }
    
    def create_sidebar(self, parent):
        self.sidebar_frame = create_modern_frame(parent, ModernColors.SIDEBAR_BG, relief='solid')
        self.sidebar_frame.configure(width=220, bd=1, borderwidth=1)
        
        header_frame = create_modern_frame(self.sidebar_frame, ModernColors.SIDEBAR_BG)
        header_frame.pack(fill='x', padx=8, pady=(8, 4))
        
        header_label = tk.Label(header_frame, text="📂 Categories",
                               bg=ModernColors.SIDEBAR_BG, fg=ModernColors.TEXT_PRIMARY,
                               font=('Segoe UI', 10, 'bold'))
        header_label.pack(anchor='w')
        
        separator = tk.Frame(self.sidebar_frame, bg=ModernColors.BORDER, height=1)
        separator.pack(fill='x', padx=8, pady=4)
        
        self.buttons_frame = create_modern_frame(self.sidebar_frame, ModernColors.SIDEBAR_BG)
        self.buttons_frame.pack(fill='both', expand=True, padx=4, pady=4)
        
        self._create_category_buttons()
        
        return self.sidebar_frame
    
    def _create_category_buttons(self):
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
        
        self.category_buttons.clear()
        
        counts = self._get_category_counts()
        
        for category, info in self.categories.items():
            count = counts.get(category, 0)
            if category == "All":
                count = sum(counts.values())
            
            is_active = self.current_category == category
            
            button_frame = create_modern_frame(self.buttons_frame, 
                                             ModernColors.ACCENT_BLUE if is_active else ModernColors.SIDEBAR_BG)
            button_frame.pack(fill='x', pady=1)
            
            button = tk.Button(button_frame,
                              text=f"{info['icon']} {category}",
                              command=lambda c=category: self._on_category_click(c),
                              bg=ModernColors.ACCENT_BLUE if is_active else ModernColors.SIDEBAR_BG,
                              fg="white" if is_active else ModernColors.TEXT_PRIMARY,
                              font=('Segoe UI', 9, 'bold' if is_active else 'normal'),
                              relief='flat', bd=0, padx=8, pady=4,
                              anchor='w', cursor='hand2')
            button.pack(side='left', fill='x', expand=True)
            
            count_label = tk.Label(button_frame, text=f"({count})",
                                  bg=ModernColors.ACCENT_BLUE if is_active else ModernColors.SIDEBAR_BG,
                                  fg="white" if is_active else ModernColors.TEXT_SECONDARY,
                                  font=('Segoe UI', 8, 'normal'))
            count_label.pack(side='right', padx=(0, 8))
            
            self.category_buttons[category] = {'button': button, 'count': count_label, 'frame': button_frame}
            
            if not is_active:
                button.bind('<Enter>', lambda e, b=button, f=button_frame, c=count_label: self._on_hover_enter(b, f, c))
                button.bind('<Leave>', lambda e, b=button, f=button_frame, c=count_label: self._on_hover_leave(b, f, c))
                count_label.bind('<Enter>', lambda e, b=button, f=button_frame, c=count_label: self._on_hover_enter(b, f, c))
                count_label.bind('<Leave>', lambda e, b=button, f=button_frame, c=count_label: self._on_hover_leave(b, f, c))
    
    def _on_hover_enter(self, button, frame, count_label):
        if self.current_category != self._get_category_from_button(button):
            button.configure(bg=ModernColors.BUTTON_HOVER)
            frame.configure(bg=ModernColors.BUTTON_HOVER)
            count_label.configure(bg=ModernColors.BUTTON_HOVER)
    
    def _on_hover_leave(self, button, frame, count_label):
        if self.current_category != self._get_category_from_button(button):
            button.configure(bg=ModernColors.SIDEBAR_BG)
            frame.configure(bg=ModernColors.SIDEBAR_BG)
            count_label.configure(bg=ModernColors.SIDEBAR_BG)
    
    def _get_category_from_button(self, button):
        for category, widgets in self.category_buttons.items():
            if widgets['button'] == button:
                return category
        return None
    
    def _on_category_click(self, category):
        self.current_category = category
        self._update_active_button()
        self._filter_entries_by_category()
    
    def _update_active_button(self):
        for cat, widgets in self.category_buttons.items():
            is_active = cat == self.current_category
            
            widgets['button'].configure(
                bg=ModernColors.ACCENT_BLUE if is_active else ModernColors.SIDEBAR_BG,
                fg="white" if is_active else ModernColors.TEXT_PRIMARY,
                font=('Segoe UI', 9, 'bold' if is_active else 'normal')
            )
            
            widgets['count'].configure(
                bg=ModernColors.ACCENT_BLUE if is_active else ModernColors.SIDEBAR_BG,
                fg="white" if is_active else ModernColors.TEXT_SECONDARY
            )
            
            widgets['frame'].configure(
                bg=ModernColors.ACCENT_BLUE if is_active else ModernColors.SIDEBAR_BG
            )
    
    def _filter_entries_by_category(self):
        if hasattr(self.main_window, 'pm') and self.main_window.pm.is_unlocked:
            entries = self.main_window.pm.get_entries_by_category(self.current_category)
            
            if hasattr(self.main_window, 'table_manager'):
                self.main_window.table_manager.update_table(entries)
            
            if hasattr(self.main_window, 'status_label') and self.main_window.status_label:
                from gui.modern_styles import update_status_bar
                if self.current_category == "All":
                    status_text = f"Showing all {len(entries)} entries"
                else:
                    status_text = f"Showing {len(entries)} entries in {self.current_category}"
                update_status_bar(self.main_window.status_label, status_text, "normal")
    
    def _get_category_counts(self):
        if hasattr(self.main_window, 'pm') and self.main_window.pm.is_unlocked:
            return self.main_window.pm.get_categories_with_counts()
        return {}
    
    def refresh_categories(self):
        self._create_category_buttons()
        self._filter_entries_by_category()
    
    def get_current_category(self):
        return self.current_category
    
    def set_category(self, category):
        if category in self.categories:
            self.current_category = category
            self._update_active_button()
            self._filter_entries_by_category()
    
    def toggle_sidebar(self):
        self.sidebar_visible = not self.sidebar_visible
        if self.sidebar_frame:
            if self.sidebar_visible:
                self.sidebar_frame.pack(side='left', fill='y', before=self.main_window.table_frame)
            else:
                self.sidebar_frame.pack_forget()
    
    def get_categories_list(self):
        return [cat for cat in self.categories.keys() if cat != "All"]