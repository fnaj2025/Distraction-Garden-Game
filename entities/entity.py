# entities/entity.py
import pygame
from abc import ABC, abstractmethod

class Entity(ABC):
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (x, y)
        self._alive = True

    @abstractmethod
    def update(self, dt, scene):
        """
        scene = GameScene
        """
        raise NotImplementedError

    @abstractmethod
    def draw(self, surface):
        raise NotImplementedError

    def interact(self, player, scene):
        """
        Optional interaction hook
        """
        return None

    def destroy(self):
        self._alive = False

    def is_alive(self):
        return self._alive
