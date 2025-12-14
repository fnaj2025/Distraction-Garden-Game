# entities/bug.py
import pygame, random, math
from .entity import Entity

class Bug(Entity):
    def __init__(self, x, y, w=30, h=30):
        super().__init__(x, y, w, h)
        # Kecepatan dasar, akan diset di subclass
        self.speed = 1.5
        self.target = None
        self.value = 6
        self.color = (220, 70, 70) 
        
        # Variasi gerakan
        self.wobble_timer = random.uniform(0, math.pi * 2)
        self.wobble_amount = random.uniform(0.5, 2.0)

    def update(self, dt, scene):
        self.rect.y += self.speed * 60 * dt  # Convert speed ke pixels per second
        
        # Gerakan wobble horizontal
        self.wobble_timer += dt * 3
        self.rect.x += math.sin(self.wobble_timer) * self.wobble_amount
        
        # Boundary check - jika keluar dari layar bawah, hancurkan
        if self.rect.top > scene.game.height:
            self.destroy()
            
        # Jika mencapai plant, serang
        for ent in scene.entities:
            if ent.__class__.__name__ == "Plant" and ent.is_alive():
                if self.rect.colliderect(ent.rect):
                    ent.damage(self.value)
                    self.destroy()
                    scene.spawn_particles(self, "spark", 8)
                    break

    def draw(self, surface):
        # Badan bug utama
        pygame.draw.circle(surface, self.color, self.rect.center, self.rect.width//2)
        
        # Highlight/glow effect
        highlight_radius = self.rect.width//2 - 2
        highlight_color = (
            min(255, self.color[0] + 50),
            min(255, self.color[1] + 50),
            min(255, self.color[2] + 50)
        )
        pygame.draw.circle(surface, highlight_color, 
                         (self.rect.centerx - 3, self.rect.centery - 3), 
                         highlight_radius//2)
        
        # Mata bug
        eye_size = 3
        eye_offset = self.rect.width//4
        pygame.draw.circle(surface, (30, 30, 30), 
                         (self.rect.centerx - eye_offset, self.rect.centery - eye_offset), 
                         eye_size)
        pygame.draw.circle(surface, (30, 30, 30), 
                         (self.rect.centerx + eye_offset, self.rect.centery - eye_offset), 
                         eye_size)
        
        # Antena bug
        antenna_length = self.rect.width//2
        antenna_angle = math.sin(pygame.time.get_ticks() / 300) * 0.5
        
        # Antena kiri
        left_antenna_x = self.rect.centerx - antenna_length * math.cos(math.pi/4 + antenna_angle)
        left_antenna_y = self.rect.centery - antenna_length * math.sin(math.pi/4 + antenna_angle)
        pygame.draw.line(surface, self.color, 
                        (self.rect.centerx - 3, self.rect.centery - 3),
                        (left_antenna_x, left_antenna_y), 2)
        
        # Antena kanan
        right_antenna_x = self.rect.centerx + antenna_length * math.cos(math.pi/4 - antenna_angle)
        right_antenna_y = self.rect.centery - antenna_length * math.sin(math.pi/4 - antenna_angle)
        pygame.draw.line(surface, self.color, 
                        (self.rect.centerx + 3, self.rect.centery - 3),
                        (right_antenna_x, right_antenna_y), 2)

    def interact(self, player, scene):
        """Dipanggil saat player menabrak bug"""
        self.destroy()
        scene.spawn_particles(self, "spark", 12)
        return {"type": "bug_destroyed", "value": self.value}


class ChatBug(Bug):
    def __init__(self, x, y):
        super().__init__(x, y, 32, 32)
        self.value = 7
        self.color = (255, 50, 50) 
        self.speed = random.uniform(0.8, 1.2) 

    def draw(self, surface):
        # Badan utama
        pygame.draw.circle(surface, self.color, self.rect.center, self.rect.width//2)
        
        # Efek chat bubble
        bubble_radius = self.rect.width//2 - 4
        bubble_color = (255, 255, 255)
        pygame.draw.circle(surface, bubble_color, 
                         (self.rect.centerx, self.rect.centery), 
                         bubble_radius)
        
        # Tanda chat (tiga titik)
        dot_color = (100, 100, 100)
        dot_spacing = 5
        for i in range(3):
            pygame.draw.circle(surface, dot_color,
                             (self.rect.centerx - dot_spacing + i * dot_spacing,
                              self.rect.centery),
                             2)
        
        # Ekor chat bubble
        points = [
            (self.rect.centerx - 8, self.rect.centery + bubble_radius),
            (self.rect.centerx, self.rect.centery + bubble_radius + 6),
            (self.rect.centerx + 8, self.rect.centery + bubble_radius)
        ]
        pygame.draw.polygon(surface, bubble_color, points)
        
        # Border chat bubble
        pygame.draw.circle(surface, (200, 200, 200), 
                         (self.rect.centerx, self.rect.centery), 
                         bubble_radius, 1)

    def interact(self, player, scene):
        """ChatBug hanya memberikan nilai dan efek visual"""
        self.destroy()
        scene.spawn_particles(self, "spark", 12)
        return {"type": "bug_destroyed", "value": self.value}


class NotifBadge(Bug):
    def __init__(self, x, y):
        super().__init__(x, y, 28, 28)
        self.value = 10
        self.color = (50, 200, 50) 
        self.speed = random.uniform(1.2, 1.6)

    def draw(self, surface):
        # Badan utama (lingkaran dengan pinggiran)
        pygame.draw.circle(surface, self.color, self.rect.center, self.rect.width//2)
        pygame.draw.circle(surface, (255, 255, 255), 
                         self.rect.center, self.rect.width//2 - 2)
        pygame.draw.circle(surface, self.color, 
                         self.rect.center, self.rect.width//2 - 4)
        
        # Angka notifikasi (acak 1-9)
        number_font = pygame.font.SysFont("arial", 12, bold=True)
        number = random.randint(1, 9)
        number_text = number_font.render(str(number), True, (255, 255, 255))
        number_rect = number_text.get_rect(center=self.rect.center)
        surface.blit(number_text, number_rect)
        
        # Efek glow/kilat
        pulse = (math.sin(pygame.time.get_ticks() / 200) + 1) * 0.5
        glow_radius = self.rect.width//2 + int(3 * pulse)
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.color, int(100 * pulse)), 
                          (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surface, (self.rect.centerx - glow_radius, 
                                   self.rect.centery - glow_radius))

    def interact(self, player, scene):
        """NotifBadge mengurangi fokus saat ditabrak"""
        self.destroy()
        scene.spawn_particles(self, "spark", 12)
        scene.focus = max(0, scene.focus - 10)  # Mengurangi fokus
        return {"type": "bug_destroyed", "value": self.value}


class PopupBug(Bug):
    def __init__(self, x, y):
        super().__init__(x, y, 36, 30)
        self.value = 9
        self.color = (255, 255, 50)  
        self.speed = random.uniform(1.0, 1.4) 

    def draw(self, surface):
        # Badan utama 
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        
        # Efek pinggiran
        pygame.draw.rect(surface, (255, 255, 200), 
                        (self.rect.x + 2, self.rect.y + 2, 
                         self.rect.width - 4, self.rect.height - 4), 
                        border_radius=6)
        
        # Ikon X (close button)
        x_color = (100, 100, 100)
        padding = 8
        pygame.draw.line(surface, x_color,
                        (self.rect.left + padding, self.rect.top + padding),
                        (self.rect.right - padding, self.rect.bottom - padding), 3)
        pygame.draw.line(surface, x_color,
                        (self.rect.right - padding, self.rect.top + padding),
                        (self.rect.left + padding, self.rect.bottom - padding), 3)
        
        # Efek berkedip
        blink = math.sin(pygame.time.get_ticks() / 150) > 0
        if blink:
            border_color = (255, 100, 100)
            pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)

    def interact(self, player, scene):
        """Popup bug akan trigger question saat ditabrak"""
        self.destroy()
        scene.spawn_particles(self, "spark", 15)
        return {"type": "popup_bug"}