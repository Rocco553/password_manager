import tkinter as tk
import threading
import time
from gui.modern_styles import (
    WindowsClassicStyles, WindowsClassicColors, create_classic_frame, ClassicSpacing
)


class AutoLockTimer:
    def __init__(self, main_window, timeout_minutes=0.75, warning_seconds=15):
        self.main_window = main_window
        self.timeout_seconds = timeout_minutes * 60
        self.warning_seconds = warning_seconds
        self.last_activity = time.time()
        self.timer_thread = None
        self.is_running = False
        self.warning_dialog = None
        self.countdown_active = False
        self.active_dialogs = set()
        self.dialog_pause_active = False
        self.activity_callbacks = []
        
    def start(self):
        if not self.is_running:
            self.is_running = True
            self.reset_activity()
            self._setup_global_activity_tracking()
            self._start_timer_thread()
    
    def stop(self):
        self.is_running = False
        if self.warning_dialog:
            try:
                self.warning_dialog.destroy()
            except:
                pass
        self.warning_dialog = None
        self.countdown_active = False
        self.active_dialogs.clear()
        self.dialog_pause_active = False
    
    def reset_activity(self):
        self.last_activity = time.time()
        if self.warning_dialog and not self.countdown_active:
            try:
                self.warning_dialog.destroy()
                self.warning_dialog = None
            except:
                pass
    
    def register_dialog(self, dialog_window):
        try:
            if not dialog_window or not dialog_window.winfo_exists():
                return
                
            dialog_id = id(dialog_window)
            self.active_dialogs.add(dialog_id)
            self.dialog_pause_active = True
            
            self._setup_dialog_activity_tracking(dialog_window)
            
            def enhanced_destroy():
                try:
                    self.unregister_dialog(dialog_window)
                    dialog_window.destroy()
                except:
                    pass
            
            def on_close_handler():
                try:
                    self.unregister_dialog(dialog_window)
                except:
                    pass
            
            try:
                dialog_window.protocol("WM_DELETE_WINDOW", on_close_handler)
            except:
                pass
                
        except Exception as e:
            pass
    
    def unregister_dialog(self, dialog_window):
        try:
            dialog_id = id(dialog_window)
            self.active_dialogs.discard(dialog_id)
            
            if not self.active_dialogs:
                self.dialog_pause_active = False
                self.reset_activity()
        except:
            pass
    
    def has_active_dialogs(self):
        self._cleanup_invalid_dialogs()
        return len(self.active_dialogs) > 0
    
    def _cleanup_invalid_dialogs(self):
        try:
            valid_dialogs = set()
            for dialog_id in self.active_dialogs.copy():
                try:
                    for child in self.main_window.root.winfo_children():
                        if isinstance(child, tk.Toplevel) and id(child) == dialog_id:
                            if child.winfo_exists():
                                valid_dialogs.add(dialog_id)
                            break
                except:
                    pass
            
            self.active_dialogs = valid_dialogs
            
            if not self.active_dialogs:
                self.dialog_pause_active = False
        except:
            self.active_dialogs.clear()
            self.dialog_pause_active = False
    
    def _setup_global_activity_tracking(self):
        def on_activity(event=None):
            if self.is_running:
                self.reset_activity()
        
        events = ['<Motion>', '<Button>', '<Key>', '<MouseWheel>']
        for event in events:
            try:
                self.main_window.root.bind_all(event, on_activity, add='+')
            except:
                pass
        
        self.activity_callback = on_activity
    
    def _setup_dialog_activity_tracking(self, dialog_window):
        def on_dialog_activity(event=None):
            if self.is_running:
                self.reset_activity()
        
        events = ['<Motion>', '<Button>', '<Key>', '<MouseWheel>', '<FocusIn>']
        for event in events:
            try:
                dialog_window.bind(event, on_dialog_activity, add='+')
            except:
                pass
        
        def bind_to_children(widget):
            try:
                if not widget.winfo_exists():
                    return
                for event in events:
                    widget.bind(event, on_dialog_activity, add='+')
                for child in widget.winfo_children():
                    bind_to_children(child)
            except:
                pass
        
        try:
            dialog_window.after(200, lambda: bind_to_children(dialog_window))
        except:
            pass
    
    def _start_timer_thread(self):
        if self.timer_thread and self.timer_thread.is_alive():
            return
        
        self.timer_thread = threading.Thread(target=self._enhanced_timer_loop, daemon=True)
        self.timer_thread.start()
    
    def _enhanced_timer_loop(self):
        while self.is_running:
            time.sleep(1)
            
            if not self.is_running:
                break
            
            if self.has_active_dialogs():
                self.last_activity = time.time()
                continue
            
            elapsed = time.time() - self.last_activity
            remaining = self.timeout_seconds - elapsed
            
            if remaining <= self.warning_seconds and remaining > 0 and not self.warning_dialog:
                try:
                    self.main_window.root.after(0, self._show_warning, int(remaining))
                except:
                    pass
            
            elif remaining <= 0:
                try:
                    self.main_window.root.after(0, self._trigger_auto_lock)
                except:
                    pass
                break
    
    def _show_warning(self, remaining_seconds):
        if self.has_active_dialogs():
            return
        
        if self.warning_dialog or not self.is_running:
            return
        
        try:
            self.countdown_active = True
            self.warning_dialog = AutoLockWarningDialog(
                self.main_window.root, 
                remaining_seconds,
                self._on_warning_stay_logged_in,
                self._trigger_auto_lock,
                self
            )
        except Exception as e:
            self.countdown_active = False
    
    def _on_warning_stay_logged_in(self):
        self.reset_activity()
        self.countdown_active = False
        if self.warning_dialog:
            try:
                self.warning_dialog.destroy()
            except:
                pass
        self.warning_dialog = None
        self._start_timer_thread()
    
    def _trigger_auto_lock(self):
        if not self.is_running:
            return
        
        self.stop()
        
        if self.warning_dialog:
            try:
                self.warning_dialog.destroy()
            except:
                pass
        self.warning_dialog = None
        
        try:
            self.main_window._handle_auto_lock()
        except:
            pass


class AutoLockWarningDialog:
    def __init__(self, parent, countdown_seconds, on_stay_callback, on_lock_callback, auto_lock_timer):
        self.on_stay_callback = on_stay_callback
        self.on_lock_callback = on_lock_callback
        self.countdown = countdown_seconds
        self.is_active = True
        self.auto_lock_timer = auto_lock_timer
        
        try:
            WindowsClassicStyles.setup_windows_classic_theme()
            
            self.dialog = tk.Toplevel(parent)
            self.dialog.title("⚠️ Auto-Lock Warnung")
            self.dialog.geometry("500x280")
            self.dialog.configure(bg=WindowsClassicColors.WINDOW_BG)
            self.dialog.transient(parent)
            self.dialog.grab_set()
            self.dialog.resizable(False, False)
            
            self.dialog.geometry("+%d+%d" % (
                parent.winfo_rootx() + 200, 
                parent.winfo_rooty() + 200
            ))
            
            self.dialog.protocol("WM_DELETE_WINDOW", self._on_lock)
            
            self.auto_lock_timer.register_dialog(self.dialog)
            
            self._create_warning_ui()
            self._start_countdown()
            
        except Exception as e:
            self.is_active = False
            if hasattr(self, 'dialog'):
                try:
                    self.dialog.destroy()
                except:
                    pass
    
    def _create_warning_ui(self):
        try:
            main_frame = create_classic_frame(self.dialog)
            main_frame.pack(expand=True, fill='both', padx=20, pady=20)
            
            title_frame = create_classic_frame(main_frame)
            title_frame.pack(fill='x', pady=(0, 15))
            
            icon_label = tk.Label(title_frame, text="⚠️", 
                                 bg=WindowsClassicColors.WINDOW_BG, 
                                 fg=WindowsClassicColors.WARNING,
                                 font=('Segoe UI', 24, 'normal'))
            icon_label.pack(side='left', padx=(0, 10))
            
            title_label = tk.Label(title_frame, text="Automatische Sperre", 
                                  bg=WindowsClassicColors.WINDOW_BG, 
                                  fg=WindowsClassicColors.WARNING,
                                  font=('Segoe UI', 14, 'bold'))
            title_label.pack(side='left', anchor='w')
            
            warning_text = ("Die Datenbank wird aus Sicherheitsgründen automatisch gesperrt,\n"
                           "da keine Aktivität erkannt wurde.\n\n"
                           "💡 Tipp: In geöffneten Dialogen wird der Timer automatisch pausiert.")
            
            warning_label = tk.Label(main_frame, text=warning_text,
                                    bg=WindowsClassicColors.WINDOW_BG,
                                    fg=WindowsClassicColors.TEXT_PRIMARY,
                                    font=('Segoe UI', 9, 'normal'),
                                    justify='left')
            warning_label.pack(pady=(0, 20))
            
            self.countdown_label = tk.Label(main_frame, text="",
                                           bg=WindowsClassicColors.WINDOW_BG,
                                           fg=WindowsClassicColors.ERROR,
                                           font=('Segoe UI', 16, 'bold'))
            self.countdown_label.pack(pady=(0, 25))
            
            button_frame = create_classic_frame(main_frame)
            button_frame.pack()
            
            stay_btn = tk.Button(button_frame, text="✅ Weiter arbeiten", 
                                command=self._on_stay,
                                bg='#e1e1e1', fg='#000000', font=('Segoe UI', 10, 'bold'),
                                relief='raised', bd=1, padx=25, pady=10,
                                width=15)
            stay_btn.pack(side='left', padx=(0, 20))
            
            lock_btn = tk.Button(button_frame, text="🔒 Jetzt sperren", 
                                command=self._on_lock,
                                bg='#e1e1e1', fg='#000000', font=('Segoe UI', 10, 'normal'),
                                relief='raised', bd=1, padx=25, pady=10,
                                width=15)
            lock_btn.pack(side='left')
            
            def create_hover_effect(button):
                def on_enter(event):
                    try:
                        button.config(bg='#d5d5d5')
                    except:
                        pass
                def on_leave(event):
                    try:
                        button.config(bg='#e1e1e1')
                    except:
                        pass
                button.bind('<Enter>', on_enter)
                button.bind('<Leave>', on_leave)
            
            create_hover_effect(stay_btn)
            create_hover_effect(lock_btn)
            
            self.dialog.bind('<Return>', lambda e: self._on_stay())
            self.dialog.bind('<Escape>', lambda e: self._on_lock())
            self.dialog.bind('<space>', lambda e: self._on_stay())
            
        except Exception as e:
            self.is_active = False
    
    def _start_countdown(self):
        self._update_countdown()
    
    def _update_countdown(self):
        if not self.is_active:
            return
        
        try:
            if self.countdown > 0:
                self.countdown_label.config(text="Sperre in " + str(self.countdown) + " Sekunden")
                self.countdown -= 1
                self.dialog.after(1000, self._update_countdown)
            else:
                self._on_lock()
        except:
            self.is_active = False
    
    def _on_stay(self):
        self.is_active = False
        try:
            self.on_stay_callback()
        except:
            pass
    
    def _on_lock(self):
        self.is_active = False
        try:
            self.on_lock_callback()
        except:
            pass
    
    def destroy(self):
        self.is_active = False
        try:
            if hasattr(self, 'dialog'):
                self.dialog.destroy()
        except:
            pass