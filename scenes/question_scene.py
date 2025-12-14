import pygame
import json
import random
import math
from scenes.base_scene import BaseScene
from settings import *

class QuestionScene(BaseScene):
    def __init__(self, game, level_id, callback, return_scene):
        super().__init__(game)
        self.callback = callback
        self.return_scene = return_scene
        self.level_id = str(level_id)

        self.font = pygame.font.SysFont("arial", 24)
        self.big_font = pygame.font.SysFont("arial", 32, bold=True)
        self.button_font = pygame.font.SysFont("arial", 28, bold=True)
        self.title_font = pygame.font.SysFont("arial", 36, bold=True)
        self.timer_font = pygame.font.SysFont("arial", 42, bold=True)  # Diperkecil untuk pojok

        # Load semua level pertanyaan 
        self.all_questions = self.load_all_questions()

        self.load_question()
        
        self.time_limit = self.get_time_limit(level_id)
        self.time_left = self.time_limit
        
        self.animation_timer = 0
        self.pulse_timer = 0
        
        # Buat overlay dengan efek vignette
        self.overlay = self.create_vignette_overlay()
        
        # Ukuran dan posisi untuk semua elemen
        self.screen_width = self.game.screen.get_width()
        self.screen_height = self.game.screen.get_height()
        
        # Panel pertanyaan
        self.panel_width = 600
        self.panel_height = 180
        self.panel_x = (self.screen_width - self.panel_width) // 2
        self.panel_y = 200  
        
        # Timer di pojok kanan atas
        self.timer_radius = 30  # Diperkecil
        self.timer_x = self.screen_width - 60
        self.timer_y = 60
        
        # Tombol
        self.button_width = 180
        self.button_height = 60
        self.button_y = 420
        
        # Tombol TRUE (kiri)
        self.true_button = pygame.Rect(
            self.screen_width // 2 - self.button_width - 20,
            self.button_y,
            self.button_width,
            self.button_height
        )
        
        # Tombol FALSE (kanan)
        self.false_button = pygame.Rect(
            self.screen_width // 2 + 20,
            self.button_y,
            self.button_width,
            self.button_height
        )
        
        # Track hover state
        self.hover_button = None
        
        # Timer animation
        self.timer_rotation = 0
        self.critical_time = 5 
        
        # Play popup sound
        self.game.audio.play('popupbug_hit')

    def load_all_questions(self):
        """Load all questions from questions.json file only"""
        with open("data/questions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Validasi struktur minimal
        if not isinstance(data, dict):
            raise ValueError("questions.json should be a dictionary")
        
        all_levels = {}
        for level in ["1", "2", "3"]:
            if level not in data:
                raise ValueError(f"Level {level} not found in questions.json")
            
            if not isinstance(data[level], list):
                raise ValueError(f"Level {level} should contain a list")
            
            all_levels[level] = data[level]
        
        return all_levels

    def create_vignette_overlay(self):
        """Create a vignette effect overlay"""
        overlay = pygame.Surface(self.game.screen.get_size(), pygame.SRCALPHA)
        center_x = overlay.get_width() // 2
        center_y = overlay.get_height() // 2
        max_radius = max(center_x, center_y) * 1.5
        
        # Create radial gradient
        for radius in range(int(max_radius), 0, -1):
            alpha = int(180 * (1 - radius / max_radius) ** 2)
            color = (0, 0, 0, alpha)
            pygame.draw.circle(overlay, color, (center_x, center_y), radius)
        
        return overlay

    def load_question(self):
        """Load a random question for the current level"""
        # Pastikan level_id valid
        if self.level_id not in self.all_questions:
            print(f"Warning: Level {self.level_id} not found in questions")
            self.level_id = "1"  # Fallback ke level 1
        
        questions = self.all_questions.get(self.level_id, [])
        
        if not questions:
            print(f"Warning: No questions for level {self.level_id}")
            # Buat pertanyaan default
            self.question = {
                "text": f"Default question for level {self.level_id}: Distractions reduce productivity.",
                "answer": True
            }
        else:
            self.question = random.choice(questions)

    def get_time_limit(self, level_id):
        """Get time limit based on level"""
        limits = {1: 12, 2: 10, 3: 8}
        return limits.get(level_id, 10)

        
    def handle_event(self, event):
        # Keyboard input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t or event.key == pygame.K_1:
                self.game.audio.play('button_click')
                self.finish(True)
            elif event.key == pygame.K_f or event.key == pygame.K_2:
                self.game.audio.play('button_click')
                self.finish(False)
            elif event.key == pygame.K_ESCAPE:
                self.game.audio.play('button_click')
                self.finish(False)
        
        # Mouse hover
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            old_hover = self.hover_button
            
            if self.true_button.collidepoint(mouse_pos):
                self.hover_button = "true"
            elif self.false_button.collidepoint(mouse_pos):
                self.hover_button = "false"
            else:
                self.hover_button = None
                
             # Play hover sound jika hover berubah
            if old_hover != self.hover_button and self.hover_button is not None:
                self.game.audio.play('hover')
        
        # Mouse click
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if self.true_button.collidepoint(mouse_pos):
                self.game.audio.play('button_click')
                self.finish(True)
            elif self.false_button.collidepoint(mouse_pos):
                self.game.audio.play('button_click')
                self.finish(False)

    def update(self, dt):
        self.time_left -= dt
        self.animation_timer += dt * 2
        self.pulse_timer += dt * 3
        self.timer_rotation += dt * (2 if self.time_left < self.critical_time else 1)
        
        if self.time_left <= 0:
            self.finish(False)

    def finish(self, player_answer):
        correct = player_answer == self.question["answer"]
        # Play feedback sound
        if correct:
            self.game.audio.play('answer_correct')
        else:
            self.game.audio.play('answer_wrong')
            pygame.time.delay(300)
        
        self.callback(correct)
        self.game.change_scene(self.return_scene)

    def render(self, screen):
        # Background dengan gradien berdasarkan waktu
        bg_color = self.get_background_color()
        screen.fill(bg_color)
        
        # Overlay dengan animasi
        overlay_copy = self.overlay.copy()
        vignette_pulse = 0.9 + 0.1 * math.sin(self.animation_timer)
        overlay_copy.set_alpha(int(150 * vignette_pulse))
        screen.blit(overlay_copy, (0, 0))
        
        # Timer di pojok kanan atas
        self.draw_timer(screen)
        
        # Judul FOCUS TEST - dipindah lebih ke kiri
        title = self.title_font.render("FOCUS TEST", True, (255, 255, 255))
        title_shadow = self.title_font.render("FOCUS TEST", True, (0, 0, 0, 150))
        title_x = 40  # Posisi kiri
        title_y = 40
        
        # Shadow effect
        screen.blit(title_shadow, (title_x + 2, title_y + 2))
        screen.blit(title, (title_x, title_y))
        
        # Level indicator - di samping judul
        level_text = self.font.render(f"Level {self.level_id} Challenge", True, (200, 220, 255))
        screen.blit(level_text, (title_x, title_y + 45))

        # Panel pertanyaan dengan efek
        self.draw_question_panel(screen)
        
        # Tombol TRUE dan FALSE
        self.draw_buttons(screen)
        

    def get_background_color(self):
        """Get background color based on time left"""
        if self.time_left > self.critical_time:
            # Normal - dark blue gradient
            progress = self.time_left / self.time_limit
            r = int(20 + 30 * progress)
            g = int(30 + 40 * progress)
            b = int(50 + 60 * progress)
            return (r, g, b)
        else:
            # Critical - pulsating dark red
            pulse = 0.7 + 0.3 * math.sin(self.pulse_timer * 4)
            r = int(60 + 20 * pulse)
            g = int(30 - 10 * pulse)
            b = int(30 - 10 * pulse)
            return (r, g, b)

    def draw_timer(self, screen):
        """Draw timer circle di pojok kanan atas"""
        time_ratio = self.time_left / self.time_limit
        
        # Warna berdasarkan sisa waktu
        if time_ratio > 0.6:
            color = (100, 255, 100)  # Hijau
        elif time_ratio > 0.3:
            color = (255, 255, 100)  # Kuning
        else:
            # Merah berdenyut saat waktu kritis
            pulse = 0.5 + 0.5 * math.sin(self.pulse_timer * 4)
            color = (255, int(100 + 50 * pulse), 100)  # Merah berdenyut
        
        # Timer background circle
        timer_bg_radius = self.timer_radius + 8
        pygame.draw.circle(screen, (20, 20, 30), 
                         (self.timer_x, self.timer_y), timer_bg_radius)
        
        # Outer glow effect saat waktu kritis
        if self.time_left < self.critical_time:
            pulse = 1 + 0.2 * math.sin(self.pulse_timer * 4)
            glow_radius = int(timer_bg_radius * pulse)
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*color, 80), 
                             (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, (self.timer_x - glow_radius, self.timer_y - glow_radius))
        
        # Progress ring background
        pygame.draw.circle(screen, (40, 40, 60), 
                         (self.timer_x, self.timer_y), self.timer_radius)
        
        # Timer progress ring
        if self.time_left > 0:
            progress = 360 * time_ratio
            pygame.draw.arc(screen, color,
                          (self.timer_x - self.timer_radius, 
                           self.timer_y - self.timer_radius,
                           self.timer_radius * 2, 
                           self.timer_radius * 2),
                          math.radians(-90), math.radians(progress - 90), 5)
        
        # Timer text
        timer_text = self.timer_font.render(f"{int(self.time_left)}", True, color)
        timer_rect = timer_text.get_rect(center=(self.timer_x, self.timer_y))
        screen.blit(timer_text, timer_rect)
        
        # Label "SEC" kecil di bawah angka
        sec_font = pygame.font.SysFont("arial", 14)
        sec_label = sec_font.render("Sec", True, (180, 180, 200))
        sec_rect = sec_label.get_rect(center=(self.timer_x, self.timer_y + 35))
        screen.blit(sec_label, sec_rect)

    def draw_question_panel(self, screen):
        """Draw question panel di tengah layar"""
        # Panel background dengan efek depth
        panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        
        # Shadow effect
        pygame.draw.rect(panel_surface, (0, 0, 0, 100), 
                        (3, 3, self.panel_width, self.panel_height), 
                        border_radius=12)
        
        # Main panel dengan gradien
        for y in range(self.panel_height):
            alpha = 220 - int(20 * (y / self.panel_height))
            color = (255, 255, 255, alpha)
            pygame.draw.line(panel_surface, color, 
                           (0, y), (self.panel_width, y))
        
        # Border dengan animasi
        border_color = (100, 150, 200) if self.time_left > self.critical_time else (255, 100, 100)
        border_width = 3
        
        if self.time_left < self.critical_time:
            border_width += int(2 * math.sin(self.pulse_timer * 4))
        
        pygame.draw.rect(panel_surface, border_color, 
                        (0, 0, self.panel_width, self.panel_height), 
                        border_width, border_radius=10)
        
        # Inner highlight
        pygame.draw.rect(panel_surface, (255, 255, 255, 30), 
                        (2, 2, self.panel_width - 4, self.panel_height - 4), 
                        1, border_radius=8)
        
        screen.blit(panel_surface, (self.panel_x, self.panel_y))
        
        # Pertanyaan (dipusatkan dalam panel)
        text_lines = self.wrap_text(self.question["text"], self.font, self.panel_width - 40)
        
        # Hitung total tinggi text
        line_height = 28
        total_text_height = len(text_lines) * line_height
        start_y = self.panel_y + (self.panel_height - total_text_height) // 2
        
        # Gambar setiap baris
        for i, line in enumerate(text_lines):
            line_color = (40, 40, 40) if self.time_left > self.critical_time else (60, 40, 40)
            line_surface = self.font.render(line, True, line_color)
            line_x = self.screen_width // 2 - line_surface.get_width() // 2
            line_y = start_y + i * line_height
            screen.blit(line_surface, (line_x, line_y))
        

    def draw_buttons(self, screen):
        """Draw TRUE and FALSE buttons"""
        # TRUE button (hijau)
        true_color, true_border = self.get_button_colors("true")
        self.draw_button(screen, self.true_button, "TRUE", true_color, true_border)
        
        # FALSE button (merah)
        false_color, false_border = self.get_button_colors("false")
        self.draw_button(screen, self.false_button, "FALSE", false_color, false_border)

    def draw_button(self, screen, rect, text, color, border_color):
        """Draw a single button with shortcut hint"""
        button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        is_hovered = (self.hover_button == text.lower())
        
        # Button background dengan gradien
        for y in range(rect.height):
            shade = int(40 * (y / rect.height))
            row_color = (
                min(255, color[0] + shade),
                min(255, color[1] + shade),
                min(255, color[2] + shade)
            )
            pygame.draw.line(button_surface, row_color, (0, y), (rect.width, y))
        
        # Button border
        border_width = 4 if is_hovered else 3
        
        if self.time_left < self.critical_time and not is_hovered:
            # Pulse effect saat waktu kritis
            border_width += int(math.sin(self.pulse_timer * 4))
        
        pygame.draw.rect(button_surface, border_color, 
                        (0, 0, rect.width, rect.height), 
                        border_width, border_radius=10)
        
        # Button text
        text_surface = self.button_font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(rect.width//2, rect.height//2 - 5))
        button_surface.blit(text_surface, text_rect)
        
        # Hover glow effect
        if is_hovered:
            glow_size = 8
            glow_surface = pygame.Surface((rect.width + glow_size*2, rect.height + glow_size*2), pygame.SRCALPHA)
            glow_alpha = int(100 * (0.7 + 0.3 * math.sin(self.animation_timer * 2)))
            pygame.draw.rect(glow_surface, (*border_color[:3], glow_alpha), 
                           (glow_size, glow_size, rect.width, rect.height), 
                           border_radius=10 + glow_size)
            screen.blit(glow_surface, (rect.x - glow_size, rect.y - glow_size))
        
        screen.blit(button_surface, rect)

    def get_button_colors(self, button_type):
        """Get button colors based on hover state"""
        is_hovered = (self.hover_button == button_type)
        
        if button_type == "true":
            if is_hovered:
                return ((120, 220, 120), (80, 200, 80))  # Hijau terang saat hover
            else:
                return ((70, 160, 70), (50, 140, 50))    # Hijau normal
        else:  # false
            if is_hovered:
                return ((240, 120, 120), (220, 80, 80))  # Merah terang saat hover
            else:
                return ((180, 70, 70), (160, 50, 50))    # Merah normal

    def wrap_text(self, text, font, width):
        """Wrap text to fit within given width"""
        words = text.split(" ")
        lines = []
        current = ""
        
        for w in words:
            test = current + w + " "
            if font.size(test)[0] <= width:
                current = test
            else:
                if current:
                    lines.append(current.strip())
                current = w + " "
        
        if current:
            lines.append(current.strip())
        
        return lines