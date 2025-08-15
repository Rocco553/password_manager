import tkinter as tk
from tkinter import ttk, messagebox
from gui.modern_styles import (
    WindowsClassicStyles, WindowsClassicColors, create_classic_entry,
    create_classic_frame, ClassicSpacing
)


class LoginWindow:
    def __init__(self, root, password_manager, on_login_success, database_path=None):
        self.root = root
        self.pm = password_manager
        self.on_login_success = on_login_success
        self.database_path = database_path
        self.master_pw_entry = None
        self.login_btn = None
        self.password_visible = False

        if database_path:
            self.pm.database_file = database_path

        WindowsClassicStyles.setup_windows_classic_theme()
        self.setup_login_screen()

    def setup_login_screen(self):
        self.clear_screen()
        self.root.configure(bg=WindowsClassicColors.WINDOW_BG)
        self.root.geometry("500x400")
        self.root.minsize(500, 400)

        main_frame = create_classic_frame(self.root)
        main_frame.pack(expand=True, fill='both')
        
        header_frame = create_classic_frame(main_frame, "#6ba644")
        header_frame.pack(fill='x')
        
        header_content = create_classic_frame(header_frame, "#6ba644")
        header_content.pack(expand=True, fill='x', padx=40, pady=30)
        
        icon_frame = create_classic_frame(header_content, "#5a9137")
        icon_frame.configure(width=60, height=60)
        icon_frame.pack_propagate(False)
        icon_frame.pack(pady=(0, 15))
        
        icon_label = tk.Label(icon_frame, text="🔐", 
                            bg="#5a9137", fg="white", 
                            font=('Segoe UI', 24, 'normal'))
        icon_label.place(relx=0.5, rely=0.5, anchor='center')

        display_path = self.database_path or self.pm.database_file
        
        if display_path:
            from pathlib import Path
            db_name = Path(display_path).stem
            title_text = f"{db_name}"
            subtitle_text = f"Datenbank: {db_name}.enc"
        else:
            title_text = "🔐 Passwort-Manager"
            subtitle_text = ""

        title_label = tk.Label(header_content, text=title_text,
                               font=('Segoe UI', 18, 'normal'),
                               bg="#6ba644", fg="white")
        title_label.pack()

        if subtitle_text:
            subtitle_label = tk.Label(header_content, text=subtitle_text,
                                      bg="#6ba644", fg="white",
                                      font=('Segoe UI', 10, 'normal'))
            subtitle_label.pack(pady=(5, 0))
        
        content_frame = create_classic_frame(main_frame)
        content_frame.pack(expand=True, fill='both', padx=40, pady=40)

        form_frame = create_classic_frame(content_frame)
        form_frame.pack(expand=True)
        
        pw_label = tk.Label(form_frame, text="Master-Passwort:",
                            bg=WindowsClassicColors.WINDOW_BG,
                            fg=WindowsClassicColors.TEXT_PRIMARY,
                            font=('Segoe UI', 11, 'bold'))
        pw_label.pack(anchor='w', pady=(0, 8))
        
        input_frame = create_classic_frame(form_frame)
        input_frame.pack(fill='x', pady=(0, 8))

        entry_container = create_classic_frame(input_frame)
        entry_container.pack(fill='x')

        self.master_pw_entry = tk.Entry(entry_container, show='*', 
                                       font=('Segoe UI', 12, 'normal'),
                                       bg=WindowsClassicColors.INPUT_BG,
                                       fg=WindowsClassicColors.TEXT_PRIMARY,
                                       relief='solid', bd=2)
        self.master_pw_entry.pack(side='left', fill='x', expand=True)
        self.master_pw_entry.bind('<Return>', lambda e: self.login())
        self.master_pw_entry.bind('<KeyRelease>', self.on_key_release)
        
        toggle_container = create_classic_frame(entry_container, WindowsClassicColors.INPUT_BG)
        toggle_container.configure(width=32, height=32, relief='solid', bd=2)
        toggle_container.pack_propagate(False)
        toggle_container.pack(side='right', padx=(2, 0))
        
        toggle_inner = create_classic_frame(toggle_container, WindowsClassicColors.INPUT_BG)
        toggle_inner.configure(relief='solid', bd=1)
        toggle_inner.pack(fill='both', expand=True, padx=1, pady=1)
        
        self.toggle_btn = tk.Button(toggle_inner, text="👁",
                                   command=self.toggle_password_visibility,
                                   bg=WindowsClassicColors.INPUT_BG, fg=WindowsClassicColors.TEXT_PRIMARY, 
                                   font=('Segoe UI', 11, 'normal'),
                                   relief='flat', bd=0, cursor='hand2')
        self.toggle_btn.pack(fill='both', expand=True)
        
        def toggle_hover(event):
            self.toggle_btn.config(bg='#f0f0f0')
        def toggle_leave(event):
            self.toggle_btn.config(bg=WindowsClassicColors.INPUT_BG)
        self.toggle_btn.bind('<Enter>', toggle_hover)
        self.toggle_btn.bind('<Leave>', toggle_leave)

        button_frame = create_classic_frame(form_frame)
        button_frame.pack(pady=(20, 0))

        self.back_btn = tk.Button(button_frame, text="⬅️ Zurück", 
                                 command=self.go_back,
                                 bg='#e1e1e1', fg='#000000', 
                                 font=('Segoe UI', 10, 'normal'),
                                 relief='raised', bd=1, padx=15, pady=8)
        self.back_btn.pack(side='left', padx=(0, 15))

        self.login_btn = tk.Button(button_frame, text="🔓 Anmelden",
                                  command=self.login,
                                  bg="#6ba644", fg="white",
                                  font=('Segoe UI', 10, 'bold'),
                                  relief='flat', bd=0, padx=20, pady=8,
                                  state='disabled')
        self.login_btn.pack(side='left')
        
        def back_hover(event):
            self.back_btn.config(bg='#d5d5d5')
        def back_leave(event):
            self.back_btn.config(bg='#e1e1e1')
        self.back_btn.bind('<Enter>', back_hover)
        self.back_btn.bind('<Leave>', back_leave)
        
        def login_hover(event):
            if self.login_btn['state'] != 'disabled':
                self.login_btn.config(bg='#5a9137')
        def login_leave(event):
            if self.login_btn['state'] != 'disabled':
                self.login_btn.config(bg='#6ba644')
        self.login_btn.bind('<Enter>', login_hover)
        self.login_btn.bind('<Leave>', login_leave)

        info_frame = create_classic_frame(content_frame)
        info_frame.pack(side='bottom', pady=(20, 0))
        
        info_label = tk.Label(info_frame, text="Gib das Master-Passwort für diese Datenbank ein",
                              bg=WindowsClassicColors.WINDOW_BG,
                              fg=WindowsClassicColors.TEXT_SECONDARY,
                              font=('Segoe UI', 9, 'italic'))
        info_label.pack()

        self.master_pw_entry.focus()
    
    def toggle_password_visibility(self):
        if self.password_visible:
            self.master_pw_entry.config(show='*')
            self.toggle_btn.config(text="👁")
            self.password_visible = False
        else:
            self.master_pw_entry.config(show='')
            self.toggle_btn.config(text="🙈")
            self.password_visible = True

    def on_key_release(self, event=None):
        pw = self.master_pw_entry.get()
        if pw.strip():
            self.login_btn.configure(state='normal', bg="#6ba644")
        else:
            self.login_btn.configure(state='disabled', bg="#cccccc")

    def login(self):
        master_password = self.master_pw_entry.get()

        if not master_password:
            messagebox.showerror("Fehler", "Bitte Master-Passwort eingeben!")
            return

        if self.pm.unlock_database(master_password):
            self.on_login_success()
        else:
            messagebox.showerror("Fehler", "Falsches Master-Passwort oder keine Datenbank gefunden!")
            self.master_pw_entry.delete(0, tk.END)
            self.login_btn.configure(state='disabled', bg="#cccccc")

    def go_back(self):
        from gui.database_selector import DatabaseSelector
        DatabaseSelector(self.root, self.on_database_selected_callback)

    def on_database_selected_callback(self, database_path):
        LoginWindow(self.root, self.pm, self.on_login_success, database_path)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()