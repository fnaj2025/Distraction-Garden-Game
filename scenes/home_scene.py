import pygame, math
import random  
from scenes.base_scene import BaseScene

class HomeScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("bahnschrift", 72, bold=True, italic=True)
        self.menu_font = pygame.font.SysFont("segoeui", 36, bold=True)
        self.small = pygame.font.SysFont("segoeui", 24, bold=True, italic=True)
        self.hint_font = pygame.font.SysFont("consolas", 16, bold=True)

        self.menu = [
            ("Start Game", self.start_game),
            ("Select Level", self.select_level),
            ("Exit", self.exit_game)
        ]
        self.selected = 0
        
        # Animation variables
        self.animation_timer = 0
        self.bg_particles = []
        self.init_background()
        
        # Menu item rectangles for click detection
        self.menu_rects = []
        self.calculate_menu_rects()
        
        # Audio state
        self.last_hover_index = -1
    
    def init_background(self):
        """Initialize background particles"""
        for _ in range(30):
            self.bg_particles.append({
                'x': random.randint(0, self.game.width),
                'y': random.randint(0, self.game.height),
                'size': random.randint(2, 6),
                'speed': random.uniform(0.2, 0.5),
                'color': random.choice([
                    (100, 200, 255, 100),
                    (120, 220, 120, 100),
                    (255, 220, 100, 100),
                    (220, 120, 220, 100)
                ]),
                'wobble': random.uniform(0, math.pi * 2),
                'direction': random.uniform(0, math.pi * 2)
            })
    
    def calculate_menu_rects(self):
        """Calculate clickable areas for each menu item"""
        self.menu_rects = []
        y = 240
        for i, (text, _) in enumerate(self.menu):
            text_width = self.menu_font.size("> " + text)[0]
            rect = pygame.Rect(
                self.game.width // 2 - text_width // 2 - 20,
                y - 8,
                text_width + 20,
                40
            )
            self.menu_rects.append(rect)
            y += 50

    def handle_event(self, event):
        # Keyboard navigation
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.menu)
                self.game.audio.play('menu_select')
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.menu)
                self.game.audio.play('menu_select')
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.game.audio.play('button_click')
                self.menu[self.selected][1]()
            elif event.key == pygame.K_ESCAPE:
                self.game.audio.play('button_click')
                self.exit_game()
        
        # Mouse hover - update selection
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            for i, rect in enumerate(self.menu_rects):
                if rect.collidepoint(mouse_pos):
                    if self.selected != i:
                        self.game.audio.play('hover')
                        self.selected = i
                        self.last_hover_index = i 
                    break
            else:
                self.last_hover_index = -1  
            
        # Mouse click - execute selected menu
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for i, rect in enumerate(self.menu_rects):
                if rect.collidepoint(mouse_pos):
                    self.game.audio.play('button_click')
                    self.selected = i
                    # Execute the menu action
                    self.menu[i][1]()
                    break
    
    def update(self, dt):
        # Update animation timer
        self.animation_timer += dt
        self.title_glow = (math.sin(self.animation_timer) + 1) / 2
        
        # Update background particles
        for particle in self.bg_particles:
            particle['wobble'] += dt * 2
            particle['x'] += math.cos(particle['direction']) * particle['speed']
            particle['y'] += math.sin(particle['direction']) * particle['speed']
            
            # Wrap around screen
            if particle['x'] < -20:
                particle['x'] = self.game.width + 20
            elif particle['x'] > self.game.width + 20:
                particle['x'] = -20
            if particle['y'] < -20:
                particle['y'] = self.game.height + 20
            elif particle['y'] > self.game.height + 20:
                particle['y'] = -20

    def start_game(self):
        from scenes.game_scene import GameScene
        self.game.change_scene(GameScene(self.game, level_id=1))

    def select_level(self):
        from scenes.level_select_scene import LevelSelectScene
        self.game.change_scene(LevelSelectScene(self.game))

    def exit_game(self):
        pygame.quit()
        quit()

    def render(self, screen):
        # Gradient background
        self.draw_gradient_background(screen)
        
        # Background particles
        for particle in self.bg_particles:
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), 
                                            pygame.SRCALPHA)
            alpha = 80 + int(40 * math.sin(particle['wobble']))
            color = (*particle['color'][:3], alpha)
            pygame.draw.circle(particle_surface, color, 
                             (particle['size'], particle['size']), particle['size'])
            screen.blit(particle_surface, 
                       (int(particle['x']), int(particle['y'])))
        
        # Title with glow effect
        self.draw_title(screen)
        
        # Subtitle
        subtitle = self.small.render("Protect Your Mind Garden", True, (200, 200, 220))
        screen.blit(subtitle, (self.game.width // 2 - subtitle.get_width() // 2, 160))
    
        # Menu items
        self.draw_menu(screen)
        
        # Version/copyright
        version = self.hint_font.render("© 2025 Distraction Garden v1.0", 
                                       True, (120, 120, 140))
        screen.blit(version, (self.game.width // 2 - version.get_width() // 2, 
                            self.game.height - 30))
    
    def draw_gradient_background(self, screen):
        """Draw gradient background"""
        for y in range(self.game.height):
            # Vertical gradient from dark to light
            r = int(20 + 10 * (y / self.game.height))
            g = int(30 + 15 * (y / self.game.height))
            b = int(40 + 20 * (y / self.game.height))
            pygame.draw.line(screen, (r, g, b), (0, y), (self.game.width, y))
        
        # Add some stars/particles in the "sky"
        for _ in range(20):
            x = random.randint(0, self.game.width)
            y = random.randint(0, 100)
            size = random.randint(1, 3)
            brightness = random.randint(150, 255)
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)
    
    # Versi sederhana tanpa glow untuk testing
    def draw_title(self, screen):
        """Draw animated title - SIMPLE VERSION FOR DEBUGGING"""
        title_text = "DISTRACTION GARDEN"
        
        # Hanya render teks utama tanpa glow
        title_color = (180, 220, 255)
        title = self.font.render(title_text, True, title_color)
        title_x = self.game.width // 2 - title.get_width() // 2
        title_y = 80
        
        screen.blit(title, (title_x, title_y))
                
        # Animated underline
        underline_width = title.get_width() + 40
        underline_x = self.game.width // 2 - underline_width // 2
        underline_y = title_y + title.get_height() + 5
        
        # Animated dots
        dot_spacing = 10
        for i in range(0, underline_width, dot_spacing):
            dot_x = underline_x + i
            dot_phase = (i / dot_spacing + self.animation_timer * 2) % 3
            dot_size = 2 if dot_phase < 1 else 4 if dot_phase < 2 else 2
            dot_color = (100, 200, 255) if dot_phase < 2 else (255, 255, 255)
            pygame.draw.circle(screen, dot_color, (int(dot_x), underline_y), dot_size)
    
    def draw_menu(self, screen):
        """Draw animated menu items"""
        y = 240
        
        for i, (text, _) in enumerate(self.menu):
            is_selected = (i == self.selected)
            is_hovered = self.menu_rects[i].collidepoint(pygame.mouse.get_pos())
            
            # Calculate animation values
            if is_selected or is_hovered:
                scale = 1.1
                pulse = 1 + 0.1 * math.sin(self.animation_timer * 3)
                color_intensity = 255
            else:
                scale = 1.0
                pulse = 1.0
                color_intensity = 200
            
            # Menu item background
            rect = self.menu_rects[i].copy()
            rect.width = int(rect.width * scale)
            rect.height = int(rect.height * scale)
            rect.center = self.menu_rects[i].center
            
            # Background with animation
            bg_color = (30, 40, 60, 150) if not is_selected else (40, 60, 80, 200)
            pygame.draw.rect(screen, bg_color, rect, border_radius=8)
            
            # Border with pulse effect
            if is_selected:
                border_color = (100, 200, 255)
                border_width = 2 + int(2 * pulse)
            elif is_hovered:
                border_color = (200, 200, 255)
                border_width = 2
            else:
                border_color = (80, 100, 120)
                border_width = 1
            
            pygame.draw.rect(screen, border_color, rect, border_width, border_radius=8)
            
            # Selection indicator
            if is_selected:
                # Animated triangle indicator
                indicator_size = 8
                indicator_x = rect.left - 15
                indicator_y = rect.centery
                
                points = [
                    (indicator_x, indicator_y),
                    (indicator_x + indicator_size, indicator_y - indicator_size),
                    (indicator_x + indicator_size, indicator_y + indicator_size)
                ]
                
                indicator_color = (100, 200, 255)
                pygame.draw.polygon(screen, indicator_color, points)
                
                # Pulsing dot
                dot_size = 3 + int(2 * pulse)
                pygame.draw.circle(screen, (255, 255, 255), 
                                 (indicator_x + 2, indicator_y), dot_size)
            
            # Menu text
            if is_selected:
                text_color = (255, 255, 200)
                prefix = "› "
            else:
                text_color = (color_intensity, color_intensity, color_intensity)
                prefix = "  "
            
            menu_text = self.menu_font.render(prefix + text, True, text_color)
            text_x = rect.centerx - menu_text.get_width() // 2
            text_y = rect.centery - menu_text.get_height() // 2
            
            # Text shadow for better readability
            shadow = self.menu_font.render(prefix + text, True, (0, 0, 0, 100))
            screen.blit(shadow, (text_x + 1, text_y + 1))
            screen.blit(menu_text, (text_x, text_y))

            y += 50