import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
from gui.modern_styles import WindowsClassicStyles, WindowsClassicColors, create_classic_frame, create_classic_label_frame, create_classic_entry, ClassicSpacing
from gui.password_strength_visualizer import PasswordStrengthVisualizer


class PasswordGeneratorDialog:
    def __init__(self, parent, password_generator):
        self.result = None
        self.password_generator = password_generator
        self.password_history = []
        self.strength_visualizer = None
        
        WindowsClassicStyles.setup_windows_classic_theme()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🎲 Passwort-Generator")
        self.dialog.geometry("650x750")
        self.dialog.configure(bg=WindowsClassicColors.WINDOW_BG)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)

        self.dialog.focus_set()
        self.dialog.focus_force()
        
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 25))
        
        self.create_generator_form()
        self.generate_password()
        self.dialog.wait_window()
    
    def create_generator_form(self):
        main_frame = create_classic_frame(self.dialog, WindowsClassicColors.DIALOG_BG)
        main_frame.pack(expand=True, fill='both', padx=ClassicSpacing.DIALOG_PADDING, pady=ClassicSpacing.DIALOG_PADDING)
        
        title_label = tk.Label(main_frame, text="🎲 Passwort-Generator", 
                              bg=WindowsClassicColors.DIALOG_BG, fg=WindowsClassicColors.TEXT_PRIMARY, 
                              font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=(0, ClassicSpacing.SECTION_SPACING))
        
        content_frame = tk.Frame(main_frame, bg=WindowsClassicColors.DIALOG_BG)
        content_frame.pack(expand=True, fill='both')
        
        left_frame = tk.Frame(content_frame, bg=WindowsClassicColors.DIALOG_BG)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, ClassicSpacing.LG))
        
        right_frame = tk.Frame(content_frame, bg=WindowsClassicColors.DIALOG_BG)
        right_frame.pack(side='right', fill='y')
        
        self._create_settings_section(left_frame)
        self._create_password_section(left_frame)
        self._create_actions_section(left_frame)
        self._create_history_section(left_frame)
        
        self._create_strength_visualization(right_frame)
    
    def _create_settings_section(self, parent):
        settings_frame = create_classic_label_frame(parent, "⚙️ Einstellungen")
        settings_frame.pack(fill='x', pady=(0, ClassicSpacing.GROUP_SPACING))
        
        settings_container = create_classic_frame(settings_frame, WindowsClassicColors.WINDOW_BG)
        settings_container.pack(fill='x', padx=ClassicSpacing.DIALOG_PADDING, pady=ClassicSpacing.DIALOG_PADDING)
        
        length_frame = create_classic_frame(settings_container, WindowsClassicColors.WINDOW_BG)
        length_frame.pack(fill='x', pady=(0, ClassicSpacing.SM))
        
        length_label = tk.Label(length_frame, text="Länge:", 
                               bg=WindowsClassicColors.WINDOW_BG, fg=WindowsClassicColors.TEXT_PRIMARY,
                               font=('Segoe UI', 9, 'normal'))
        length_label.pack(side='left')
        
        self.length_var = tk.IntVar(value=16)
        length_spinbox = tk.Spinbox(length_frame, from_=8, to=64, width=5, 
                                   textvariable=self.length_var, command=self.generate_password,
                                   bg=WindowsClassicColors.INPUT_BG, fg=WindowsClassicColors.TEXT_PRIMARY,
                                   font=('Segoe UI', 9, 'normal'), relief='sunken', bd=1)
        length_spinbox.pack(side='right')
        
        self.use_uppercase = tk.BooleanVar(value=True)
        self.use_lowercase = tk.BooleanVar(value=True)
        self.use_numbers = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        self.exclude_ambiguous = tk.BooleanVar(value=True)
        
        checkboxes = [
            ("✓ Großbuchstaben (A-Z)", self.use_uppercase),
            ("✓ Kleinbuchstaben (a-z)", self.use_lowercase),
            ("✓ Zahlen (0-9)", self.use_numbers),
            ("✓ Symbole (!@#$%...)", self.use_symbols),
            ("✓ Mehrdeutige Zeichen ausschließen (0,O,l,1...)", self.exclude_ambiguous)
        ]
        
        for text, var in checkboxes:
            cb = tk.Checkbutton(settings_container, text=text, variable=var, 
                               bg=WindowsClassicColors.WINDOW_BG, fg=WindowsClassicColors.TEXT_PRIMARY,
                               font=('Segoe UI', 9, 'normal'),
                               activebackground=WindowsClassicColors.WINDOW_BG,
                               selectcolor=WindowsClassicColors.INPUT_BG,
                               command=self.generate_password)
            cb.pack(anchor='w', pady=ClassicSpacing.XS)
    
    def _create_password_section(self, parent):
        password_frame = create_classic_label_frame(parent, "🔐 Generiertes Passwort")
        password_frame.pack(fill='x', pady=(0, ClassicSpacing.GROUP_SPACING))
        
        pw_container = create_classic_frame(password_frame, WindowsClassicColors.WINDOW_BG)
        pw_container.pack(fill='x', padx=ClassicSpacing.DIALOG_PADDING, pady=ClassicSpacing.DIALOG_PADDING)
        
        pw_display_frame = create_classic_frame(pw_container, WindowsClassicColors.WINDOW_BG)
        pw_display_frame.pack(fill='x', pady=(0, ClassicSpacing.SM))
        
        self.password_display = create_classic_entry(pw_display_frame)
        self.password_display.configure(font=('Courier New', 11, 'normal'), 
                                       fg=WindowsClassicColors.ACCENT, state='readonly')
        self.password_display.pack(side='left', fill='x', expand=True)
        self.password_display.bind('<KeyRelease>', self._on_password_change)
        
        copy_btn = tk.Button(pw_display_frame, text="📋", width=3, 
                            command=self.copy_to_clipboard,
                            bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                            relief='raised', bd=1, padx=6, pady=2)
        copy_btn.pack(side='right', padx=(ClassicSpacing.XS, 0))
        
        def create_hover_effect(button):
            def on_enter(event):
                button.config(bg='#d5d5d5')
            def on_leave(event):
                button.config(bg='#e1e1e1')
            button.bind('<Enter>', on_enter)
            button.bind('<Leave>', on_leave)
        
        create_hover_effect(copy_btn)
    
    def _create_actions_section(self, parent):
        action_frame = create_classic_label_frame(parent, "🎯 Aktionen")
        action_frame.pack(fill='x', pady=(0, ClassicSpacing.GROUP_SPACING))
        
        button_container = create_classic_frame(action_frame, WindowsClassicColors.WINDOW_BG)
        button_container.pack(fill='x', padx=ClassicSpacing.DIALOG_PADDING, pady=ClassicSpacing.DIALOG_PADDING)
        
        left_buttons = create_classic_frame(button_container, WindowsClassicColors.WINDOW_BG)
        left_buttons.pack(side='left')
        
        generate_btn = tk.Button(left_buttons, text="🎲 Neues Passwort", 
                                command=self.generate_password,
                                bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                                relief='raised', bd=1, padx=12, pady=4)
        generate_btn.pack(side='left', padx=(0, ClassicSpacing.BUTTON_SPACING))
        
        use_btn = tk.Button(left_buttons, text="✅ Verwenden", 
                           command=self.use_password,
                           bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'bold'),
                           relief='raised', bd=1, padx=12, pady=4)
        use_btn.pack(side='left')
        
        right_buttons = create_classic_frame(button_container, WindowsClassicColors.WINDOW_BG)
        right_buttons.pack(side='right')
        
        cancel_btn = tk.Button(right_buttons, text="❌ Abbrechen", 
                              command=self.cancel,
                              bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                              relief='raised', bd=1, padx=12, pady=4)
        cancel_btn.pack(side='right')
        
        def create_hover_effect(button):
            def on_enter(event):
                button.config(bg='#d5d5d5')
            def on_leave(event):
                button.config(bg='#e1e1e1')
            button.bind('<Enter>', on_enter)
            button.bind('<Leave>', on_leave)
        
        for btn in [generate_btn, use_btn, cancel_btn]:
            create_hover_effect(btn)
    
    def _create_history_section(self, parent):
        history_frame = create_classic_label_frame(parent, "📜 Letzte Passwörter")
        history_frame.pack(fill='both', expand=True)
        
        history_container = create_classic_frame(history_frame, WindowsClassicColors.WINDOW_BG)
        history_container.pack(fill='both', expand=True, padx=ClassicSpacing.DIALOG_PADDING, pady=ClassicSpacing.DIALOG_PADDING)
        
        listbox_frame = create_classic_frame(history_container, WindowsClassicColors.INPUT_BG, relief='sunken')
        listbox_frame.pack(fill='both', expand=True)
        
        self.history_listbox = tk.Listbox(listbox_frame, 
                                         bg=WindowsClassicColors.INPUT_BG, 
                                         fg=WindowsClassicColors.TEXT_PRIMARY, 
                                         font=('Courier New', 9, 'normal'), 
                                         height=6,
                                         relief='flat', bd=0,
                                         selectbackground=WindowsClassicColors.ACCENT,
                                         selectforeground='#ffffff')
        self.history_listbox.pack(side='left', fill='both', expand=True)
        
        history_scrollbar = tk.Scrollbar(listbox_frame, orient='vertical', 
                                        command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=history_scrollbar.set)
        history_scrollbar.pack(side='right', fill='y')
        
        self.history_listbox.bind('<Double-Button-1>', self.select_from_history)
        
        info_frame = create_classic_frame(parent, WindowsClassicColors.DIALOG_BG)
        info_frame.pack(fill='x', pady=(ClassicSpacing.SM, 0))
        
        info_text = "💡 Tipp: Doppelklick auf ein Passwort aus der Historie zum Auswählen"
        info_label = tk.Label(info_frame, text=info_text, 
                             bg=WindowsClassicColors.DIALOG_BG, fg=WindowsClassicColors.ACCENT, 
                             font=('Segoe UI', 8, 'italic'))
        info_label.pack()
    
    def _create_strength_visualization(self, parent):
        viz_frame = create_classic_label_frame(parent, "📊 Passwort-Stärke")
        viz_frame.pack(fill='both', expand=True)
        
        viz_container = create_classic_frame(viz_frame, WindowsClassicColors.WINDOW_BG)
        viz_container.pack(fill='both', expand=True, padx=ClassicSpacing.DIALOG_PADDING, pady=ClassicSpacing.DIALOG_PADDING)
        
        self.strength_visualizer = PasswordStrengthVisualizer(viz_container, self.password_generator)
        strength_widget = self.strength_visualizer.create_visualizer(viz_container)
        strength_widget.pack(fill='both', expand=True)
    
    def generate_password(self):
        password = self.password_generator.generate_secure_password(
            length=self.length_var.get(),
            use_uppercase=self.use_uppercase.get(),
            use_lowercase=self.use_lowercase.get(),
            use_numbers=self.use_numbers.get(),
            use_symbols=self.use_symbols.get(),
            exclude_ambiguous=self.exclude_ambiguous.get()
        )
        
        self.password_display.config(state='normal')
        self.password_display.delete(0, tk.END)
        self.password_display.insert(0, password)
        self.password_display.config(state='readonly')
        
        if self.strength_visualizer:
            self.strength_visualizer.update_strength(password)
        
        if password not in self.password_history:
            self.password_history.insert(0, password)
            if len(self.password_history) > 10:
                self.password_history.pop()
            
            self.history_listbox.delete(0, tk.END)
            for pw in self.password_history:
                display_pw = pw[:25] + "..." if len(pw) > 25 else pw
                strength_text, _ = self.password_generator.calculate_password_strength(pw)
                self.history_listbox.insert(tk.END, f"{display_pw} ({strength_text})")
    
    def _on_password_change(self, event):
        password = self.password_display.get()
        if self.strength_visualizer:
            self.strength_visualizer.update_strength(password)
    
    def copy_to_clipboard(self):
        password = self.password_display.get()
        if password:
            pyperclip.copy(password)
            messagebox.showinfo("Kopiert", "Passwort in Zwischenablage kopiert!")
    
    def select_from_history(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            password = self.password_history[selection[0]]
            self.password_display.config(state='normal')
            self.password_display.delete(0, tk.END)
            self.password_display.insert(0, password)
            self.password_display.config(state='readonly')
            
            if self.strength_visualizer:
                self.strength_visualizer.update_strength(password)
    
    def use_password(self):
        password = self.password_display.get()
        if password:
            self.result = password
            self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()