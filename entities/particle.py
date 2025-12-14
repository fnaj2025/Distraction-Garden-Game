# entities/particle.py
import pygame, random, math
from .entity import Entity

class Particle(Entity):
    def __init__(self, x, y, kind="spark"):
        super().__init__(x, y, 4, 4)
        self.vx = random.uniform(-120, 120)
        self.vy = random.uniform(-160, -40)
        self.life = random.uniform(0.4, 1.1)
        self.age = 0.0
        self.kind = kind
        self.rotation = random.uniform(0, math.pi * 2)
        self.rotation_speed = random.uniform(-5, 5)
        
        # Set color and size based on kind
        if kind == "spark":
            self.color = (255, 210, 100)
            self.size = random.randint(3, 6)
            self.glow = True
        elif kind == "leaf":
            self.color = (100, 180, 100)
            self.size = random.randint(4, 8)
            self.glow = False
        elif kind == "pop":
            self.color = (220, 100, 100)
            self.size = random.randint(2, 5)
            self.glow = True
        elif kind == "flow":
            self.color = (100, 200, 255)
            self.size = random.randint(4, 7)
            self.glow = True
        else:
            self.color = (220, 220, 220)
            self.size = random.randint(2, 4)
            self.glow = False
        
        self.rect = pygame.Rect(0, 0, self.size * 2, self.size * 2)
        self.rect.center = (x, y)

    def update(self, dt, game):
        self.age += dt
        self.rotation += self.rotation_speed * dt
        
        if self.age >= self.life:
            self.destroy()
            return
        
        # Physics
        self.vy += 300 * dt
        self.vx *= 0.99  # Air resistance
        self.vy *= 0.99
        
        self.rect.x += int(self.vx * dt)
        self.rect.y += int(self.vy * dt)
        
        # Wobble effect
        if self.kind == "leaf":
            self.rect.x += math.sin(self.age * 5) * 2

    def draw(self, surface):
        x, y = self.rect.center
        
        # Calculate alpha based on remaining life
        life_ratio = 1 - (self.age / self.life)
        alpha = int(255 * life_ratio)
        
        # Create particle surface
        particle_size = int(self.size * (0.5 + 0.5 * life_ratio))
        
        if self.glow:
            # Draw glow effect
            glow_size = particle_size * 2
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            
            # Outer glow
            for i in range(3, 0, -1):
                glow_alpha = int(alpha * 0.3 / i)
                glow_color = (*self.color[:3], glow_alpha)
                pygame.draw.circle(glow_surface, glow_color, 
                                 (glow_size, glow_size), 
                                 particle_size + i)
            
            surface.blit(glow_surface, (x - glow_size, y - glow_size))
        
        # Draw particle
        if self.kind == "spark" or self.kind == "pop":
            # Sparkle/star shape
            particle_surface = pygame.Surface((particle_size * 2, particle_size * 2), 
                                            pygame.SRCALPHA)
            
            # Star points
            points = []
            for i in range(5):
                angle = self.rotation + i * math.pi * 2 / 5
                radius = particle_size if i % 2 == 0 else particle_size * 0.5
                px = particle_size + math.cos(angle) * radius
                py = particle_size + math.sin(angle) * radius
                points.append((px, py))
            
            pygame.draw.polygon(particle_surface, (*self.color[:3], alpha), points)
            surface.blit(particle_surface, (x - particle_size, y - particle_size))
            
        elif self.kind == "leaf":
            # Leaf shape
            leaf_surface = pygame.Surface((particle_size * 3, particle_size * 2), 
                                         pygame.SRCALPHA)
            
            # Leaf polygon
            leaf_points = [
                (particle_size * 1.5, particle_size),
                (particle_size * 0.5, particle_size * 0.3),
                (particle_size * 0.8, particle_size * 1.7),
                (particle_size * 2.2, particle_size * 1.7),
                (particle_size * 2.5, particle_size * 0.3)
            ]
            
            # Apply rotation
            rotated_points = []
            for px, py in leaf_points:
                cos_a = math.cos(self.rotation)
                sin_a = math.sin(self.rotation)
                rx = (px - particle_size * 1.5) * cos_a - (py - particle_size) * sin_a
                ry = (px - particle_size * 1.5) * sin_a + (py - particle_size) * cos_a
                rotated_points.append((rx + particle_size * 1.5, ry + particle_size))
            
            pygame.draw.polygon(leaf_surface, (*self.color[:3], alpha), rotated_points)
            
            # Leaf vein
            vein_color = (70, 130, 70, alpha)
            vein_start = (particle_size * 1.5, particle_size * 0.5)
            vein_end = (particle_size * 1.5, particle_size * 1.5)
            pygame.draw.line(leaf_surface, vein_color, vein_start, vein_end, 1)
            
            surface.blit(leaf_surface, (x - particle_size * 1.5, y - particle_size))
            
        else:
            # Simple circle
            pygame.draw.circle(surface, (*self.color[:3], alpha), 
                             (x, y), particle_size)
            
            # Inner circle for depth
            if particle_size > 2:
                inner_color = (min(255, self.color[0] + 50),
                             min(255, self.color[1] + 50),
                             min(255, self.color[2] + 50),
                             alpha)
                pygame.draw.circle(surface, inner_color, (x, y), 
                                 max(1, particle_size // 2))