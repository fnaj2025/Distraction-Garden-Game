import pygame, math
from .entity import Entity
from settings import WIDTH, HEIGHT

class Player(Entity):
    """
    The MIND Guardian - diamond-shaped character with glow and animations.
    """
    def __init__(self, x, y):
        super().__init__(x, y, 40, 46)
        self.speed = 260  # px/sec
        self.color = (120, 200, 255)
        self.eye_color = (20, 30, 40)
        self.score = 0
        self.repels = 0
        
        # Animation variables
        self.float_timer = 0
        self.walk_timer = 0
        self.move_direction = (0, 0)
        self.is_moving = False
        self.interact_timer = 0

    def update(self, dt, game):
        # Update animation timers
        self.float_timer += dt * 2
        self.walk_timer += dt * 8 if self.is_moving else dt * 2
        self.interact_timer = max(0, self.interact_timer - dt * 4)
        
        # Movement
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
            
        self.is_moving = (dx != 0 or dy != 0)
        if self.is_moving:
            self.move_direction = (dx, dy)
            
        if dx != 0 or dy != 0:
            m = (dx*dx + dy*dy)**0.5
            dx /= m
            dy /= m
            
        self.rect.x += dx * self.speed * dt
        self.rect.y += dy * self.speed * dt
        
        # Keep inside play area (below HUD)
        self.rect.clamp_ip(pygame.Rect(0, 64, WIDTH, HEIGHT-64))

    def draw(self, surface):
        x, y = self.rect.center
        
        # Float animation
        float_offset = math.sin(self.float_timer) * 3
        
        # Walk animation
        if self.is_moving:
            walk_offset = math.sin(self.walk_timer) * 5
        else:
            walk_offset = 0
        
        # Interaction pulse
        if self.interact_timer > 0:
            pulse_radius = int(60 * self.interact_timer)
            pulse_surface = pygame.Surface((pulse_radius * 2, pulse_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(pulse_surface, (120, 200, 255, int(100 * self.interact_timer)), 
                             (pulse_radius, pulse_radius), pulse_radius)
            surface.blit(pulse_surface, (x - pulse_radius, y - pulse_radius))
        
        # Glow effect with animation
        for i in range(3):
            glow_radius = 26 + i * 8
            glow_alpha = 40 - i * 10
            glow_pulse = 1 + 0.1 * math.sin(self.float_timer + i)
            
            s = pygame.Surface((int(glow_radius * 2 * glow_pulse), 
                              int(glow_radius * 2 * glow_pulse)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color[:3], glow_alpha), 
                             (int(glow_radius * glow_pulse), int(glow_radius * glow_pulse)), 
                             int(glow_radius * glow_pulse))
            surface.blit(s, (x - int(glow_radius * glow_pulse), 
                           y - int(glow_radius * glow_pulse)))
        
        # Diamond polygon with float and walk animations
        points = [
            (x, y - 20 + float_offset + walk_offset),
            (x + 18, y + float_offset),
            (x, y + 20 + float_offset - walk_offset),
            (x - 18, y + float_offset)
        ]
        
        # Draw diamond with gradient
        pygame.draw.polygon(surface, self.color, points)
        
        # Inner glow effect
        inner_points = [
            (x, y - 12 + float_offset + walk_offset),
            (x + 10, y + float_offset),
            (x, y + 12 + float_offset - walk_offset),
            (x - 10, y + float_offset)
        ]
        
        # Inner diamond with gradient
        inner_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(inner_surface, (255, 255, 255, 200), 
                          [(p[0] - x + 20, p[1] - y + 20) for p in inner_points])
        surface.blit(inner_surface, (x - 20, y - 20))
        
        # Sparkle effect when not moving
        if not self.is_moving and math.sin(self.float_timer * 1.5) > 0.8:
            sparkle_size = 2
            sparkle_x = x + math.cos(self.float_timer) * 25
            sparkle_y = y + math.sin(self.float_timer * 1.3) * 25
            pygame.draw.circle(surface, (255, 255, 255, 200), 
                             (int(sparkle_x), int(sparkle_y)), sparkle_size)
        
        # Eyes with blink animation
        blink = 1 if math.sin(self.float_timer * 0.5) > 0 else 0.3
        eye_y_offset = -6 * blink
        
        # Animated pupils when moving
        if self.is_moving and self.move_direction[0] != 0:
            pupil_offset = 2 if self.move_direction[0] > 0 else -2
        else:
            pupil_offset = 0
        
        pygame.draw.circle(surface, self.eye_color, 
                         (int(x - 4 + pupil_offset), int(y + eye_y_offset)), 2)
        pygame.draw.circle(surface, self.eye_color, 
                         (int(x + 4 + pupil_offset), int(y + eye_y_offset)), 2)
        
        # Eye highlights
        pygame.draw.circle(surface, (255, 255, 255), 
                         (int(x - 5 + pupil_offset), int(y + eye_y_offset - 1)), 1)
        pygame.draw.circle(surface, (255, 255, 255), 
                         (int(x + 3 + pupil_offset), int(y + eye_y_offset - 1)), 1)

    def interact_nearby(self, game, radius=48):
        # Trigger interaction animation
        self.interact_timer = 1.0
        
        # repel bugs within radius: push and destroy some types
        cx, cy = self.rect.center
        for ent in list(game.entities):
            if ent is self or not ent.is_alive():
                continue
            ex, ey = ent.rect.center
            dx = ex-cx
            dy = ey-cy
            if dx*dx + dy*dy <= radius*radius:
                result = ent.interact(self, game)  # many bugs define interaction
                if result and result.get("type") == "bug_repelled":
                    self.repels += 1
                    self.score += result.get("value", 5)
                    game.spawn_particles(ent=ent, kind="pop", count=12)  # More particles