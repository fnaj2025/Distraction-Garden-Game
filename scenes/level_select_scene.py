import pygame
import random  
import math
from scenes.base_scene import BaseScene

LEVELS = [
    (1, "Notification Overload", "Basic distractions", (100, 200, 255)),
    (2, "Multitasking Trap", "Multiple distractions", (255, 200, 100)),
    (3, "Burnout Phase", "Intense pressure", (255, 100, 100))
]

class LevelSelectScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("arial", 32, bold=True)
        self.level_font = pygame.font.SysFont("arial", 24)
        self.desc_font = pygame.font.SysFont("arial", 18)
        self.small = pygame.font.SysFont("arial", 16)
        
        self.selected = 0
        self.animation_timer = 0
        
        # Posisi antar level
        self.level_start_y = 160  
        self.level_spacing = 90   
        self.preview_x = 720      

        # Level item rectangles for click detection
        self.level_rects = []
        self.calculate_level_rects()
        
        # Back button
        self.back_rect = pygame.Rect(50, 500, 120, 40)
        
        # Preview elements
        self.preview_bugs = []
        self.init_preview()
        
        # Audio state
        self.last_hover_index = -1
        
    def init_preview(self):
        """Initialize preview animations"""
        for _ in range(5):
            self.preview_bugs.append({
                'x': random.randint(200, 800),
                'y': random.randint(100, 400),
                'size': random.randint(10, 20),
                'speed': random.uniform(1, 3),
                'color': random.choice([
                    (220, 70, 70),    # Red bug
                    (255, 150, 100),  # Orange bug
                    (255, 200, 100)   # Yellow bug
                ]),
                'direction': random.uniform(0, math.pi * 2),
                'wobble': random.uniform(0, math.pi * 2)
            })

    def calculate_level_rects(self):
        """Calculate clickable areas for each level"""
        self.level_rects = []
        y = self.level_start_y
        for i in range(len(LEVELS)):
            rect = pygame.Rect(100, y - 10, 400, 65)  # Lebar dikurangi
            self.level_rects.append(rect)
            y += self.level_spacing

    def handle_event(self, event):
        # Keyboard navigation
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(LEVELS)
                self.game.audio.play('menu_select')
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(LEVELS)
                self.game.audio.play('menu_select')
            elif event.key == pygame.K_RETURN:
                self.game.audio.play('button_click')
                from scenes.game_scene import GameScene
                level_id = LEVELS[self.selected][0]
                self.game.change_scene(GameScene(self.game, level_id))
            elif event.key == pygame.K_ESCAPE:
                self.game.audio.play('button_click')
                from scenes.home_scene import HomeScene
                self.game.change_scene(HomeScene(self.game))
        
        # Mouse hover
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            # Check level hover
            for i, rect in enumerate(self.level_rects):
                if rect.collidepoint(mouse_pos):
                    if self.selected != i:
                        self.game.audio.play('hover')
                        self.selected = i
                        self.last_hover_index = i 
                    break
            else:
                self.last_hover_index = -1  
        
        # Mouse click
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Check level click
            for i, rect in enumerate(self.level_rects):
                if rect.collidepoint(mouse_pos):
                    self.game.audio.play('button_click')
                    from scenes.game_scene import GameScene
                    level_id = LEVELS[i][0]
                    self.game.change_scene(GameScene(self.game, level_id))
                    return
            
           # Check back button click
            if self.back_rect.collidepoint(mouse_pos):
                self.game.audio.play('button_click')
                from scenes.home_scene import HomeScene
                self.game.change_scene(HomeScene(self.game))
    
    def update(self, dt):
        # Update animation timer
        self.animation_timer += dt
        
        # Update preview bugs
        for bug in self.preview_bugs:
            bug['wobble'] += dt * 3
            bug['x'] += math.cos(bug['direction']) * bug['speed']
            bug['y'] += math.sin(bug['direction']) * bug['speed'] * 0.5
            
            # Bounce off edges
            if bug['x'] < 100 or bug['x'] > 900:
                bug['direction'] = math.pi - bug['direction']
            if bug['y'] < 80 or bug['y'] > 500:
                bug['direction'] = -bug['direction']
            
            # Add some wobble
            bug['x'] += math.sin(bug['wobble']) * 2

    def render(self, screen):
        # Gradient background
        self.draw_gradient_background(screen)
        
        # Preview bugs (tetap di background)
        for bug in self.preview_bugs:
            # Bug body
            pygame.draw.circle(screen, bug['color'], 
                             (int(bug['x']), int(bug['y'])), bug['size'])
            
            # Bug eyes
            eye_offset = bug['size'] * 0.4
            pygame.draw.circle(screen, (30, 30, 30), 
                             (int(bug['x'] - eye_offset), int(bug['y'] - eye_offset)), 2)
            pygame.draw.circle(screen, (30, 30, 30), 
                             (int(bug['x'] + eye_offset), int(bug['y'] - eye_offset)), 2)
            
            # Bug legs
            for leg in range(3):
                angle = math.radians(30 + leg * 60) + bug['wobble']
                leg_length = bug['size'] * 1.2
                leg_x = bug['x'] + math.cos(angle) * bug['size']
                leg_y = bug['y'] + math.sin(angle) * bug['size']
                leg_end_x = leg_x + math.cos(angle) * leg_length
                leg_end_y = leg_y + math.sin(angle) * leg_length
                pygame.draw.line(screen, bug['color'], 
                               (leg_x, leg_y), (leg_end_x, leg_end_y), 2)
        
        # Title (lebih besar dan di tengah)
        self.draw_title(screen)

        # Level items
        y = self.level_start_y
        for i, (level_id, name, description, color) in enumerate(LEVELS):
            self.draw_level_item(screen, i, level_id, name, description, color, y)
            y += self.level_spacing
        
        # Back button
        self.draw_back_button(screen)
        
        # Selected level preview - dipindah ke kanan
        self.draw_selected_preview(screen)

    def draw_gradient_background(self, screen):
        """Draw gradient background based on selected level"""
        selected_color = LEVELS[self.selected][3]
        
        for y in range(self.game.height):
            # Interpolate between dark blue and selected level color
            ratio = y / self.game.height
            r = int(20 + (selected_color[0] - 20) * ratio * 0.3)
            g = int(30 + (selected_color[1] - 30) * ratio * 0.3)
            b = int(40 + (selected_color[2] - 40) * ratio * 0.3)
            pygame.draw.line(screen, (r, g, b), (0, y), (self.game.width, y))
        
        # Add subtle grid pattern
        grid_size = 40
        for x in range(0, self.game.width, grid_size):
            for y in range(0, self.game.height, grid_size):
                alpha = 10 + int(5 * math.sin(x * 0.01 + y * 0.01 + self.animation_timer))
                grid_surface = pygame.Surface((1, 1), pygame.SRCALPHA)
                grid_surface.fill((255, 255, 255, alpha))
                screen.blit(grid_surface, (x, y))

    def draw_title(self, screen):
        """Draw animated title"""
        title_text = "SELECT YOUR CHALLENGE"
        
        # Title dengan ukuran yang sesuai
        title_color = (180, 220, 255)
        title = self.font.render(title_text, True, title_color)
        title_x = self.game.width // 2 - title.get_width() // 2
        title_y = 60  # Lebih ke atas
        
        # Title background yang lebih sederhana
        title_bg = pygame.Surface((title.get_width() + 30, title.get_height() + 15), 
                                 pygame.SRCALPHA)
        title_bg.fill((0, 0, 0, 80))
        pygame.draw.rect(title_bg, (255, 255, 255, 20), 
                        (0, 0, title_bg.get_width(), title_bg.get_height()), 
                        2, border_radius=5)
        screen.blit(title_bg, (title_x - 15, title_y - 7))
        
        screen.blit(title, (title_x, title_y))

    def draw_level_item(self, screen, index, level_id, name, description, color, y):
        """Draw a single level selection item"""
        is_selected = (index == self.selected)
        is_hovered = self.level_rects[index].collidepoint(pygame.mouse.get_pos())
        
        rect = self.level_rects[index]
        
        # Animation values
        if is_selected:
            scale = 1.02
            pulse = 1 + 0.1 * math.sin(self.animation_timer * 3)
            bg_alpha = 200
        elif is_hovered:
            scale = 1.01
            pulse = 1.0
            bg_alpha = 150
        else:
            scale = 1.0
            pulse = 1.0
            bg_alpha = 100
        
        # Apply scale
        scaled_rect = rect.copy()
        scaled_rect.width = int(rect.width * scale)
        scaled_rect.height = int(rect.height * scale)
        scaled_rect.center = rect.center
        
        # Level card background
        card_surface = pygame.Surface((scaled_rect.width, scaled_rect.height), 
                                     pygame.SRCALPHA)
        
        # Card gradient
        for i in range(scaled_rect.height):
            shade = int(30 * (i / scaled_rect.height))
            row_color = (
                min(255, color[0] // 4 + shade),
                min(255, color[1] // 4 + shade),
                min(255, color[2] // 4 + shade),
                bg_alpha
            )
            pygame.draw.line(card_surface, row_color, 
                           (0, i), (scaled_rect.width, i))
        
        # Card border
        border_color = color if is_selected else (color[0]//2, color[1]//2, color[2]//2)
        border_width = 3 if is_selected else 2
        
        if is_selected:
            border_width += int(1 * pulse)  # Pulse lebih kecil
        
        pygame.draw.rect(card_surface, border_color, 
                        (0, 0, scaled_rect.width, scaled_rect.height), 
                        border_width, border_radius=10)
        
        screen.blit(card_surface, scaled_rect)
        
        # Level number badge - lebih kecil
        badge_size = 40
        badge_x = scaled_rect.x + 30
        badge_y = scaled_rect.centery
        
        # Animated badge for selected level
        if is_selected:
            badge_scale = 1 + 0.05 * pulse  # Scale lebih kecil
            badge_color = (255, 255, 255)
            badge_bg_color = color
        else:
            badge_scale = 1.0
            badge_color = (200, 200, 200)
            badge_bg_color = (color[0]//2, color[1]//2, color[2]//2)
        
        badge_rect = pygame.Rect(
            badge_x - int(badge_size * badge_scale // 2),
            badge_y - int(badge_size * badge_scale // 2),
            int(badge_size * badge_scale),
            int(badge_size * badge_scale)
        )
        
        pygame.draw.rect(screen, badge_bg_color, badge_rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255, 100), badge_rect, 2, border_radius=8)
        
        # Level number text
        level_text = self.desc_font.render(str(level_id), True, badge_color)
        screen.blit(level_text, (badge_x - level_text.get_width() // 2, 
                               badge_y - level_text.get_height() // 2))
        
        # Level name
        name_x = badge_x + 45  # Lebih dekat ke badge
        name_color = (255, 255, 255) if is_selected else (220, 220, 220)
        name_text = self.level_font.render(name, True, name_color)
        screen.blit(name_text, (name_x, badge_y - 20))
        
        # Level description
        desc_color = (180, 180, 200) if is_selected else (150, 150, 170)
        desc_text = self.small.render(description, True, desc_color)
        screen.blit(desc_text, (name_x, badge_y + 5))  # Diperbaiki: spacing yang lebih baik

    def draw_back_button(self, screen):
        """Draw animated back button"""
        mouse_pos = pygame.mouse.get_pos()
        back_hover = self.back_rect.collidepoint(mouse_pos)
        
        # Button animation
        if back_hover:
            scale = 1.05
            color = (120, 200, 180)
            pulse = 1 + 0.1 * math.sin(self.animation_timer * 4)
        else:
            scale = 1.0
            color = (80, 120, 100)
            pulse = 1.0
        
        # Scaled button rect
        scaled_rect = self.back_rect.copy()
        scaled_rect.width = int(self.back_rect.width * scale)
        scaled_rect.height = int(self.back_rect.height * scale)
        scaled_rect.center = self.back_rect.center
        
        # Button with gradient
        button_surface = pygame.Surface((scaled_rect.width, scaled_rect.height), 
                                       pygame.SRCALPHA)
        
        for i in range(scaled_rect.height):
            shade = int(30 * (i / scaled_rect.height))
            row_color = (
                min(255, color[0] + shade),
                min(255, color[1] + shade),
                min(255, color[2] + shade)
            )
            pygame.draw.line(button_surface, row_color, 
                           (0, i), (scaled_rect.width, i))
        
        # Button border
        border_width = 2 + int(1 * pulse) if back_hover else 2
        border_color = (200, 255, 220) if back_hover else (120, 180, 150)
        pygame.draw.rect(button_surface, border_color, 
                        (0, 0, scaled_rect.width, scaled_rect.height), 
                        border_width, border_radius=6)
        
        screen.blit(button_surface, scaled_rect)
        
        # Button text
        back_text = self.desc_font.render("← Back", True, (255, 255, 255))
        screen.blit(back_text, (scaled_rect.x + 20, scaled_rect.y + 12))

    def draw_selected_preview(self, screen):
        """Draw preview of selected level"""
        level_id, name, description, color = LEVELS[self.selected]
        
        # Preview panel - lebih kecil dan di posisi yang tepat
        preview_rect = pygame.Rect(self.preview_x, 150, 250, 220)
        preview_surface = pygame.Surface((preview_rect.width, preview_rect.height), 
                                        pygame.SRCALPHA)
        
        # Panel background
        pygame.draw.rect(preview_surface, (0, 0, 0, 150), 
                        (0, 0, preview_rect.width, preview_rect.height), 
                        border_radius=10)
        pygame.draw.rect(preview_surface, (255, 255, 255, 40), 
                        (0, 0, preview_rect.width, preview_rect.height), 
                        2, border_radius=10)
        
        screen.blit(preview_surface, preview_rect)
        
        # Preview title
        preview_title = self.desc_font.render("LEVEL FEATURES", True, (255, 255, 200))
        screen.blit(preview_title, (preview_rect.x + 20, preview_rect.y + 15))
        
        # Level features
        features = self.get_level_features(level_id)
        feature_y = preview_rect.y + 45
        
        for feature in features:
            feature_text = self.small.render(f"• {feature}", True, (220, 220, 220))
            screen.blit(feature_text, (preview_rect.x + 30, feature_y))
            feature_y += 22
        
        # Separator line
        pygame.draw.line(screen, (100, 100, 100, 100), 
                        (preview_rect.x + 20, feature_y + 5),
                        (preview_rect.right - 20, feature_y + 5), 1)
        
        # Stats
        time_limit = self.get_time_limit(level_id)
        time_y = feature_y + 15
        
        time_text = self.small.render(f"Time: {time_limit}s per Q", True, (200, 200, 255))
        screen.blit(time_text, (preview_rect.x + 30, time_y))
        
        drain_rate = 4 + level_id * 2
        drain_y = time_y + 20
        
        drain_text = self.small.render(f"Focus drain: {drain_rate}/s", True, (255, 200, 200))
        screen.blit(drain_text, (preview_rect.x + 30, drain_y))

    def get_level_features(self, level_id):
        """Get features description for each level"""
        features = {
            1: ["Basic notifications", "Slow bug spawn", "Easy questions"],
            2: ["Multiple distractions", "Faster bugs", "Medium questions"],
            3: ["Intense pressure", "Rapid spawn", "Hard questions"]
        }
        return features.get(level_id, [])

    def get_time_limit(self, level_id):
        """Get time limit for level"""
        limits = {1: 10, 2: 8, 3: 6}
        return limits.get(level_id, 5)