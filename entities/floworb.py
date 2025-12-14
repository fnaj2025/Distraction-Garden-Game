# entities/floworb.py
import pygame, math
from .entity import Entity

class FlowOrb(Entity):
    """
    Flow state orb that appears when garden is calm.
    Collecting it boosts focus for a short time.
    """
    def __init__(self, x, y):
        super().__init__(x,y,20,20)
        self.timer = 10.0

    def update(self, dt, game):
        self.timer -= dt
        if self.timer <= 0:
            self.destroy()

    def draw(self, surface):
        x,y = self.rect.center
        # outer rotating arc effect (simple)
        for s in range(3):
            r = 12 + s*4
            start = (pygame.time.get_ticks()/200.0 + s) % (2*math.pi)
            # draw small arc by drawing many lines
            pts = []
            for a in [start + i*0.3 for i in range(6)]:
                pts.append((x + math.cos(a)*r, y + math.sin(a)*r))
            if pts:
                pygame.draw.lines(surface, (120,200,255), False, pts, 3)
        # center
        pygame.draw.circle(surface, (160,230,255), (x,y), 8)

    def interact(self, player, game):
        if self.is_alive():
            self.destroy()
            return {"type": "flow_collected"}
        return None
