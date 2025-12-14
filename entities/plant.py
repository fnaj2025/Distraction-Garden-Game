# entities/plant.py
import pygame, math, random
from .entity import Entity

class Plant(Entity):
    """
    Focus Blossom - grows through attention and can be damaged by bugs.
    Levels: 0 (seed) -> 1 -> 2 -> 3 (bloom)
    """
    def __init__(self, x, y):
        super().__init__(x, y, 28, 44)
        self.level = 1
        self.growth = 0.0
        self.max_growth = 100.0
        self.health = 100.0  # if 0 -> destroyed
        self.animation_timer = 0
        self.level_up_timer = 0
        self.wobble_offset = random.uniform(0, math.pi * 2)
        self.particles = []

    def update(self, dt, game):
        self.animation_timer += dt
        self.level_up_timer = max(0, self.level_up_timer - dt)
        
        # natural slow growth determined by game focus
        focus_boost = max(0, (game.get_focus_level() - 40)/60.0)
        self.growth += 2.0 * (1 + focus_boost) * dt
        
        if self.growth >= self.max_growth:
            self.growth = 0
            if self.level < 3:
                self.level += 1
                self.level_up_timer = 1.0  # Trigger level up animation
                game.player.score += 5  # reward for plant leveling
                # Spawn level up particles
                game.spawn_particles(self, kind="leaf", count=15)
        
        # if health low, degrade level
        if self.health <= 0:
            self.destroy()

    def draw(self, surface):
        x, y = self.rect.center
        
        # Wobble animation
        wobble = math.sin(self.animation_timer * 1.5 + self.wobble_offset) * 0.1
        
        # Level up pulse effect
        if self.level_up_timer > 0:
            pulse_radius = int(40 * self.level_up_timer)
            pulse_surface = pygame.Surface((pulse_radius * 2, pulse_radius * 2), pygame.SRCALPHA)
            pulse_color = (100, 255, 100, int(150 * self.level_up_timer))
            pygame.draw.circle(pulse_surface, pulse_color, 
                             (pulse_radius, pulse_radius), pulse_radius)
            surface.blit(pulse_surface, (x - pulse_radius, y - pulse_radius))
        
        # Growth progress circle
        if self.level < 3:
            progress = self.growth / self.max_growth
            angle = progress * math.pi * 2
            pygame.draw.arc(surface, (100, 180, 100), 
                          (x - 25, y - 25, 50, 50), 0, angle, 3)
        
        # Health indicator
        health_percent = self.health / 100.0
        if health_percent < 0.7:
            health_color = (255, int(255 * health_percent), 0)
            health_width = 2
            health_rect = pygame.Rect(x - 20, y + 25, 40 * health_percent, 3)
            pygame.draw.rect(surface, health_color, health_rect)
        
        # stem with animation
        stem_length = 18 + math.sin(self.animation_timer) * 2
        pygame.draw.line(surface, (70, 120, 60), 
                        (x, y + stem_length), (x, y + 6), 3)
        
        # leaves depend on level with animation
        leaf_pulse = 1 + 0.1 * math.sin(self.animation_timer * 2)
        
        if self.level >= 1:
            leaf_scale = 1 + wobble * 0.5
            leaf_rect = pygame.Rect(x - 12 * leaf_scale, y + 2, 
                                  18 * leaf_scale, 10 * leaf_scale)
            pygame.draw.ellipse(surface, (86, 146, 92), leaf_rect)
            
            # Leaf veins
            pygame.draw.line(surface, (60, 110, 70), 
                           (x - 3, y + 7), (x - 9, y + 4), 1)
            pygame.draw.line(surface, (60, 110, 70), 
                           (x - 3, y + 7), (x + 2, y + 6), 1)
        
        if self.level >= 2:
            leaf_scale = 1 + wobble * 0.3
            leaf_rect = pygame.Rect(x - 2, y - 4 * leaf_scale, 
                                  20 * leaf_scale, 12 * leaf_scale)
            pygame.draw.ellipse(surface, (102, 170, 110), leaf_rect)
            
            # Leaf veins
            pygame.draw.line(surface, (80, 140, 90), 
                           (x + 8, y - 2), (x + 2, y - 1), 1)
            pygame.draw.line(surface, (80, 140, 90), 
                           (x + 8, y - 2), (x + 10, y + 2), 1)
        
        if self.level >= 3:
            # bloom with animation
            bloom_size = 8 + math.sin(self.animation_timer * 3) * 2
            bloom_pulse = 1 + 0.2 * math.sin(self.animation_timer * 1.5)
            
            # Petals
            petal_colors = [(250, 220, 110), (255, 200, 100), (245, 230, 120)]
            for i in range(6):
                angle = self.animation_timer + i * math.pi / 3
                petal_x = x + math.cos(angle) * bloom_size * 0.8
                petal_y = y - 12 + math.sin(angle) * bloom_size * 0.8
                pygame.draw.circle(surface, petal_colors[i % 3], 
                                 (int(petal_x), int(petal_y)), 
                                 int(bloom_size * 0.6 * bloom_pulse))
            
            # Center with pulse
            center_size = bloom_size * 0.4 * bloom_pulse
            pygame.draw.circle(surface, (255, 150, 100), (x, y - 12), 
                             int(center_size))
            
            # Stamen
            for i in range(4):
                angle = self.animation_timer * 2 + i * math.pi / 2
                stamen_x = x + math.cos(angle) * center_size * 0.7
                stamen_y = y - 12 + math.sin(angle) * center_size * 0.7
                pygame.draw.line(surface, (255, 200, 50), 
                               (x, y - 12), (stamen_x, stamen_y), 2)
            
            # Sparkles
            if math.sin(self.animation_timer * 4) > 0.9:
                sparkle_x = x + math.cos(self.animation_timer * 5) * 15
                sparkle_y = y - 12 + math.sin(self.animation_timer * 5) * 15
                pygame.draw.circle(surface, (255, 255, 200, 200), 
                                 (int(sparkle_x), int(sparkle_y)), 2)

    def damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.destroy()