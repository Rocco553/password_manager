import tkinter as tk
import math
from gui.modern_styles import ModernColors


class PasswordStrengthVisualizer:
    def __init__(self, parent, password_generator):
        self.parent = parent
        self.password_generator = password_generator
        self.canvas = None
        self.score_label = None
        self.strength_label = None
        self.requirements_widgets = []
        self.current_score = 0
        self.target_score = 0
        self.animation_steps = 0
        self.max_animation_steps = 20
        
    def create_visualizer(self, container_frame):
        viz_frame = tk.Frame(container_frame, bg=ModernColors.PANEL_BG)
        
        self._create_circular_progress(viz_frame)
        self._create_strength_bars(viz_frame)
        self._create_requirements(viz_frame)
        
        return viz_frame
    
    def _create_circular_progress(self, parent):
        circle_frame = tk.Frame(parent, bg=ModernColors.PANEL_BG)
        circle_frame.pack(pady=(0, 12))
        
        self.canvas = tk.Canvas(circle_frame, width=100, height=100, 
                               bg=ModernColors.PANEL_BG, highlightthickness=0)
        self.canvas.pack()
        
        score_frame = tk.Frame(parent, bg=ModernColors.PANEL_BG)
        score_frame.pack()
        
        self.score_label = tk.Label(score_frame, text="0%",
                                   bg=ModernColors.PANEL_BG, 
                                   fg=ModernColors.ERROR,
                                   font=('Segoe UI', 16, 'bold'))
        self.score_label.pack()
        
        self.strength_label = tk.Label(score_frame, text="Sehr schwach",
                                      bg=ModernColors.PANEL_BG, 
                                      fg=ModernColors.ERROR,
                                      font=('Segoe UI', 10, 'bold'))
        self.strength_label.pack(pady=(2, 0))
        
        self._draw_initial_circle()
    
    def _create_strength_bars(self, parent):
        bars_frame = tk.Frame(parent, bg=ModernColors.PANEL_BG)
        bars_frame.pack(pady=(12, 8))
        
        self.strength_bars = []
        for i in range(5):
            bar_container = tk.Frame(bars_frame, bg="#eeeeee", width=40, height=6)
            bar_container.pack(side='left', padx=2)
            bar_container.pack_propagate(False)
            
            bar_fill = tk.Frame(bar_container, bg="#eeeeee", height=6)
            bar_fill.place(x=0, y=0, width=0, height=6)
            
            self.strength_bars.append({
                'container': bar_container,
                'fill': bar_fill
            })
    
    def _create_requirements(self, parent):
        req_frame = tk.Frame(parent, bg=ModernColors.PANEL_BG)
        req_frame.pack(fill='x', pady=(8, 0))
        
        requirements = [
            "Mindestens 8 Zeichen",
            "Großbuchstaben (A-Z)",
            "Kleinbuchstaben (a-z)", 
            "Zahlen (0-9)",
            "Symbole (!@#$%...)"
        ]
        
        self.requirements_widgets = []
        for req_text in requirements:
            req_row = tk.Frame(req_frame, bg=ModernColors.PANEL_BG)
            req_row.pack(fill='x', pady=1)
            
            check_label = tk.Label(req_row, text="○",
                                  bg=ModernColors.PANEL_BG, 
                                  fg=ModernColors.TEXT_DISABLED,
                                  font=('Segoe UI', 10, 'normal'))
            check_label.pack(side='left', padx=(0, 6))
            
            text_label = tk.Label(req_row, text=req_text,
                                 bg=ModernColors.PANEL_BG, 
                                 fg=ModernColors.TEXT_DISABLED,
                                 font=('Segoe UI', 8, 'normal'))
            text_label.pack(side='left')
            
            self.requirements_widgets.append({
                'check': check_label,
                'text': text_label,
                'met': False
            })
    
    def _draw_initial_circle(self):
        self.canvas.delete("all")
        
        center_x, center_y = 50, 50
        radius = 35
        
        self.canvas.create_oval(center_x - radius, center_y - radius,
                               center_x + radius, center_y + radius,
                               outline="#eeeeee", width=4, fill="")
    
    def update_strength(self, password):
        if not password:
            self._reset_visualization()
            return
        
        score = self._calculate_detailed_score(password)
        strength_text, color = self._get_strength_info(score)
        
        self.target_score = score
        self._animate_to_target()
        
        self.strength_label.config(text=strength_text, fg=color)
        self._update_strength_bars(score, color)
        self._update_requirements(password)
    
    def _calculate_detailed_score(self, password):
        if not password:
            return 0
            
        score = 0
        
        if len(password) >= 8:
            score += 20
        elif len(password) >= 6:
            score += 10
        elif len(password) >= 4:
            score += 5
        
        if any(c.isupper() for c in password):
            score += 15
        if any(c.islower() for c in password):
            score += 15
        if any(c.isdigit() for c in password):
            score += 15
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 20
        
        if len(password) >= 12:
            score += 5
        if len(password) >= 16:
            score += 5
        
        unique_ratio = len(set(password)) / len(password) if password else 0
        if unique_ratio > 0.8:
            score += 5
        
        return min(score, 100)
    
    def _get_strength_info(self, score):
        if score >= 85:
            return "Sehr stark", ModernColors.SUCCESS
        elif score >= 70:
            return "Stark", ModernColors.ACCENT_GREEN_LIGHT
        elif score >= 50:
            return "Mittel", ModernColors.WARNING
        elif score >= 30:
            return "Schwach", "#ff6b35"
        else:
            return "Sehr schwach", ModernColors.ERROR
    
    def _animate_to_target(self):
        if abs(self.current_score - self.target_score) < 1:
            self.current_score = self.target_score
            self._draw_progress_circle()
            self._update_score_label()
            return
        
        diff = self.target_score - self.current_score
        step = diff / 10
        self.current_score += step
        
        self._draw_progress_circle()
        self._update_score_label()
        
        self.parent.after(20, self._animate_to_target)
    
    def _draw_progress_circle(self):
        self.canvas.delete("all")
        
        center_x, center_y = 50, 50
        radius = 35
        
        self.canvas.create_oval(center_x - radius, center_y - radius,
                               center_x + radius, center_y + radius,
                               outline="#eeeeee", width=4, fill="")
        
        if self.current_score > 0:
            color = self._get_progress_color(self.current_score)
            
            if self.current_score >= 99.5:
                self.canvas.create_oval(center_x - radius, center_y - radius,
                                       center_x + radius, center_y + radius,
                                       outline=color, width=4, fill="")
            else:
                extent = int(360 * self.current_score / 100)
                start_angle = 90
                
                self.canvas.create_arc(center_x - radius, center_y - radius,
                                      center_x + radius, center_y + radius,
                                      start=start_angle, extent=-extent,
                                      outline=color, width=4, style="arc")
    
    def _get_progress_color(self, score):
        if score >= 85:
            return ModernColors.SUCCESS
        elif score >= 70:
            return ModernColors.ACCENT_GREEN_LIGHT
        elif score >= 50:
            return ModernColors.WARNING
        elif score >= 30:
            return "#ff6b35"
        else:
            return ModernColors.ERROR
    
    def _update_score_label(self):
        score_text = f"{int(self.current_score)}%"
        color = self._get_progress_color(self.current_score)
        self.score_label.config(text=score_text, fg=color)
        
        if int(self.current_score) != int(self.target_score):
            self.score_label.config(font=('Segoe UI', 17, 'bold'))
            self.parent.after(50, lambda: self.score_label.config(font=('Segoe UI', 16, 'bold')))
    
    def _update_strength_bars(self, score, color):
        for i, bar in enumerate(self.strength_bars):
            threshold = (i + 1) * 20
            
            if score >= threshold:
                bar['fill'].config(bg=color)
                bar['fill'].place(x=0, y=0, width=40, height=6)
            else:
                remaining_score = max(0, score - (i * 20))
                width = int(40 * remaining_score / 20) if remaining_score > 0 else 0
                
                if width > 0:
                    bar['fill'].config(bg=color)
                    bar['fill'].place(x=0, y=0, width=width, height=6)
                else:
                    bar['fill'].place(x=0, y=0, width=0, height=6)
    
    def _update_requirements(self, password):
        requirements_met = [
            len(password) >= 8,
            any(c.isupper() for c in password),
            any(c.islower() for c in password),
            any(c.isdigit() for c in password),
            any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        ]
        
        for i, (met, widget) in enumerate(zip(requirements_met, self.requirements_widgets)):
            if met != widget['met']:
                widget['met'] = met
                
                if met:
                    widget['check'].config(text="✓", fg=ModernColors.SUCCESS)
                    widget['text'].config(fg=ModernColors.TEXT_PRIMARY)
                    
                    widget['check'].config(font=('Segoe UI', 11, 'bold'))
                    self.parent.after(100, lambda w=widget: w['check'].config(font=('Segoe UI', 10, 'normal')))
                else:
                    widget['check'].config(text="○", fg=ModernColors.TEXT_DISABLED)
                    widget['text'].config(fg=ModernColors.TEXT_DISABLED)
    
    def _reset_visualization(self):
        self.current_score = 0
        self.target_score = 0
        
        self._draw_initial_circle()
        self.score_label.config(text="0%", fg=ModernColors.ERROR)
        self.strength_label.config(text="Sehr schwach", fg=ModernColors.ERROR)
        
        for bar in self.strength_bars:
            bar['fill'].place(x=0, y=0, width=0, height=6)
        
        for widget in self.requirements_widgets:
            widget['check'].config(text="○", fg=ModernColors.TEXT_DISABLED)
            widget['text'].config(fg=ModernColors.TEXT_DISABLED)
            widget['met'] = False