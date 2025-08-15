import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
from PIL import Image, ImageTk
from gui.modern_styles import (
    WindowsClassicStyles, WindowsClassicColors, create_classic_frame,
    create_classic_label_frame, ClassicSpacing
)


class TOTPDialog:
    def __init__(self, parent, password_manager, totp_manager):
        self.pm = password_manager
        self.totp_manager = totp_manager
        self.totp_entries = []
        self.update_timer = None
        self.selected_index = -1
        
        WindowsClassicStyles.setup_windows_classic_theme()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🔐 2FA/TOTP Manager")
        self.dialog.geometry("800x600")
        self.dialog.configure(bg=WindowsClassicColors.WINDOW_BG)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 25))

        self.dialog.focus_set()
        self.dialog.focus_force()
        
        self.create_totp_ui()
        self.load_totp_entries()
        self.start_update_timer()
        
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.dialog.bind('<Escape>', lambda e: self.on_closing())
        
        self.dialog.wait_window()
    
    def create_totp_ui(self):
        main_frame = create_classic_frame(self.dialog, WindowsClassicColors.DIALOG_BG)
        main_frame.pack(expand=True, fill='both', padx=12, pady=12)
        
        title_frame = create_classic_frame(main_frame, WindowsClassicColors.DIALOG_BG)
        title_frame.pack(fill='x', pady=(0, 16))
        
        icon_label = tk.Label(title_frame, text="🔐", 
                             bg=WindowsClassicColors.DIALOG_BG, 
                             fg=WindowsClassicColors.ACCENT,
                             font=('Segoe UI', 16, 'normal'))
        icon_label.pack(side='left', padx=(0, 8))
        
        title_label = tk.Label(title_frame, text="2FA/TOTP Manager", 
                              bg=WindowsClassicColors.DIALOG_BG, 
                              fg=WindowsClassicColors.TEXT_PRIMARY,
                              font=('Segoe UI', 14, 'bold'))
        title_label.pack(side='left')
        
        subtitle_label = tk.Label(title_frame, text="Verwalte alle deine 2FA-Codes an einem Ort", 
                                 bg=WindowsClassicColors.DIALOG_BG, 
                                 fg=WindowsClassicColors.TEXT_SECONDARY,
                                 font=('Segoe UI', 9, 'italic'))
        subtitle_label.pack(side='left', padx=(16, 0))
        
        list_frame = create_classic_label_frame(main_frame, "🔑 Aktive 2FA-Codes")
        list_frame.pack(expand=True, fill='both', pady=(0, 16))
        
        tree_container = create_classic_frame(list_frame, WindowsClassicColors.WINDOW_BG, relief='sunken')
        tree_container.pack(expand=True, fill='both', padx=8, pady=8)
        
        self.totp_tree = ttk.Treeview(tree_container, 
                                     columns=('username', 'current_code', 'remaining'), 
                                     show='tree headings', 
                                     height=12,
                                     style='Classic.Treeview')
        
        self.totp_tree.heading('#0', text='📝 Account', anchor='w')
        self.totp_tree.heading('username', text='👤 Benutzername', anchor='w')
        self.totp_tree.heading('current_code', text='🔐 Aktueller Code', anchor='center')
        self.totp_tree.heading('remaining', text='⏱️ Zeit', anchor='center')
        
        self.totp_tree.column('#0', width=200)
        self.totp_tree.column('username', width=150)
        self.totp_tree.column('current_code', width=120)
        self.totp_tree.column('remaining', width=80)
        
        totp_scrollbar = ttk.Scrollbar(tree_container, orient='vertical', 
                                      command=self.totp_tree.yview)
        self.totp_tree.configure(yscrollcommand=totp_scrollbar.set)
        
        self.totp_tree.pack(side='left', expand=True, fill='both')
        totp_scrollbar.pack(side='right', fill='y')
        
        self.totp_tree.bind('<Button-1>', self.on_tree_click)
        self.totp_tree.bind('<Double-Button-1>', self.copy_selected_code)
        
        actions_frame = create_classic_frame(main_frame, WindowsClassicColors.DIALOG_BG)
        actions_frame.pack(fill='x', pady=(0, 16))
        
        left_actions = create_classic_frame(actions_frame, WindowsClassicColors.DIALOG_BG)
        left_actions.pack(side='left')
        
        copy_btn = tk.Button(left_actions, text="📋 Code kopieren", 
                            command=self.copy_selected_code,
                            bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                            relief='raised', bd=1, padx=12, pady=4)
        copy_btn.pack(side='left', padx=(0, 8))
        
        show_qr_btn = tk.Button(left_actions, text="📱 QR-Code anzeigen", 
                               command=self.show_qr_code,
                               bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                               relief='raised', bd=1, padx=12, pady=4)
        show_qr_btn.pack(side='left', padx=8)
        
        backup_btn = tk.Button(left_actions, text="💾 Backup-Codes", 
                              command=self.generate_backup_codes,
                              bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                              relief='raised', bd=1, padx=12, pady=4)
        backup_btn.pack(side='left', padx=8)
        
        right_actions = create_classic_frame(actions_frame, WindowsClassicColors.DIALOG_BG)
        right_actions.pack(side='right')
        
        refresh_btn = tk.Button(right_actions, text="🔄 Aktualisieren", 
                               command=self.load_totp_entries,
                               bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                               relief='raised', bd=1, padx=12, pady=4)
        refresh_btn.pack(side='right', padx=(8, 0))
        
        close_btn = tk.Button(right_actions, text="Schließen", 
                             command=self.on_closing,
                             bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9, 'normal'),
                             relief='raised', bd=1, padx=20, pady=4, width=10)
        close_btn.pack(side='right')
        
        info_frame = create_classic_frame(main_frame, WindowsClassicColors.DIALOG_BG)
        info_frame.pack(fill='x')
        
        info_text = ("💡 Tipp: Klick auf einen Eintrag um ihn auszuwählen, dann 'Code kopieren'. "
                    "Codes aktualisieren sich automatisch alle 30 Sekunden.")
        info_label = tk.Label(info_frame, text=info_text,
                             bg=WindowsClassicColors.DIALOG_BG,
                             fg=WindowsClassicColors.TEXT_SECONDARY,
                             font=('Segoe UI', 8, 'italic'),
                             wraplength=750)
        info_label.pack()
        
        self._add_hover_effects([copy_btn, show_qr_btn, backup_btn, refresh_btn, close_btn])
    
    def on_tree_click(self, event):
        item = self.totp_tree.identify_row(event.y)
        if item:
            self.totp_tree.selection_set(item)
            self.selected_index = self.totp_tree.index(item)
    
    def load_totp_entries(self):
        old_selection = self.selected_index
        
        for item in self.totp_tree.get_children():
            self.totp_tree.delete(item)
        
        self.totp_entries = []
        all_entries = self.pm.list_entries()
        
        for entry in all_entries:
            if entry.has_totp():
                self.totp_entries.append(entry)
        
        if not self.totp_entries:
            self.totp_tree.insert('', 'end', text="Keine 2FA-Codes vorhanden",
                                 values=("", "Füge 2FA zu deinen Passwörtern hinzu", ""))
            return
        
        self.update_codes()
        
        if 0 <= old_selection < len(self.totp_entries):
            items = self.totp_tree.get_children()
            if old_selection < len(items):
                self.totp_tree.selection_set(items[old_selection])
                self.selected_index = old_selection
    
    def update_codes(self):
        if not self.totp_entries:
            return
        
        current_selection = self.totp_tree.selection()
        selected_item_id = current_selection[0] if current_selection else None
        
        for item in self.totp_tree.get_children():
            self.totp_tree.delete(item)
        
        for i, entry in enumerate(self.totp_entries):
            current_code, remaining_time = self.totp_manager.get_current_totp(entry.totp_secret)
            
            if current_code:
                formatted_code = f"{current_code[:3]} {current_code[3:]}"
                time_display = f"{remaining_time}s"
            else:
                formatted_code = "Fehler"
                time_display = "0s"
            
            item_id = self.totp_tree.insert('', 'end', text=entry.title,
                                           values=(entry.username, formatted_code, time_display))
            
            if i == self.selected_index:
                self.totp_tree.selection_set(item_id)
    
    def start_update_timer(self):
        self.update_codes()
        self.update_timer = self.dialog.after(1000, self.start_update_timer)
    
    def copy_selected_code(self, event=None):
        if self.selected_index < 0 or self.selected_index >= len(self.totp_entries):
            messagebox.showwarning("Warnung", "Bitte einen Eintrag auswählen!")
            return
        
        entry = self.totp_entries[self.selected_index]
        current_code, remaining_time = self.totp_manager.get_current_totp(entry.totp_secret)
        
        if current_code:
            pyperclip.copy(current_code)
            messagebox.showinfo("Code kopiert", 
                               f"2FA-Code für '{entry.title}' wurde kopiert!\n"
                               f"Code: {current_code}\n"
                               f"Gültig für weitere {remaining_time} Sekunden.")
        else:
            messagebox.showerror("Fehler", "Konnte 2FA-Code nicht generieren!")
    
    def show_qr_code(self):
        if self.selected_index < 0 or self.selected_index >= len(self.totp_entries):
            messagebox.showwarning("Warnung", "Bitte einen Eintrag auswählen!")
            return
        
        entry = self.totp_entries[self.selected_index]
        self._show_qr_dialog(entry)
    
    def _show_qr_dialog(self, entry):
        qr_dialog = tk.Toplevel(self.dialog)
        qr_dialog.title(f"QR-Code - {entry.title}")
        qr_dialog.geometry("300x400")
        qr_dialog.configure(bg=WindowsClassicColors.WINDOW_BG)
        qr_dialog.transient(self.dialog)
        qr_dialog.grab_set()
        qr_dialog.resizable(False, False)
        
        qr_dialog.geometry("+%d+%d" % (
            self.dialog.winfo_rootx() + 250, 
            self.dialog.winfo_rooty() + 100
        ))
        
        main_frame = create_classic_frame(qr_dialog)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        title_label = tk.Label(main_frame, text=f"📱 QR-Code für {entry.title}",
                              bg=WindowsClassicColors.WINDOW_BG,
                              fg=WindowsClassicColors.TEXT_PRIMARY,
                              font=('Segoe UI', 12, 'bold'))
        title_label.pack(pady=(0, 16))
        
        try:
            qr_img = self.totp_manager.generate_qr_code(entry.totp_secret, entry.title)
            qr_img = qr_img.resize((200, 200), Image.Resampling.LANCZOS)
            
            qr_photo = ImageTk.PhotoImage(qr_img)
            
            qr_label = tk.Label(main_frame, image=qr_photo,
                               bg=WindowsClassicColors.WINDOW_BG)
            qr_label.image = qr_photo
            qr_label.pack(pady=(0, 16))
            
        except Exception as e:
            error_label = tk.Label(main_frame, text=f"QR-Code Fehler:\n{str(e)}",
                                  bg=WindowsClassicColors.WINDOW_BG,
                                  fg=WindowsClassicColors.ERROR,
                                  font=('Segoe UI', 9))
            error_label.pack(pady=(0, 16))
        
        secret_frame = create_classic_frame(main_frame)
        secret_frame.pack(fill='x', pady=(0, 16))
        
        tk.Label(secret_frame, text="Secret Key (Backup):",
                bg=WindowsClassicColors.WINDOW_BG, fg=WindowsClassicColors.TEXT_PRIMARY,
                font=('Segoe UI', 9, 'bold')).pack()
        
        secret_text = tk.Text(secret_frame, height=2, width=35,
                             bg=WindowsClassicColors.INPUT_BG,
                             fg=WindowsClassicColors.TEXT_PRIMARY,
                             font=('Courier New', 8), wrap='char')
        secret_text.pack(pady=(4, 0))
        secret_text.insert('1.0', entry.totp_secret)
        secret_text.config(state='disabled')
        
        button_frame = create_classic_frame(main_frame)
        button_frame.pack()
        
        copy_secret_btn = tk.Button(button_frame, text="📋 Secret kopieren",
                                   command=lambda: self._copy_secret(entry.totp_secret),
                                   bg='#e1e1e1', fg='#000000', font=('Segoe UI', 8),
                                   relief='raised', bd=1, padx=8, pady=4)
        copy_secret_btn.pack(side='left', padx=(0, 8))
        
        close_qr_btn = tk.Button(button_frame, text="Schließen",
                                command=qr_dialog.destroy,
                                bg='#e1e1e1', fg='#000000', font=('Segoe UI', 8),
                                relief='raised', bd=1, padx=12, pady=4)
        close_qr_btn.pack(side='left')
        
        def create_hover_effect(button):
            def on_enter(event):
                button.config(bg='#d5d5d5')
            def on_leave(event):
                button.config(bg='#e1e1e1')
            button.bind('<Enter>', on_enter)
            button.bind('<Leave>', on_leave)
        
        create_hover_effect(copy_secret_btn)
        create_hover_effect(close_qr_btn)
        
        qr_dialog.bind('<Escape>', lambda e: qr_dialog.destroy())
    
    def _copy_secret(self, secret):
        pyperclip.copy(secret)
        messagebox.showinfo("Secret kopiert", "Secret Key wurde in die Zwischenablage kopiert!")
    
    def generate_backup_codes(self):
        backup_codes = self.totp_manager.generate_backup_codes()
        
        backup_dialog = tk.Toplevel(self.dialog)
        backup_dialog.title("💾 Backup-Codes")
        backup_dialog.geometry("400x500")
        backup_dialog.configure(bg=WindowsClassicColors.WINDOW_BG)
        backup_dialog.transient(self.dialog)
        backup_dialog.grab_set()
        backup_dialog.resizable(False, False)
        
        backup_dialog.geometry("+%d+%d" % (
            self.dialog.winfo_rootx() + 200, 
            self.dialog.winfo_rooty() + 50
        ))
        
        main_frame = create_classic_frame(backup_dialog)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        title_label = tk.Label(main_frame, text="💾 Backup Recovery Codes",
                              bg=WindowsClassicColors.WINDOW_BG,
                              fg=WindowsClassicColors.TEXT_PRIMARY,
                              font=('Segoe UI', 12, 'bold'))
        title_label.pack(pady=(0, 8))
        
        warning_label = tk.Label(main_frame, 
                                text="⚠️ Diese Codes können verwendet werden, wenn du keinen Zugang\n"
                                     "zu deiner 2FA-App hast. Bewahre sie sicher auf!",
                                bg=WindowsClassicColors.WINDOW_BG,
                                fg=WindowsClassicColors.WARNING,
                                font=('Segoe UI', 9),
                                justify='center')
        warning_label.pack(pady=(0, 16))
        
        codes_frame = create_classic_frame(backup_dialog, WindowsClassicColors.INPUT_BG, relief='sunken')
        codes_frame.pack(fill='both', expand=True, pady=(0, 16))
        
        codes_text = tk.Text(codes_frame, 
                            bg=WindowsClassicColors.INPUT_BG,
                            fg=WindowsClassicColors.TEXT_PRIMARY,
                            font=('Courier New', 10),
                            relief='flat', bd=0,
                            wrap='none')
        codes_text.pack(expand=True, fill='both', padx=8, pady=8)
        
        import datetime
        codes_content = "BACKUP RECOVERY CODES\n"
        codes_content += "=" * 25 + "\n\n"
        for i, code in enumerate(backup_codes, 1):
            codes_content += f"{i:2d}. {code}\n"
        
        codes_content += "\n" + "=" * 25 + "\n"
        codes_content += f"Generiert: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
        codes_content += "Bewahre diese Codes sicher auf!"
        
        codes_text.insert('1.0', codes_content)
        codes_text.config(state='disabled')
        
        button_frame = create_classic_frame(main_frame)
        button_frame.pack()
        
        copy_all_btn = tk.Button(button_frame, text="📋 Alle kopieren",
                                command=lambda: self._copy_backup_codes(codes_content),
                                bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9),
                                relief='raised', bd=1, padx=12, pady=4)
        copy_all_btn.pack(side='left', padx=(0, 8))
        
        save_btn = tk.Button(button_frame, text="💾 Speichern",
                            command=lambda: self._save_backup_codes(codes_content),
                            bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9),
                            relief='raised', bd=1, padx=12, pady=4)
        save_btn.pack(side='left', padx=8)
        
        close_backup_btn = tk.Button(button_frame, text="Schließen",
                                    command=backup_dialog.destroy,
                                    bg='#e1e1e1', fg='#000000', font=('Segoe UI', 9),
                                    relief='raised', bd=1, padx=12, pady=4)
        close_backup_btn.pack(side='left', padx=(8, 0))
        
        def create_hover_effect(button):
            def on_enter(event):
                button.config(bg='#d5d5d5')
            def on_leave(event):
                button.config(bg='#e1e1e1')
            button.bind('<Enter>', on_enter)
            button.bind('<Leave>', on_leave)
        
        for btn in [copy_all_btn, save_btn, close_backup_btn]:
            create_hover_effect(btn)
        
        backup_dialog.bind('<Escape>', lambda e: backup_dialog.destroy())
    
    def _copy_backup_codes(self, codes_content):
        pyperclip.copy(codes_content)
        messagebox.showinfo("Codes kopiert", "Alle Backup-Codes wurden in die Zwischenablage kopiert!")
    
    def _save_backup_codes(self, codes_content):
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            title="Backup-Codes speichern",
            defaultextension=".txt",
            filetypes=[("Text Dateien", "*.txt"), ("Alle Dateien", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(codes_content)
                messagebox.showinfo("Gespeichert", f"Backup-Codes wurden gespeichert:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Konnte Datei nicht speichern:\n{str(e)}")
    
    def _add_hover_effects(self, buttons):
        def create_hover_effect(button):
            def on_enter(event):
                button.config(bg='#d5d5d5')
            def on_leave(event):
                button.config(bg='#e1e1e1')
            button.bind('<Enter>', on_enter)
            button.bind('<Leave>', on_leave)
        
        for btn in buttons:
            create_hover_effect(btn)
    
    def on_closing(self):
        if self.update_timer:
            self.dialog.after_cancel(self.update_timer)
        self.dialog.destroy()