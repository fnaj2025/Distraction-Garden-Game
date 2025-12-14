# scenes/game_scene.py

import pygame
import random
import math

from scenes.base_scene import BaseScene
from scenes.question_scene import QuestionScene

from entities.player import Player
from entities.bug import ChatBug, NotifBadge, PopupBug
from entities.plant import Plant
from entities.floworb import FlowOrb
from ui.hud import HUD
from settings import *


class GameScene(BaseScene):
    def __init__(self, game, level_id: int):
        super().__init__(game)
        self.level_id = level_id

        # ===== LEVEL TARGETS =====
        self.level_targets = {1: 100, 2: 200, 3: 300}  # Score target per level
        self.target_score = self.level_targets.get(level_id, 100)
        self.level_complete = False
        
        # ===== CORE STATE =====
        self.focus = 100
        self.game_over = False
        self.repels = 0  # Counter for repelled bugs

        # ===== WORLD =====
        self.entities = []
        self.player = Player(WIDTH // 2, HEIGHT // 2 + 40)
        self.entities.append(self.player)

        # Background particles
        self.bg_particles = []
        self.init_background()

        # initial plants
        for i in range(3):
            self.entities.append(
                Plant(140 + i * 220, HEIGHT - 140)
            )

        # ===== UI =====
        self.hud = None

        # ===== SPAWN CONTROL =====
        self.bug_timer = 0
        self.flow_timer = 0
        self.question_cooldown = 0

        self.font = pygame.font.SysFont("segoeui", 20)
        self.title_font = pygame.font.SysFont("bahnschrift", 32, bold=True, italic=True)
        self.big_font = pygame.font.SysFont("arial", 48, bold=True)
        
        self.recent_bug_pressure = []
        
        # Level background colors
        self.level_colors = [
            (210, 235, 210),  # Level 1 - Soft green
            (235, 210, 220),  # Level 2 - Soft pink
            (210, 220, 235)   # Level 3 - Soft blue
        ]
        
        # Animation timers
        self.pulse_timer = 0
        self.focus_pulse = 0
        
        # Game over/complete screen state
        self.game_over_selection = 0  # 0: Retry, 1: Home
        self.level_complete_selection = 0  # 0: Next Level, 1: Home
        
        # Tombol untuk touchpad
        self.retry_button = None
        self.home_button = None
        self.next_button = None

        # Play level start sound
        self.game.audio.play('level_start')

    def init_background(self):
        """Initialize background particles"""
        for _ in range(PARTICLE_COUNT):
            self.bg_particles.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(64, HEIGHT - 160),
                'size': random.randint(2, 5),
                'speed': random.uniform(0.1, 0.3),
                'color': random.choice([GRASS_LIGHT, GRASS_DARK, (255, 255, 255, 100)]),
                'wobble': random.uniform(0, math.pi * 2)
            })
        
    # ===============================
    # EVENT HANDLING
    # ===============================
    def handle_event(self, event):
        # Handle mouse events untuk touchpad
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            if self.game_over:
                if self.retry_button and self.retry_button.collidepoint(mouse_pos):
                    self.game.audio.play('button_click')
                    from scenes.game_scene import GameScene
                    self.game.change_scene(GameScene(self.game, self.level_id))
                    return
                elif self.home_button and self.home_button.collidepoint(mouse_pos):
                    self.game.audio.play('button_click')
                    from scenes.home_scene import HomeScene
                    self.game.change_scene(HomeScene(self.game))
                    return
            
            if self.level_complete:
                if self.next_button and self.next_button.collidepoint(mouse_pos):
                    self.game.audio.play('button_click')
                    if self.level_id < 3:
                        from scenes.game_scene import GameScene
                        self.game.change_scene(GameScene(self.game, self.level_id + 1))
                    else:
                        from scenes.home_scene import HomeScene
                        self.game.change_scene(HomeScene(self.game))
                    return
                elif self.home_button and self.home_button.collidepoint(mouse_pos):
                    self.game.audio.play('button_click')
                    from scenes.home_scene import HomeScene
                    self.game.change_scene(HomeScene(self.game))
                    return
                
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    self.game.audio.play('menu_select')
                    self.game_over_selection = 1 if self.game_over_selection == 0 else 0
                elif event.key == pygame.K_RETURN:
                    self.game.audio.play('button_click')
                    if self.game_over_selection == 0:  # Retry
                        from scenes.game_scene import GameScene
                        self.game.change_scene(GameScene(self.game, self.level_id))
                    elif self.game_over_selection == 1:  # Home
                        from scenes.home_scene import HomeScene
                        self.game.change_scene(HomeScene(self.game))
                elif event.key == pygame.K_ESCAPE:
                    self.game.audio.play('button_click')
                    from scenes.home_scene import HomeScene
                    self.game.change_scene(HomeScene(self.game))
            return
        
        if self.level_complete:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    self.game.audio.play('menu_select')
                    self.level_complete_selection = 1 if self.level_complete_selection == 0 else 0
                elif event.key == pygame.K_RETURN:
                    self.game.audio.play('button_click')
                    if self.level_complete_selection == 0:  # Next Level atau Finish
                        if self.level_id < 3:
                            from scenes.game_scene import GameScene
                            self.game.change_scene(GameScene(self.game, self.level_id + 1))
                        else:
                            from scenes.home_scene import HomeScene
                            self.game.change_scene(HomeScene(self.game))
                    elif self.level_complete_selection == 1:  # Home
                        from scenes.home_scene import HomeScene
                        self.game.change_scene(HomeScene(self.game))
                elif event.key == pygame.K_ESCAPE:
                    self.game.audio.play('button_click')
                    from scenes.home_scene import HomeScene
                    self.game.change_scene(HomeScene(self.game))
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.audio.play('button_click')
                from scenes.home_scene import HomeScene
                self.game.change_scene(HomeScene(self.game))

    # ===============================
    # UPDATE LOOP
    # ===============================
    def update(self, dt):
        # Update animation timers
        self.pulse_timer += dt * 2
        self.focus_pulse = max(0, self.focus_pulse - dt * 2)

        # Jika game over atau level complete, hanya update animasi
        if self.game_over or self.level_complete:
            return

        # Update background particles
        for particle in self.bg_particles:
            particle['wobble'] += dt * 2
            particle['x'] += math.sin(particle['wobble']) * particle['speed']
            particle['y'] += math.cos(particle['wobble'] * 0.7) * particle['speed']
            
            # Wrap around screen
            if particle['x'] < 0:
                particle['x'] = WIDTH
            elif particle['x'] > WIDTH:
                particle['x'] = 0
            if particle['y'] < 64:
                particle['y'] = HEIGHT - 160
            elif particle['y'] > HEIGHT - 160:
                particle['y'] = 64

        # cooldown soal
        if self.question_cooldown > 0:
            self.question_cooldown -= dt

        self.focus -= dt * (2 + self.level_id * 1)

        # PERIKSA APAKAH LEVEL SELESAI
        if self.player.score >= self.target_score and not self.level_complete:
            self.level_complete = True
            self.focus = 100
            self.game.audio.play('level_complete') 
            return

        # game over jika fokus habis
        if self.focus <= 0 and not self.level_complete:
            self.focus = 0
            self.game_over = True
            self.game.audio.play('game_over')  
            return

        # spawn bug 
        self.bug_timer += dt
        if self.bug_timer >= max(1.5, 3.0 - self.level_id * 0.3):  
            self.spawn_bug()
            self.bug_timer = 0

        bug_count = len([
            e for e in self.entities
            if e.__class__.__name__ in ("ChatBug", "NotifBadge", "PopupBug")
        ])
        self.recent_bug_pressure.append(bug_count)
        if len(self.recent_bug_pressure) > 120:
            self.recent_bug_pressure.pop(0)

        self.flow_timer += dt
        if self.flow_timer >= 8:
            self.spawn_flow()
            self.flow_timer = 0

        # update entities
        for ent in list(self.entities):
            ent.update(dt, self)
            if not ent.is_alive():
                self.entities.remove(ent)

        # collision detection 
        for ent in list(self.entities):
            if ent is self.player:
                continue
            
            if self.player.rect.colliderect(ent.rect):
                # Jika ent adalah bug (gangguan)
                if ent.__class__.__name__ in ("ChatBug", "NotifBadge", "PopupBug"):
                    result = ent.interact(self.player, self)
                    
                    if result:
                        if result.get("type") == "bug_destroyed":
                            if isinstance(ent, ChatBug):
                                self.game.audio.play('chatbug_hit')
                            elif isinstance(ent, NotifBadge):
                                self.game.audio.play('notifbug_hit')
                            elif isinstance(ent, PopupBug):
                                self.game.audio.play('popupbug_hit')
                                
                            self.repels += 1  # Tambah counter repels
                            self.player.score += 15
                            self.focus_pulse = 1.0
                            # Spawn particles untuk feedback
                            self.spawn_particles(ent, "spark", 10)
                        
                        elif result.get("type") == "popup_bug":
                            if self.question_cooldown <= 0:
                                self.trigger_question()
                
                # Jika ent adalah flow orb
                elif ent.__class__.__name__ == "FlowOrb":
                    result = ent.interact(self.player, self)
                    if result and result.get("type") == "flow_collected":
                        self.focus = min(100, self.focus + 20)
                        self.player.score += 20
                        self.focus_pulse = 1.5

    # ===============================
    # RENDER
    # ===============================
    def render(self, screen):
        bg_color = self.level_colors[(self.level_id - 1) % len(self.level_colors)]
        screen.fill(bg_color)

        # Draw background particles
        for particle in self.bg_particles:
            alpha = 100 + int(math.sin(particle['wobble']) * 50)
            color = (*particle['color'][:3], alpha)
            s = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (particle['size'], particle['size']), particle['size'])
            screen.blit(s, (int(particle['x']), int(particle['y'])))

        # ground with pattern
        pygame.draw.rect(
            screen,
            GRASS_DARK,
            (0, HEIGHT - 160, WIDTH, 160)
        )
        
        # Grass pattern
        for i in range(0, WIDTH, 20):
            height = 10 + int(math.sin(i * 0.1 + self.pulse_timer) * 3)
            pygame.draw.line(
                screen,
                GRASS_LIGHT,
                (i, HEIGHT - 160),
                (i, HEIGHT - 160 + height),
                2
            )

        # entities
        for ent in self.entities:
            ent.draw(screen)

        # Focus pulse effect
        if self.focus_pulse > 0:
            pulse_radius = int(50 * self.focus_pulse)
            pulse_surface = pygame.Surface((pulse_radius * 2, pulse_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(pulse_surface, (100, 200, 255, int(100 * self.focus_pulse)), 
                             (pulse_radius, pulse_radius), pulse_radius)
            screen.blit(pulse_surface, (self.player.rect.centerx - pulse_radius, 
                                      self.player.rect.centery - pulse_radius))

        # Title and Stats overlay
        self.draw_game_header(screen)

        # Tampilkan layar game over atau level complete
        if self.game_over:
            self.draw_game_over_screen(screen)
        elif self.level_complete:
            self.draw_level_complete_screen(screen)

    def draw_game_header(self, screen):
        """Draw game title and player stats dengan target score"""
        # 1. TOP BAR BACKGROUND
        top_bar = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
        for y in range(80):
            alpha = 180 - int(y * 0.5)
            color = (20, 30, 40, alpha)
            pygame.draw.line(top_bar, color, (0, y), (WIDTH, y))
        screen.blit(top_bar, (0, 0))
        
        # 2. KIRI: GAME TITLE
        pulse = (math.sin(self.pulse_timer * 1.5) + 1) * 0.5
        title_color = (int(180 + 50 * pulse), int(220 + 20 * pulse), 255)
        
        title = self.title_font.render("DISTRACTION GARDEN", True, title_color)
        subtitle = pygame.font.SysFont("Russo One", 21).render("Protect Your Focus", True, (200, 200, 220))

        screen.blit(title, (25, 15))
        screen.blit(subtitle, (30, 55))
        
        # 3. TENGAH: FOCUS BAR 
        focus_percent = int(self.focus)
        bar_width = 200
        bar_height = 20
        bar_x = 450
        bar_y = 28
    
        # Label FOCUS
        focus_label = pygame.font.SysFont("arial", 17, bold=True).render("Focus", True, (240, 240, 240))
        screen.blit(focus_label, (bar_x - 55, bar_y + 3))
        
        # Focus bar
        bar_container = pygame.Rect(bar_x - 3, bar_y - 3, bar_width + 6, bar_height + 6)
        pygame.draw.rect(screen, (40, 50, 70), bar_container, border_radius=6)
        pygame.draw.rect(screen, (80, 90, 110), bar_container, 2, border_radius=6)

        # Bar fill
        fill_width = max(0, int((focus_percent / 100) * bar_width))
        if fill_width > 0:
            if focus_percent > 70:
                color_start = (80, 220, 120)
                color_end = (120, 255, 160)
            elif focus_percent > 40:
                color_start = (250, 200, 80)
                color_end = (255, 220, 100)
            else:
                color_start = (220, 70, 60)
                color_end = (255, 100, 90)
            
            # Draw gradient fill
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            for i in range(fill_width):
                ratio = i / fill_width
                r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
                g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
                b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
                pygame.draw.line(screen, (r, g, b), 
                               (bar_x + i, bar_y), 
                               (bar_x + i, bar_y + bar_height - 1))
            
            pygame.draw.rect(screen, (255, 255, 255, 50), 
                            (bar_x, bar_y, fill_width, bar_height), 
                            1, border_radius=4)
            
            # Pulse effect saat fokus rendah
            if focus_percent < 30:
                pulse_alpha = int(100 * (0.5 + 0.5 * math.sin(self.pulse_timer * 4)))
                pulse_overlay = pygame.Surface((fill_width, bar_height), pygame.SRCALPHA)
                pulse_overlay.fill((255, 255, 255, pulse_alpha))
                screen.blit(pulse_overlay, (bar_x, bar_y))
        
        # Persentase fokus
        focus_text = pygame.font.SysFont("arial", 17, bold=True).render(f"{focus_percent}%", True, (255, 255, 255))
        screen.blit(focus_text, (bar_x + bar_width + 15, bar_y + 2))
        
        # Progress score (target)
        progress_ratio = min(1.0, self.player.score / self.target_score)
        progress_text = pygame.font.SysFont("arial", 12).render(
            f"Target: {self.player.score}/{self.target_score}", 
            True, (200, 200, 200)
        )
        screen.blit(progress_text, (bar_x, bar_y + bar_height + 8))
        
        # Progress bar kecil
        progress_width = 100
        progress_height = 4
        progress_bar_x = bar_x + bar_width - progress_width
        progress_bar_y = bar_y + bar_height + 12
        
        pygame.draw.rect(screen, (60, 60, 80), 
                        (progress_bar_x, progress_bar_y, progress_width, progress_height))
        
        if progress_ratio > 0:
            progress_fill = int(progress_width * progress_ratio)
            progress_color = (100, 200, 100) if progress_ratio >= 1.0 else (100, 150, 255)
            pygame.draw.rect(screen, progress_color, 
                           (progress_bar_x, progress_bar_y, progress_fill, progress_height))
            
        # 4. STATS PANEL 
        stats_panel_width = 220
        stats_panel_height = 80
        stats_x = WIDTH - stats_panel_width - 20
        stats_y = 5
        
        # Panel background dengan efek depth
        panel_bg = pygame.Surface((stats_panel_width, stats_panel_height), pygame.SRCALPHA)
        
        # Gradient background
        for y in range(stats_panel_height):
            alpha = 120 + int(30 * (y / stats_panel_height))
            pygame.draw.line(panel_bg, (30, 40, 50, alpha), 
                            (0, y), (stats_panel_width, y))
        
        # Border dengan efek 3D
        pygame.draw.rect(panel_bg, (255, 255, 255, 40), 
                        (0, 0, stats_panel_width, stats_panel_height), 
                        2, border_radius=8)
        pygame.draw.rect(panel_bg, (0, 0, 0, 60), 
                        (2, 2, stats_panel_width - 4, stats_panel_height - 4), 
                        1, border_radius=6)
        
        screen.blit(panel_bg, (stats_x, stats_y))
        
        # Grid stats 2x2 dengan spacing yang baik
        stats = [
            ("Score", f"{self.player.score}", (255, 255, 180)),
            ("Level", f"{self.level_id}", (255, 180, 180)),
            ("Repels", f"{self.repels}", (180, 255, 180)),
            ("Plants", "3", (180, 180, 255))
        ]
        
        # Font untuk stats
        stat_label_font = pygame.font.SysFont("arial", 13)
        stat_value_font = pygame.font.SysFont("arial", 18, bold=True)
        
        for i, (label, value, color) in enumerate(stats):
            col = i % 2
            row = i // 2
            
            # Hitung posisi dengan padding
            cell_width = stats_panel_width // 2
            cell_height = stats_panel_height // 2
            
            stat_x_pos = stats_x + col * cell_width
            stat_y_pos = stats_y + row * cell_height
            
            # Center dalam cell
            label_text = stat_label_font.render(label, True, (200, 200, 220))
            label_rect = label_text.get_rect(center=(
                stat_x_pos + cell_width // 2,
                stat_y_pos + cell_height // 2 - 10
            ))
            
            value_text = stat_value_font.render(value, True, color)
            value_rect = value_text.get_rect(center=(
                stat_x_pos + cell_width // 2,
                stat_y_pos + cell_height // 2 + 12
            ))
            
            screen.blit(label_text, label_rect)
            screen.blit(value_text, value_rect)
            
            # Garis pemisah vertikal
            if col == 0:
                pygame.draw.line(screen, (255, 255, 255, 30),
                            (stat_x_pos + cell_width - 1, stat_y_pos + 5),
                            (stat_x_pos + cell_width - 1, stat_y_pos + cell_height - 5), 1)
            
            # Garis pemisah horizontal
            if row == 0:
                pygame.draw.line(screen, (255, 255, 255, 30),
                            (stat_x_pos + 5, stat_y_pos + cell_height - 1),
                            (stat_x_pos + cell_width - 5, stat_y_pos + cell_height - 1), 1)

    # ===============================
    # SPAWN METHODS
    # ===============================
    def spawn_bug(self):
        """Spawn bugs only from top with SLOWER speeds"""
        bug_colors = {
            "chat": (255, 50, 50),     
            "notif": (50, 200, 50),    
            "popup": (255, 255, 50)     
        }
        
        base_speeds = [1.0, 1.5, 2.0]
        speed_variation = 0.3
        
        kind = random.choice(["chat", "notif", "popup"])
        
        x = random.randint(60, WIDTH - 60)
        y = -20  # Start above screen
        
        speed = base_speeds[self.level_id - 1] + random.uniform(-speed_variation, speed_variation)
        
        if kind == "chat":
            bug = ChatBug(x, y)
            bug.speed = speed
            bug.color = bug_colors["chat"]
        elif kind == "notif":
            bug = NotifBadge(x, y)
            bug.speed = speed
            bug.color = bug_colors["notif"]
        else:
            bug = PopupBug(x, y)
            bug.speed = speed
            bug.color = bug_colors["popup"]
        
        self.entities.append(bug)

    def spawn_flow(self):
        x = random.randint(120, WIDTH - 120)
        y = random.randint(120, HEIGHT - 200)
        self.entities.append(FlowOrb(x, y))
    
    def spawn_particles(self, ent, kind="spark", count=8):
        """ Spawn particle effects at entity location.
        Called when bugs are destroyed, plants level up, etc. """
        from entities.particle import Particle
        
        cx, cy = ent.rect.center
        for _ in range(count):
            self.entities.append(Particle(cx, cy, kind))
    
    # ===============================
    # QUESTION INTEGRATION
    # ===============================
    def trigger_question(self):
        self.question_cooldown = 2
        self.game.change_scene(
            QuestionScene(
                self.game,
                self.level_id,
                self.on_question_result,
                return_scene=self
            )
        )

    def on_question_result(self, correct: bool):
        if correct:
            self.game.audio.play('answer_correct')
            self.focus = min(100, self.focus + 15)
            self.focus_pulse = 1.5
        else:
            self.game.audio.play('answer_wrong')
            self.focus -= 12
            self.bug_timer = -1.2

    # ===============================
    # COLLISION HANDLING 
    # ===============================
    def handle_bug_collision(self, bug_type):
        """Handle collision with different bug types"""
        if bug_type == "chat":
            self.game.audio.play('chatbug_hit')
        elif bug_type == "notif":
            self.game.audio.play('notifbug_hit')
            self.focus -= 10
        elif bug_type == "popup":
            self.game.audio.play('popupbug_hit')
            if self.question_cooldown <= 0:
                self.trigger_question()

    def collect_floworb(self):
        """Collect flow orb"""
        self.game.audio.play('floworb_collect')
        self.focus = min(100, self.focus + 20)
        self.player.score += 20
        self.focus_pulse = 1.5

    
    # ===============================
    # GAME OVER / LEVEL COMPLETE SCREENS
    # ===============================
    
    def draw_level_complete_screen(self, screen):
        # Overlay dengan efek gradien
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(HEIGHT):
            alpha = 180 - int(y * 0.1)
            color = (0, 0, 0, alpha)
            pygame.draw.line(overlay, color, (0, y), (WIDTH, y))
        screen.blit(overlay, (0, 0))
        
        # Background panel utama dengan efek neon
        panel_width = 600
        panel_height = 500
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = HEIGHT // 2 - panel_height // 2
        
        # Panel background dengan gradien
        panel_bg = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        for y in range(panel_height):
            alpha = 200 + int(55 * (y / panel_height))
            color = (20, 30, 50, alpha)
            pygame.draw.line(panel_bg, color, (0, y), (panel_width, y))
        
        # Border dengan efek neon hijau
        pygame.draw.rect(panel_bg, (100, 255, 100, 150), 
                        (0, 0, panel_width, panel_height), 4, border_radius=20)
        pygame.draw.rect(panel_bg, (200, 255, 200, 100), 
                        (2, 2, panel_width - 4, panel_height - 4), 2, border_radius=18)
        
        # Glow effect
        glow_surface = pygame.Surface((panel_width + 40, panel_height + 40), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (100, 255, 100, 50), 
                        (0, 0, glow_surface.get_width(), glow_surface.get_height()), 
                        border_radius=30)
        screen.blit(glow_surface, (panel_x - 20, panel_y - 20))
        
        screen.blit(panel_bg, (panel_x, panel_y))
        
        # Level complete title dengan efek animasi
        pulse = (math.sin(self.pulse_timer * 3) + 1) * 0.5
        title_color = (
            int(100 + 155 * pulse),
            int(255 - 55 * pulse),
            int(100 + 155 * pulse)
        )
        
        # Judul utama dengan shadow
        level_complete_text = self.big_font.render("LEVEL COMPLETE!", True, (255, 255, 255))
        level_complete_shadow = self.big_font.render("LEVEL COMPLETE!", True, (0, 0, 0, 100))
        
        screen.blit(level_complete_shadow, (WIDTH // 2 - level_complete_text.get_width() // 2 + 3, HEIGHT // 2 - 155 + 3))
        screen.blit(level_complete_text, (WIDTH // 2 - level_complete_text.get_width() // 2, HEIGHT // 2 - 155))
        
        # Subtitle
        subtitle = pygame.font.SysFont("arial", 24).render("Congratulations! You've protected your focus", True, (200, 255, 200))
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, HEIGHT // 2 - 100))
        
        # Achievement badge
        badge_size = 60
        badge_x = WIDTH // 2 - badge_size // 2
        badge_y = HEIGHT // 2 - 70
        
        # Badge dengan efek 3D
        badge_surface = pygame.Surface((badge_size, badge_size), pygame.SRCALPHA)
        pygame.draw.circle(badge_surface, (255, 215, 0), (badge_size//2, badge_size//2), badge_size//2)
        pygame.draw.circle(badge_surface, (255, 255, 150), (badge_size//2, badge_size//2), badge_size//2 - 5)
        pygame.draw.circle(badge_surface, (255, 200, 0), (badge_size//2, badge_size//2), badge_size//2 - 8)
        
        # Star icon
        star_points = []
        for i in range(5):
            angle = math.radians(72 * i - 90)
            outer_x = badge_size//2 + math.cos(angle) * (badge_size//2 - 12)
            outer_y = badge_size//2 + math.sin(angle) * (badge_size//2 - 12)
            star_points.append((outer_x, outer_y))
            
            inner_angle = angle + math.radians(36)
            inner_x = badge_size//2 + math.cos(inner_angle) * (badge_size//4)
            inner_y = badge_size//2 + math.sin(inner_angle) * (badge_size//4)
            star_points.append((inner_x, inner_y))
        
        pygame.draw.polygon(badge_surface, (255, 255, 255), star_points)
        screen.blit(badge_surface, (badge_x, badge_y))
        
        # Stats box dengan efek glassmorphism
        stats_width = 500
        stats_height = 120
        stats_x = WIDTH // 2 - stats_width // 2
        stats_y = HEIGHT // 2
        
        stats_bg = pygame.Surface((stats_width, stats_height), pygame.SRCALPHA)
        stats_bg.fill((255, 255, 255, 30))
        pygame.draw.rect(stats_bg, (255, 255, 255, 50), 
                        (0, 0, stats_width, stats_height), 2, border_radius=15)
        
        # Blur effect
        blur_overlay = pygame.Surface((stats_width, stats_height), pygame.SRCALPHA)
        blur_overlay.fill((255, 255, 255, 20))
        stats_bg.blit(blur_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        
        screen.blit(stats_bg, (stats_x, stats_y))
        
        # Final stats dengan layout grid
        stats_font = pygame.font.SysFont("arial", 22)
        
        score_text = stats_font.render(f"Score: {self.player.score}", True, (255, 255, 180))
        repels_text = stats_font.render(f"Bugs Repelled: {self.repels}", True, (180, 255, 180))
        level_text = stats_font.render(f"Level: {self.level_id}", True, (180, 180, 255))
        target_text = stats_font.render(f"Target: {self.target_score}", True, (255, 180, 180))
        
        # Layout 2x2 grid
        screen.blit(score_text, (stats_x + 40, stats_y + 20))
        screen.blit(repels_text, (stats_x + stats_width - repels_text.get_width() - 40, stats_y + 20))
        screen.blit(level_text, (stats_x + 40, stats_y + 70))
        screen.blit(target_text, (stats_x + stats_width - target_text.get_width() - 40, stats_y + 70))
        
        # Tombol dalam layout horizontal
        button_width = 180
        button_height = 60
        button_spacing = 40
        total_buttons_width = 2 * button_width + button_spacing
        buttons_start_x = WIDTH // 2 - total_buttons_width // 2
        buttons_y = HEIGHT // 2 + 140
        
        # Next Level button
        next_text = "NEXT LEVEL" if self.level_id < 3 else "FINISH GAME"
        next_color = (100, 255, 100) if self.level_complete_selection == 0 else (200, 230, 200)
        next_hover = self.check_mouse_hover(pygame.Rect(buttons_start_x, buttons_y, button_width, button_height))
        
        self.next_button = self.draw_button(screen, 
                                          buttons_start_x, 
                                          buttons_y, 
                                          button_width, 
                                          button_height,
                                          next_text, 
                                          next_color,
                                          hover=next_hover or self.level_complete_selection == 0)
        
        # Home button
        home_color = (100, 200, 255) if self.level_complete_selection == 1 else (200, 220, 230)
        home_hover = self.check_mouse_hover(pygame.Rect(buttons_start_x + button_width + button_spacing, buttons_y, button_width, button_height))
        
        self.home_button = self.draw_button(screen, 
                                          buttons_start_x + button_width + button_spacing, 
                                          buttons_y, 
                                          button_width, 
                                          button_height,
                                          "BACK TO HOME", 
                                          home_color,
                                          hover=home_hover or self.level_complete_selection == 1)

        
    
    def draw_game_over_screen(self, screen):
        # Overlay dengan efek gelap
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(HEIGHT):
            alpha = 200 - int(y * 0.08)
            color = (0, 0, 0, alpha)
            pygame.draw.line(overlay, color, (0, y), (WIDTH, y))
        screen.blit(overlay, (0, 0))
        
        # Background panel utama
        panel_width = 600
        panel_height = 500
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = HEIGHT // 2 - panel_height // 2
        
        # Panel background dengan gradien merah
        panel_bg = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        for y in range(panel_height):
            alpha = 200 + int(55 * (y / panel_height))
            color = (40, 20, 30, alpha)
            pygame.draw.line(panel_bg, color, (0, y), (panel_width, y))
        
        # Border dengan efek neon merah
        pygame.draw.rect(panel_bg, (255, 100, 100, 150), 
                        (0, 0, panel_width, panel_height), 4, border_radius=20)
        pygame.draw.rect(panel_bg, (255, 200, 200, 100), 
                        (2, 2, panel_width - 4, panel_height - 4), 2, border_radius=18)
        
        # Glow effect
        glow_surface = pygame.Surface((panel_width + 40, panel_height + 40), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (255, 100, 100, 50), 
                        (0, 0, glow_surface.get_width(), glow_surface.get_height()), 
                        border_radius=30)
        screen.blit(glow_surface, (panel_x - 20, panel_y - 20))
        
        screen.blit(panel_bg, (panel_x, panel_y))
        
        # Game over title dengan efek pulsating
        pulse = (math.sin(self.pulse_timer * 4) + 1) * 0.5
        title_color = (
            int(255 - 55 * pulse),
            int(100 + 155 * pulse),
            int(100 + 155 * pulse)
        )
        
        # Judul utama dengan shadow
        game_over_text = self.big_font.render("GAME OVER", True, (255, 255, 255))
        game_over_shadow = self.big_font.render("GAME OVER", True, (0, 0, 0, 100))
        
        screen.blit(game_over_shadow, (WIDTH // 2 - game_over_text.get_width() // 2 + 3, HEIGHT // 2 - 155 + 3))
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 155))
        
        # Subtitle
        subtitle = pygame.font.SysFont("arial", 24).render("Your focus has been overwhelmed by distractions", True, (255, 200, 200))
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, HEIGHT // 2 - 100))
        
        # Warning icon
        warning_size = 60
        warning_x = WIDTH // 2 - warning_size // 2
        warning_y = HEIGHT // 2 - 70
        
        # Warning triangle
        warning_surface = pygame.Surface((warning_size, warning_size), pygame.SRCALPHA)
        triangle_points = [
            (warning_size//2, 10),
            (warning_size - 10, warning_size - 10),
            (10, warning_size - 10)
        ]
        pygame.draw.polygon(warning_surface, (255, 100, 100), triangle_points)
        pygame.draw.polygon(warning_surface, (255, 200, 200), triangle_points, 3)
        
        # Exclamation mark
        pygame.draw.rect(warning_surface, (255, 255, 255), 
                        (warning_size//2 - 3, warning_size//2 - 15, 6, 20))
        pygame.draw.circle(warning_surface, (255, 255, 255), 
                          (warning_size//2, warning_size - 15), 4)
        
        screen.blit(warning_surface, (warning_x, warning_y))
        
        # Stats box
        stats_width = 500
        stats_height = 120
        stats_x = WIDTH // 2 - stats_width // 2
        stats_y = HEIGHT // 2
        
        stats_bg = pygame.Surface((stats_width, stats_height), pygame.SRCALPHA)
        stats_bg.fill((255, 255, 255, 30))
        pygame.draw.rect(stats_bg, (255, 255, 255, 50), 
                        (0, 0, stats_width, stats_height), 2, border_radius=15)
        
        # Blur effect
        blur_overlay = pygame.Surface((stats_width, stats_height), pygame.SRCALPHA)
        blur_overlay.fill((255, 255, 255, 20))
        stats_bg.blit(blur_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        
        screen.blit(stats_bg, (stats_x, stats_y))
        
        # Final stats
        stats_font = pygame.font.SysFont("arial", 22)
        
        score_text = stats_font.render(f"Score: {self.player.score}", True, (255, 255, 180))
        repels_text = stats_font.render(f"Bugs Repelled: {self.repels}", True, (180, 255, 180))
        level_text = stats_font.render(f"Level: {self.level_id}", True, (180, 180, 255))
        target_text = stats_font.render(f"Target: {self.target_score}", True, (255, 180, 180))
        
        # Layout 2x2 grid
        screen.blit(score_text, (stats_x + 40, stats_y + 20))
        screen.blit(repels_text, (stats_x + stats_width - repels_text.get_width() - 40, stats_y + 20))
        screen.blit(level_text, (stats_x + 40, stats_y + 70))
        screen.blit(target_text, (stats_x + stats_width - target_text.get_width() - 40, stats_y + 70))
        
        # Tombol dalam layout horizontal
        button_width = 180
        button_height = 60
        button_spacing = 40
        total_buttons_width = 2 * button_width + button_spacing
        buttons_start_x = WIDTH // 2 - total_buttons_width // 2
        buttons_y = HEIGHT // 2 + 140
        
        # Retry button
        retry_color = (100, 255, 100) if self.game_over_selection == 0 else (200, 230, 200)
        retry_hover = self.check_mouse_hover(pygame.Rect(buttons_start_x, buttons_y, button_width, button_height))
        
        self.retry_button = self.draw_button(screen, 
                                           buttons_start_x, 
                                           buttons_y, 
                                           button_width, 
                                           button_height,
                                           "RETRY LEVEL", 
                                           retry_color,
                                           hover=retry_hover or self.game_over_selection == 0)
        
        # Home button
        home_color = (100, 200, 255) if self.game_over_selection == 1 else (200, 220, 230)
        home_hover = self.check_mouse_hover(pygame.Rect(buttons_start_x + button_width + button_spacing, buttons_y, button_width, button_height))
        
        self.home_button = self.draw_button(screen, 
                                          buttons_start_x + button_width + button_spacing, 
                                          buttons_y, 
                                          button_width, 
                                          button_height,
                                          "BACK TO HOME", 
                                          home_color,
                                          hover=home_hover or self.game_over_selection == 1)
        
        # Selection indicator (untuk keyboard navigation)
        if self.game_over_selection == 0:
            self.draw_selection_indicator(screen, buttons_start_x - 40, buttons_y + button_height//2)
        else:
            self.draw_selection_indicator(screen, buttons_start_x + button_width + button_spacing - 40, buttons_y + button_height//2)
        
    
    def draw_button(self, screen, x, y, width, height, text, base_color, hover=False):
        """Draw a button with hover effects"""
        button_rect = pygame.Rect(x, y, width, height)
        
        # Button background dengan gradien
        button_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        if hover:
            # Hover effect - lebih terang
            for i in range(height):
                alpha = 200 + int(55 * (i / height))
                color = (
                    min(255, base_color[0] + 30),
                    min(255, base_color[1] + 30),
                    min(255, base_color[2] + 30),
                    alpha
                )
                pygame.draw.line(button_surface, color, (0, i), (width, i))
            
            # Border lebih terang
            pygame.draw.rect(button_surface, (255, 255, 255, 200), 
                            (0, 0, width, height), 3, border_radius=12)
            
            # Glow effect
            glow = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*base_color[:3], 50), 
                            (0, 0, glow.get_width(), glow.get_height()), 
                            border_radius=20)
            screen.blit(glow, (x - 10, y - 10))
        else:
            # Normal state
            for i in range(height):
                alpha = 200 + int(55 * (i / height))
                color = (*base_color[:3], alpha)
                pygame.draw.line(button_surface, color, (0, i), (width, i))
            
            # Border
            pygame.draw.rect(button_surface, (255, 255, 255, 150), 
                            (0, 0, width, height), 2, border_radius=12)
        
        # Inner shadow
        pygame.draw.rect(button_surface, (0, 0, 0, 30), 
                        (2, 2, width - 4, height - 4), border_radius=10)
        
        screen.blit(button_surface, (x, y))
        
        # Button text
        button_font = pygame.font.SysFont("arial", 20, bold=True)
        text_color = (255, 255, 255) if hover else (240, 240, 240)
        text_surface = button_font.render(text, True, text_color)
        
        # Text shadow
        shadow_surface = button_font.render(text, True, (0, 0, 0, 100))
        screen.blit(shadow_surface, (x + width//2 - text_surface.get_width()//2 + 1, y + height//2 - text_surface.get_height()//2 + 1))
        
        screen.blit(text_surface, (x + width//2 - text_surface.get_width()//2, y + height//2 - text_surface.get_height()//2))
        
        return button_rect
    
    def draw_selection_indicator(self, screen, x, y):
        """Draw selection indicator arrow"""
        pygame.draw.polygon(screen, (255, 255, 255), [
            (x, y),
            (x + 20, y - 10),
            (x + 20, y + 10)
        ])
    
    def check_mouse_hover(self, rect):
        """Check if mouse is hovering over a rectangle"""
        mouse_pos = pygame.mouse.get_pos()
        return rect.collidepoint(mouse_pos)
                
    # ===============================
    # PUBLIC API (FOR HUD)
    # ===============================
    def get_focus_level(self):
        return max(0, min(100, int(self.focus)))