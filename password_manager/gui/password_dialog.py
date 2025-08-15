import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from gui.modern_styles import (
    WindowsClassicStyles, WindowsClassicColors, create_classic_frame,
    create_classic_entry, create_classic_text, ClassicSpacing
)
from core.totp_manager import TOTPManager

class PasswordDialog:
    def __init__(self, parent, title, entry=None, password_generator=None, category_manager=None):
        self.result = None
        self.password_generator = password_generator
        self.category_manager = category_manager
        self.password_visible = False
        self.totp_manager = TOTPManager()
        self.totp_secret = ""
        self.qr_image = None

        WindowsClassicStyles.setup_windows_classic_theme()

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x620")
        self.dialog.configure(bg=WindowsClassicColors.WINDOW_BG)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))

        self.create_form(entry)
        self.title_entry.focus()
        self.dialog.wait_window()

    def create_form(self, entry):
        main_frame = create_classic_frame(self.dialog)
        main_frame.pack(expand=True, fill='both', padx=ClassicSpacing.DIALOG_PADDING, pady=ClassicSpacing.DIALOG_PADDING)

        basic_info_frame = create_classic_frame(main_frame)
        basic_info_frame.pack(fill='x', pady=(0, ClassicSpacing.GROUP_SPACING))

        tk.Label(basic_info_frame, text="Titel:", bg=WindowsClassicColors.WINDOW_BG,
                 fg=WindowsClassicColors.TEXT_PRIMARY, font=('Segoe UI', 9)).pack(anchor='w')
        self.title_entry = create_classic_entry(basic_info_frame)
        self.title_entry.pack(pady=(0, ClassicSpacing.SM), fill='x')

        tk.Label(basic_info_frame, text="Benutzername:", bg=WindowsClassicColors.WINDOW_BG,
                 fg=WindowsClassicColors.TEXT_PRIMARY, font=('Segoe UI', 9)).pack(anchor='w')
        self.username_entry = create_classic_entry(basic_info_frame)
        self.username_entry.pack(pady=(0, ClassicSpacing.SM), fill='x')

        category_frame = create_classic_frame(basic_info_frame)
        category_frame.pack(fill='x', pady=(0, ClassicSpacing.SM))

        tk.Label(category_frame, text="Kategorie:", bg=WindowsClassicColors.WINDOW_BG,
                 fg=WindowsClassicColors.TEXT_PRIMARY, font=('Segoe UI', 9)).pack(side='left')

        self.category_var = tk.StringVar(value="Other")
        category_combo = ttk.Combobox(category_frame, textvariable=self.category_var,
                                     state='readonly', width=20,
                                     font=('Segoe UI', 9))
        
        if self.category_manager:
            categories = self.category_manager.get_categories_list()
            category_combo['values'] = categories
        else:
            category_combo['values'] = ["Banking", "Shopping", "Gaming", "Social", "Work", "Email", "Cloud", "Development", "Other"]
        
        category_combo.pack(side='right')

        tk.Label(basic_info_frame, text="Passwort:", bg=WindowsClassicColors.WINDOW_BG,
                 fg=WindowsClassicColors.TEXT_PRIMARY, font=('Segoe UI', 9)).pack(anchor='w')
        self.password_entry = create_classic_entry(basic_info_frame, show='*')
        self.password_entry.pack(fill='x')

        action_frame = create_classic_frame(basic_info_frame)
        action_frame.pack(fill='x', pady=(ClassicSpacing.XS, ClassicSpacing.SM))

        self.toggle_btn = ttk.Button(action_frame, text="Passwort anzeigen", command=self.toggle_password_visibility, style="Classic.TButton")
        self.toggle_btn.pack(side='left', padx=(0, ClassicSpacing.BUTTON_SPACING))

        self.generate_btn = ttk.Button(action_frame, text="Passwort generieren", command=self.generate_password_for_entry, style="Classic.TButton")
        self.generate_btn.pack(side='left')

        tk.Label(basic_info_frame, text="URL:", bg=WindowsClassicColors.WINDOW_BG,
                 fg=WindowsClassicColors.TEXT_PRIMARY, font=('Segoe UI', 9)).pack(anchor='w')
        self.url_entry = create_classic_entry(basic_info_frame)
        self.url_entry.pack(pady=(0, ClassicSpacing.SM), fill='x')

        self.totp_frame = create_classic_frame(main_frame, WindowsClassicColors.WINDOW_BG, relief='groove')
        self.totp_frame.pack(fill='x', pady=(0, ClassicSpacing.SM))

        totp_header = create_classic_frame(self.totp_frame)
        totp_header.pack(fill='x', padx=8, pady=8)

        self.totp_enabled = tk.BooleanVar()
        self.totp_checkbox = tk.Checkbutton(totp_header, text="🔐 2FA/TOTP aktivieren",
                                           variable=self.totp_enabled,
                                           command=self.toggle_totp,
                                           bg=WindowsClassicColors.WINDOW_BG,
                                           fg=WindowsClassicColors.TEXT_PRIMARY,
                                           font=('Segoe UI', 9, 'bold'),
                                           activebackground=WindowsClassicColors.WINDOW_BG,
                                           selectcolor=WindowsClassicColors.INPUT_BG)
        self.totp_checkbox.pack(side='left')

        self.totp_content = create_classic_frame(self.totp_frame)
        
        totp_info_frame = create_classic_frame(self.totp_content)
        totp_info_frame.pack(fill='x', padx=8, pady=4)

        left_frame = create_classic_frame(totp_info_frame)
        left_frame.pack(side='left', fill='both', expand=True)

        tk.Label(left_frame, text="Secret Key:",
                bg=WindowsClassicColors.WINDOW_BG, fg=WindowsClassicColors.TEXT_PRIMARY,
                font=('Segoe UI', 9, 'normal')).pack(anchor='w')
        
        self.secret_entry = create_classic_entry(left_frame, width=40)
        self.secret_entry.pack(fill='x', pady=(2, 8))

        secret_buttons = create_classic_frame(left_frame)
        secret_buttons.pack(fill='x')

        generate_secret_btn = tk.Button(secret_buttons, text="🎲 Generieren",
                                       command=self.generate_new_secret,
                                       bg='#e1e1e1', fg='#000000', font=('Segoe UI', 8),
                                       relief='raised', bd=1, padx=8, pady=2)
        generate_secret_btn.pack(side='left', padx=(0, 4))

        show_qr_btn = tk.Button(secret_buttons, text="📱 QR-Code",
                               command=self.show_qr_code,
                               bg='#e1e1e1', fg='#000000', font=('Segoe UI', 8),
                               relief='raised', bd=1, padx=8, pady=2)
        show_qr_btn.pack(side='left')

        self.qr_frame = create_classic_frame(totp_info_frame)
        self.qr_frame.pack(side='right', padx=(8, 0))

        self.qr_label = tk.Label(self.qr_frame, text="QR-Code wird hier angezeigt",
                                bg=WindowsClassicColors.WINDOW_BG,
                                fg=WindowsClassicColors.TEXT_SECONDARY,
                                font=('Segoe UI', 8))
        self.qr_label.pack()

        def create_hover_effect(button):
            def on_enter(event):
                button.config(bg='#d5d5d5')
            def on_leave(event):
                button.config(bg='#e1e1e1')
            button.bind('<Enter>', on_enter)
            button.bind('<Leave>', on_leave)

        create_hover_effect(generate_secret_btn)
        create_hover_effect(show_qr_btn)

        tk.Label(main_frame, text="Notizen:", bg=WindowsClassicColors.WINDOW_BG,
                 fg=WindowsClassicColors.TEXT_PRIMARY, font=('Segoe UI', 9)).pack(anchor='w')
        self.notes_entry = create_classic_text(main_frame, height=3)
        self.notes_entry.pack(pady=(0, ClassicSpacing.MD), fill='x')

        button_frame = create_classic_frame(main_frame)
        button_frame.pack(fill='x', pady=(ClassicSpacing.SM, 0))

        cancel_btn = ttk.Button(button_frame, text="❌ Abbrechen", command=self.cancel, style='Classic.TButton')
        cancel_btn.pack(side='left')

        save_btn = ttk.Button(button_frame, text="💾 Speichern", command=self.save, style='Classic.TButton')
        save_btn.pack(side='right')

        if entry:
            self.title_entry.insert(0, entry.title)
            self.username_entry.insert(0, entry.username)
            self.password_entry.insert(0, entry.password)
            self.url_entry.insert(0, entry.url)
            self.notes_entry.insert('1.0', entry.notes)
            self.category_var.set(entry.category or "Other")
            if entry.has_totp():
                self.totp_secret = entry.totp_secret
                self.secret_entry.insert(0, self.totp_secret)
                self.totp_enabled.set(True)
                self.toggle_totp()

        self.dialog.bind('<Return>', lambda e: self.save())
        self.dialog.bind('<Escape>', lambda e: self.cancel())

    def toggle_totp(self):
        if self.totp_enabled.get():
            self.totp_content.pack(fill='x', padx=8, pady=(0, 8))
            if not self.totp_secret:
                self.generate_new_secret()
        else:
            self.totp_content.pack_forget()
            self.totp_secret = ""
            self.secret_entry.delete(0, tk.END)

    def generate_new_secret(self):
        self.totp_secret = self.totp_manager.generate_secret()
        self.secret_entry.delete(0, tk.END)
        self.secret_entry.insert(0, self.totp_secret)
        self.show_qr_code()

    def show_qr_code(self):
        if not self.totp_secret:
            return

        account_name = self.title_entry.get() or "Account"
        try:
            qr_img = self.totp_manager.generate_qr_code(self.totp_secret, account_name)
            qr_img = qr_img.resize((120, 120), Image.Resampling.LANCZOS)
            
            self.qr_image = ImageTk.PhotoImage(qr_img)
            self.qr_label.configure(image=self.qr_image, text="")
        except Exception as e:
            self.qr_label.configure(text=f"QR-Fehler: {str(e)[:20]}", image="")

    def toggle_password_visibility(self):
        if self.password_visible:
            self.password_entry.config(show='*')
            self.toggle_btn.config(text="Passwort anzeigen")
        else:
            self.password_entry.config(show='')
            self.toggle_btn.config(text="Passwort verbergen")
        self.password_visible = not self.password_visible

    def generate_password_for_entry(self):
        if self.password_generator:
            password = self.password_generator.generate_secure_password(length=16)
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, password)
        else:
            messagebox.showinfo("Info", "Passwort-Generator nicht verfügbar")

    def save(self):
        title = self.title_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        url = self.url_entry.get().strip()
        notes = self.notes_entry.get('1.0', tk.END).strip()
        category = self.category_var.get()
        totp_secret = self.secret_entry.get().strip() if self.totp_enabled.get() else ""

        if not title:
            messagebox.showerror("Fehler", "Titel ist erforderlich!")
            return
        if not password:
            messagebox.showerror("Fehler", "Passwort ist erforderlich!")
            return

        self.result = {
            'title': title,
            'username': username,
            'password': password,
            'url': url,
            'notes': notes,
            'category': category,
            'totp_secret': totp_secret
        }
        self.dialog.destroy()

    def cancel(self):
        self.dialog.destroy()