import tkinter as tk
from tkinter import ttk


class ModernColors:
    WINDOW_BG = "#f5f5f5"
    DIALOG_BG = "#f5f5f5"
    PANEL_BG = "#ffffff"
    SIDEBAR_BG = "#f0f0f0"
    
    TOOLBAR_BG = "#f8f8f8"
    TOOLBAR_BORDER = "#d0d0d0"
    BUTTON_BG = "#e8e8e8"
    BUTTON_HOVER = "#d8d8d8"
    
    TEXT_PRIMARY = "#333333"
    TEXT_SECONDARY = "#666666"
    TEXT_DISABLED = "#999999"
    
    INPUT_BG = "#ffffff"
    INPUT_BORDER = "#c0c0c0"
    INPUT_FOCUS = "#6ba644"
    
    ACCENT_GREEN = "#6ba644"
    ACCENT_GREEN_DARK = "#5a9137"
    ACCENT_GREEN_LIGHT = "#8bc34a"
    ACCENT_BLUE = "#4a90e2"
    ACCENT_BLUE_LIGHT = "#e3f2fd"
    
    SUCCESS = "#6ba644"
    WARNING = "#ff8c00"
    ERROR = "#d32f2f"
    INFO = "#6ba644"
    
    BORDER = "#d0d0d0"
    BORDER_LIGHT = "#e0e0e0"
    
    TABLE_HEADER = "#f5f5f5"
    TABLE_ROW_HOVER = "#f9f9f9"
    TABLE_ROW_SELECTED = "#e8f5e8"


class ModernStyles:
    @staticmethod
    def setup_modern_theme():
        style = ttk.Style()
        
        if 'winnative' in style.theme_names():
            style.theme_use('winnative')
        else:
            style.theme_use('default')
        
        style.configure('Modern.TButton',
                        background=ModernColors.BUTTON_BG,
                        foreground=ModernColors.TEXT_PRIMARY,
                        borderwidth=1,
                        relief='raised',
                        font=('Segoe UI', 8, 'normal'),
                        padding=(8, 4))
        
        style.map('Modern.TButton',
                  background=[('active', ModernColors.BUTTON_HOVER), 
                             ('pressed', '#c0c0c0')],
                  relief=[('pressed', 'sunken')])
        
        style.configure('ModernPrimary.TButton',
                        background=ModernColors.ACCENT_GREEN,
                        foreground='#ffffff',
                        borderwidth=1,
                        relief='raised',
                        font=('Segoe UI', 8, 'bold'),
                        padding=(10, 4))
        
        style.map('ModernPrimary.TButton',
                  background=[('active', ModernColors.ACCENT_GREEN_DARK),
                             ('disabled', '#cccccc')],
                  foreground=[('disabled', '#999999')])
        
        style.configure('Modern.Treeview',
                        background=ModernColors.PANEL_BG,
                        foreground=ModernColors.TEXT_PRIMARY,
                        fieldbackground=ModernColors.PANEL_BG,
                        font=('Segoe UI', 9, 'normal'),
                        borderwidth=1,
                        relief='solid',
                        rowheight=22)
        
        style.configure('Modern.Treeview.Heading',
                        background=ModernColors.TABLE_HEADER,
                        foreground=ModernColors.TEXT_SECONDARY,
                        font=('Segoe UI', 8, 'normal'),
                        relief='flat',
                        borderwidth=1,
                        padding=(8, 4))
        
        style.map('Modern.Treeview',
                  background=[('selected', '!focus', ModernColors.TABLE_ROW_SELECTED),
                             ('selected', 'focus', ModernColors.ACCENT_GREEN)],
                  foreground=[('selected', '!focus', ModernColors.TEXT_PRIMARY),
                             ('selected', 'focus', '#ffffff')])
        
        style.configure('Modern.TLabelframe',
                        background=ModernColors.WINDOW_BG,
                        borderwidth=1,
                        relief='solid',
                        bordercolor=ModernColors.BORDER)
        
        style.configure('Modern.TLabelframe.Label',
                        background=ModernColors.WINDOW_BG,
                        foreground=ModernColors.TEXT_SECONDARY,
                        font=('Segoe UI', 8, 'bold'))
        
        style.configure('Classic.TButton',
                        background=ModernColors.BUTTON_BG,
                        foreground=ModernColors.TEXT_PRIMARY,
                        borderwidth=1,
                        relief='raised',
                        font=('Segoe UI', 9, 'normal'),
                        padding=(10, 2))
        
        style.map('Classic.TButton',
                  background=[('active', ModernColors.BUTTON_HOVER), ('pressed', '#c5c5c5')],
                  relief=[('pressed', 'sunken')])
        
        style.configure('ClassicPrimary.TButton',
                        background='#e0f0ff',
                        foreground='#000000',
                        borderwidth=1,
                        relief='raised',
                        font=('Segoe UI', 9, 'bold'),
                        padding=(10, 2))
        
        style.map('ClassicPrimary.TButton',
                  foreground=[('disabled', '#000000'), ('!disabled', '#000000')],
                  background=[('disabled', '#dcdcdc'), ('active', '#c0d4f0'), ('!disabled', '#e0f0ff')],
                  relief=[('pressed', 'sunken')],
                  bordercolor=[('disabled', '#a0a0a0')])
        
        style.configure('Classic.Treeview',
                        background=ModernColors.PANEL_BG,
                        foreground=ModernColors.TEXT_PRIMARY,
                        fieldbackground=ModernColors.PANEL_BG,
                        font=('Segoe UI', 9, 'normal'),
                        borderwidth=1,
                        relief='sunken')
        
        style.configure('Classic.Treeview.Heading',
                        background=ModernColors.TABLE_HEADER,
                        foreground=ModernColors.TEXT_PRIMARY,
                        font=('Segoe UI', 9, 'bold'),
                        relief='raised',
                        borderwidth=1)
        
        style.map('Classic.Treeview',
                  background=[('selected', '!focus', '#e5e5e5'),
                              ('selected', 'focus', ModernColors.ACCENT_GREEN)],
                  foreground=[('selected', '!focus', ModernColors.TEXT_PRIMARY),
                              ('selected', 'focus', '#ffffff')])
        
        style.configure('Classic.TLabelframe',
                        background=ModernColors.WINDOW_BG,
                        borderwidth=2,
                        relief='groove')
        
        style.configure('Classic.TLabelframe.Label',
                        background=ModernColors.WINDOW_BG,
                        foreground=ModernColors.TEXT_PRIMARY,
                        font=('Segoe UI', 9, 'bold'))
    
    @staticmethod
    def setup_windows_classic_theme():
        ModernStyles.setup_modern_theme()


def create_modern_entry(parent, show=None, width=None, font_size=9):
    entry = tk.Entry(parent,
                     bg=ModernColors.INPUT_BG,
                     fg=ModernColors.TEXT_PRIMARY,
                     font=('Segoe UI', font_size, 'normal'),
                     relief='solid',
                     bd=1,
                     show=show,
                     insertbackground=ModernColors.TEXT_PRIMARY,
                     highlightthickness=1,
                     highlightbackground=ModernColors.INPUT_BORDER,
                     highlightcolor=ModernColors.INPUT_FOCUS)
    
    if width:
        entry.configure(width=width)
    
    return entry


def create_modern_text(parent, height=3, width=None, font_size=9):
    text = tk.Text(parent,
                   bg=ModernColors.INPUT_BG,
                   fg=ModernColors.TEXT_PRIMARY,
                   font=('Segoe UI', font_size, 'normal'),
                   relief='solid',
                   bd=1,
                   height=height,
                   insertbackground=ModernColors.TEXT_PRIMARY,
                   highlightthickness=1,
                   highlightbackground=ModernColors.INPUT_BORDER,
                   highlightcolor=ModernColors.INPUT_FOCUS)
    
    if width:
        text.configure(width=width)
    
    return text


def create_modern_frame(parent, bg_color=None, relief='flat'):
    if bg_color is None:
        bg_color = ModernColors.WINDOW_BG
    
    frame = tk.Frame(parent,
                     bg=bg_color,
                     relief=relief,
                     bd=1 if relief != 'flat' else 0)
    
    return frame


def create_modern_label_frame(parent, text, bg_color=None):
    if bg_color is None:
        bg_color = ModernColors.WINDOW_BG
    
    label_frame = tk.LabelFrame(parent,
                                text=text,
                                bg=bg_color,
                                fg=ModernColors.TEXT_SECONDARY,
                                font=('Segoe UI', 8, 'bold'),
                                relief='solid',
                                bd=1,
                                borderwidth=1)
    
    return label_frame


def create_toolbar_frame(parent):
    toolbar = tk.Frame(parent,
                       bg=ModernColors.TOOLBAR_BG,
                       relief='flat',
                       bd=0,
                       height=36)
    toolbar.pack_propagate(False)
    return toolbar


def create_toolbar_separator(parent):
    separator = tk.Frame(parent,
                         bg=ModernColors.BORDER,
                         width=1,
                         height=20)
    return separator


def create_toolbar_button(parent, text, command, icon=None):
    if icon:
        display_text = f"{icon} {text}" if text else icon
    else:
        display_text = text
    
    button = tk.Button(parent,
                       text=display_text,
                       command=command,
                       bg=ModernColors.BUTTON_BG,
                       fg=ModernColors.TEXT_PRIMARY,
                       font=('Segoe UI', 8, 'normal'),
                       relief='raised',
                       bd=1,
                       padx=8,
                       pady=4,
                       cursor='hand2')
    
    def on_enter(event):
        button.config(bg=ModernColors.BUTTON_HOVER)
    
    def on_leave(event):
        button.config(bg=ModernColors.BUTTON_BG)
    
    button.bind('<Enter>', on_enter)
    button.bind('<Leave>', on_leave)
    
    return button


def create_search_frame(parent):
    search_frame = tk.Frame(parent, bg=ModernColors.TOOLBAR_BG)
    
    search_entry = create_modern_entry(search_frame, font_size=8)
    search_entry.configure(width=25)
    
    clear_button = tk.Button(search_frame,
                            text="✕",
                            font=('Segoe UI', 7, 'normal'),
                            bg=ModernColors.BUTTON_BG,
                            fg=ModernColors.TEXT_SECONDARY,
                            relief='flat',
                            bd=0,
                            padx=4,
                            pady=2,
                            cursor='hand2')
    
    search_entry.pack(side='left')
    clear_button.pack(side='left', padx=(2, 0))
    
    return search_frame, search_entry, clear_button


def create_status_bar(parent, text="Ready"):
    status_frame = tk.Frame(parent,
                            bg=ModernColors.SIDEBAR_BG,
                            relief='solid',
                            bd=1,
                            height=22)
    status_frame.pack_propagate(False)
    
    label = tk.Label(status_frame,
                     text=text,
                     bg=ModernColors.SIDEBAR_BG,
                     fg=ModernColors.TEXT_SECONDARY,
                     font=('Segoe UI', 8, 'normal'),
                     anchor='w')
    label.pack(side='left', fill='x', expand=True, padx=6, pady=2)
    
    return status_frame, label


def update_status_bar(label, text, status_type="normal"):
    colors = {
        "normal": ModernColors.TEXT_SECONDARY,
        "success": ModernColors.SUCCESS,
        "warning": ModernColors.WARNING,
        "error": ModernColors.ERROR,
        "info": ModernColors.INFO
    }
    
    label.configure(text=text, fg=colors.get(status_type, ModernColors.TEXT_SECONDARY))


class ModernSpacing:
    XS = 2
    SM = 4
    MD = 6
    LG = 8
    XL = 12
    XXL = 16
    
    DIALOG_PADDING = 12
    TOOLBAR_PADDING = 6
    BUTTON_SPACING = 4
    GROUP_SPACING = 8
    SECTION_SPACING = 12


class WindowsClassicColors:
    WINDOW_BG = ModernColors.WINDOW_BG
    DIALOG_BG = ModernColors.DIALOG_BG
    PANEL_BG = ModernColors.PANEL_BG
    BUTTON_BG = ModernColors.BUTTON_BG
    
    TEXT_PRIMARY = ModernColors.TEXT_PRIMARY
    TEXT_SECONDARY = ModernColors.TEXT_SECONDARY
    TEXT_DISABLED = ModernColors.TEXT_DISABLED
    
    INPUT_BG = ModernColors.INPUT_BG
    INPUT_BORDER = ModernColors.INPUT_BORDER
    INPUT_FOCUS = ModernColors.INPUT_FOCUS
    
    ACCENT = ModernColors.ACCENT_GREEN
    ACCENT_LIGHT = ModernColors.ACCENT_GREEN_LIGHT
    ACCENT_DARK = ModernColors.ACCENT_GREEN_DARK
    
    SUCCESS = ModernColors.SUCCESS
    WARNING = ModernColors.WARNING
    ERROR = ModernColors.ERROR
    
    BORDER = ModernColors.BORDER
    BORDER_DARK = ModernColors.BORDER
    SHADOW = ModernColors.BORDER
    HIGHLIGHT = "#ffffff"
    
    TREE_BG = ModernColors.PANEL_BG
    TREE_HEADER = ModernColors.TABLE_HEADER
    TREE_SELECTED = ModernColors.ACCENT_GREEN
    TREE_SELECTED_TEXT = "#ffffff"

WindowsClassicStyles = ModernStyles
ClassicSpacing = ModernSpacing

def create_classic_entry(parent, show=None, width=None):
    return create_modern_entry(parent, show, width)

def create_classic_text(parent, height=3, width=None):
    return create_modern_text(parent, height, width)

def create_classic_frame(parent, bg_color=None, relief='flat'):
    return create_modern_frame(parent, bg_color, relief)

def create_classic_label_frame(parent, text, bg_color=None):
    return create_modern_label_frame(parent, text, bg_color)

def create_classic_panel(parent, relief='raised'):
    panel = tk.Frame(parent,
                     bg=ModernColors.SIDEBAR_BG,
                     relief=relief,
                     bd=1)
    return panel