import tkinter as tk
from tkinter import ttk
import math
from datetime import datetime
from gui.modern_styles import ModernColors


class SecurityDashboardManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.dashboard_frame = None
        self.metrics = {
            'strong_passwords': {'current': 0, 'total': 0},
            'totp_enabled': {'current': 0, 'total': 0},
            'duplicate_passwords': 0,
            'last_backup': None,
            'overall_score': 0
        }
        self.update_timer = None
        self.is_destroyed = False
        
    def create_dashboard(self, parent):
        self.dashboard_frame = tk.Frame(parent, 
                                       bg=ModernColors.PANEL_BG, 
                                       relief='solid', 
                                       bd=1,
                                       width=220,
                                       height=280)
        self.dashboard_frame.pack_propagate(False)
        
        self._create_header()
        self._create_metrics()
        self._create_overall_score()
        
        self.refresh_metrics()
        self._start_auto_refresh()
        
        return self.dashboard_frame
    
    def _create_header(self):
        header_frame = tk.Frame(self.dashboard_frame, bg=ModernColors.PANEL_BG)
        header_frame.pack(fill='x', padx=8, pady=(8, 4))
        
        icon_label = tk.Label(header_frame, text="🛡️", 
                             bg=ModernColors.PANEL_BG, 
                             fg="#6ba644",
                             font=('Segoe UI', 14, 'normal'))
        icon_label.pack(side='left')
        
        title_label = tk.Label(header_frame, text="Security Health", 
                              bg=ModernColors.PANEL_BG, 
                              fg=ModernColors.TEXT_PRIMARY,
                              font=('Segoe UI', 10, 'bold'))
        title_label.pack(side='left', padx=(6, 0))
    
    def _create_metrics(self):
        metrics_frame = tk.Frame(self.dashboard_frame, bg=ModernColors.PANEL_BG)
        metrics_frame.pack(fill='x', padx=8, pady=4)
        
        self.strong_pw_metric = self._create_metric_row(
            metrics_frame, "Starke Passwörter", "0/0", 0)
        
        self.totp_metric = self._create_metric_row(
            metrics_frame, "2FA aktiviert", "0/0", 0)
        
        self.duplicate_metric = self._create_simple_metric_row(
            metrics_frame, "Duplikate", "0")
        
        self.backup_metric = self._create_simple_metric_row(
            metrics_frame, "Letztes Backup", "Nie")
    
    def _create_metric_row(self, parent, label, value, progress):
        metric_frame = tk.Frame(parent, bg=ModernColors.PANEL_BG)
        metric_frame.pack(fill='x', pady=2)
        
        label_frame = tk.Frame(metric_frame, bg=ModernColors.PANEL_BG)
        label_frame.pack(fill='x')
        
        tk.Label(label_frame, text=label,
                bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_SECONDARY,
                font=('Segoe UI', 8, 'normal')).pack(side='left')
        
        value_label = tk.Label(label_frame, text=value,
                              bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_PRIMARY,
                              font=('Segoe UI', 8, 'bold'))
        value_label.pack(side='right')
        
        progress_frame = tk.Frame(metric_frame, bg=ModernColors.PANEL_BG)
        progress_frame.pack(fill='x', pady=(2, 0))
        
        progress_bg = tk.Frame(progress_frame, bg="#eeeeee", height=4)
        progress_bg.pack(fill='x')
        
        progress_fill = tk.Frame(progress_bg, bg="#6ba644", height=4)
        progress_fill.place(x=0, y=0, relwidth=progress/100 if progress > 0 else 0, height=4)
        
        return {
            'frame': metric_frame,
            'value_label': value_label,
            'progress_fill': progress_fill,
            'progress_bg': progress_bg
        }
    
    def _create_simple_metric_row(self, parent, label, value):
        metric_frame = tk.Frame(parent, bg=ModernColors.PANEL_BG)
        metric_frame.pack(fill='x', pady=2)
        
        tk.Label(metric_frame, text=label,
                bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_SECONDARY,
                font=('Segoe UI', 8, 'normal')).pack(side='left')
        
        value_label = tk.Label(metric_frame, text=value,
                              bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_PRIMARY,
                              font=('Segoe UI', 8, 'bold'))
        value_label.pack(side='right')
        
        return {'value_label': value_label}
    
    def _create_overall_score(self):
        separator = tk.Frame(self.dashboard_frame, bg="#eeeeee", height=1)
        separator.pack(fill='x', padx=8, pady=8)
        
        score_frame = tk.Frame(self.dashboard_frame, bg=ModernColors.PANEL_BG)
        score_frame.pack(fill='x', padx=8, pady=(0, 8))
        
        canvas_frame = tk.Frame(score_frame, bg=ModernColors.PANEL_BG)
        canvas_frame.pack()
        
        self.score_canvas = tk.Canvas(canvas_frame, width=60, height=60, 
                                     bg=ModernColors.PANEL_BG, highlightthickness=0)
        self.score_canvas.pack()
        
        self.score_text = tk.Label(score_frame, text="0%",
                                  bg=ModernColors.PANEL_BG, fg="#6ba644",
                                  font=('Segoe UI', 9, 'bold'))
        self.score_text.pack(pady=(2, 0))
        
        tk.Label(score_frame, text="Security Score",
                bg=ModernColors.PANEL_BG, fg=ModernColors.TEXT_SECONDARY,
                font=('Segoe UI', 7, 'normal')).pack()
    
    def refresh_metrics(self):
        if self.is_destroyed or not self.dashboard_frame:
            return
        
        try:
            if not hasattr(self.main_window, 'pm') or not self.main_window.pm.is_unlocked:
                return
            
            entries = self.main_window.pm.list_entries()
            
            strong_count = 0
            totp_count = 0
            passwords = []
            
            for entry in entries:
                if hasattr(self.main_window, 'password_generator'):
                    _, score = self.main_window.password_generator.calculate_password_strength(entry.password)
                    if score >= 70:
                        strong_count += 1
                
                if entry.has_totp():
                    totp_count += 1
                
                passwords.append(entry.password)
            
            duplicate_count = len(passwords) - len(set(passwords))
            
            total_entries = len(entries)
            
            self.metrics['strong_passwords'] = {'current': strong_count, 'total': total_entries}
            self.metrics['totp_enabled'] = {'current': totp_count, 'total': total_entries}
            self.metrics['duplicate_passwords'] = duplicate_count
            
            if hasattr(self.main_window, 'backup_manager'):
                backups = self.main_window.backup_manager.list_backups()
                if backups:
                    latest_backup = backups[0]['created']
                    self.metrics['last_backup'] = latest_backup
            
            overall_score = self._calculate_overall_score()
            self.metrics['overall_score'] = overall_score
            
            self._update_display()
            
        except Exception as e:
            pass
    
    def _calculate_overall_score(self):
        score = 0
        
        if self.metrics['strong_passwords']['total'] > 0:
            pw_ratio = self.metrics['strong_passwords']['current'] / self.metrics['strong_passwords']['total']
            score += pw_ratio * 40
        
        if self.metrics['totp_enabled']['total'] > 0:
            totp_ratio = self.metrics['totp_enabled']['current'] / self.metrics['totp_enabled']['total']
            score += totp_ratio * 30
        
        if self.metrics['duplicate_passwords'] == 0:
            score += 20
        elif self.metrics['duplicate_passwords'] <= 2:
            score += 10
        
        if self.metrics['last_backup']:
            days_since_backup = (datetime.now() - self.metrics['last_backup']).days
            if days_since_backup == 0:
                score += 10
            elif days_since_backup <= 7:
                score += 5
        
        return min(int(score), 100)
    
    def _update_display(self):
        if self.is_destroyed or not self.dashboard_frame:
            return
        
        try:
            strong_total = self.metrics['strong_passwords']['total']
            strong_current = self.metrics['strong_passwords']['current']
            strong_percent = (strong_current / strong_total * 100) if strong_total > 0 else 0
            
            if self._widget_exists(self.strong_pw_metric['value_label']):
                self.strong_pw_metric['value_label'].config(text=f"{strong_current}/{strong_total}")
                self._update_progress_bar(self.strong_pw_metric['progress_fill'], 
                                         self.strong_pw_metric['progress_bg'], strong_percent)
            
            totp_total = self.metrics['totp_enabled']['total']
            totp_current = self.metrics['totp_enabled']['current']
            totp_percent = (totp_current / totp_total * 100) if totp_total > 0 else 0
            
            if self._widget_exists(self.totp_metric['value_label']):
                self.totp_metric['value_label'].config(text=f"{totp_current}/{totp_total}")
                self._update_progress_bar(self.totp_metric['progress_fill'], 
                                         self.totp_metric['progress_bg'], totp_percent)
            
            duplicate_text = str(self.metrics['duplicate_passwords'])
            duplicate_color = ModernColors.ERROR if self.metrics['duplicate_passwords'] > 0 else "#6ba644"
            if self._widget_exists(self.duplicate_metric['value_label']):
                self.duplicate_metric['value_label'].config(text=duplicate_text, fg=duplicate_color)
            
            if self.metrics['last_backup']:
                backup_text = self._format_backup_time(self.metrics['last_backup'])
            else:
                backup_text = "Nie"
            
            if self._widget_exists(self.backup_metric['value_label']):
                self.backup_metric['value_label'].config(text=backup_text)
            
            if self._widget_exists(self.score_canvas):
                self._update_score_circle(self.metrics['overall_score'])
            
            if self._widget_exists(self.score_text):
                self.score_text.config(text=f"{self.metrics['overall_score']}%")
                
        except Exception as e:
            pass
    
    def _widget_exists(self, widget):
        try:
            if widget is None:
                return False
            widget.winfo_exists()
            return True
        except:
            return False
    
    def _update_progress_bar(self, progress_fill, progress_bg, percent):
        try:
            if not self._widget_exists(progress_fill) or not self._widget_exists(progress_bg):
                return
            
            progress_bg.update_idletasks()
            bg_width = progress_bg.winfo_width()
            fill_width = int(bg_width * percent / 100)
            
            color = self._get_progress_color(percent)
            progress_fill.config(bg=color)
            progress_fill.place(x=0, y=0, width=fill_width, height=4)
        except:
            pass
    
    def _get_progress_color(self, percent):
        if percent >= 80:
            return "#6ba644"
        elif percent >= 60:
            return "#8bc34a"
        elif percent >= 40:
            return "#ff8c00"
        else:
            return "#d32f2f"
    
    def _update_score_circle(self, score):
        try:
            if not self._widget_exists(self.score_canvas):
                return
            
            self.score_canvas.delete("all")
            
            center_x, center_y = 30, 30
            radius = 25
            
            self.score_canvas.create_oval(center_x - radius, center_y - radius,
                                         center_x + radius, center_y + radius,
                                         outline="#eeeeee", width=3, fill="")
            
            if score > 0:
                color = self._get_score_color(score)
                
                if score >= 99.5:
                    self.score_canvas.create_oval(center_x - radius, center_y - radius,
                                                 center_x + radius, center_y + radius,
                                                 outline=color, width=3, fill="")
                else:
                    extent = int(360 * score / 100)
                    
                    self.score_canvas.create_arc(center_x - radius, center_y - radius,
                                                center_x + radius, center_y + radius,
                                                start=90, extent=-extent,
                                                outline=color, width=3, style="arc")
        except:
            pass
    
    def _get_score_color(self, score):
        if score >= 80:
            return "#6ba644"
        elif score >= 60:
            return "#8bc34a"
        elif score >= 40:
            return "#ff8c00"
        else:
            return "#d32f2f"
    
    def _format_backup_time(self, backup_time):
        now = datetime.now()
        diff = now - backup_time
        
        if diff.days == 0:
            hours = diff.seconds // 3600
            if hours == 0:
                return "Gerade"
            else:
                return f"{hours}h"
        elif diff.days == 1:
            return "Gestern"
        else:
            return f"{diff.days}d"
    
    def _start_auto_refresh(self):
        if self.is_destroyed:
            return
        
        if self.update_timer:
            try:
                self.main_window.root.after_cancel(self.update_timer)
            except:
                pass
        
        self.update_timer = self.main_window.root.after(30000, self._auto_refresh)
    
    def _auto_refresh(self):
        if not self.is_destroyed:
            self.refresh_metrics()
            self._start_auto_refresh()
    
    def destroy(self):
        self.is_destroyed = True
        
        if self.update_timer:
            try:
                self.main_window.root.after_cancel(self.update_timer)
            except:
                pass
            self.update_timer = None
        
        if self.dashboard_frame:
            try:
                self.dashboard_frame.destroy()
            except:
                pass
            self.dashboard_frame = None