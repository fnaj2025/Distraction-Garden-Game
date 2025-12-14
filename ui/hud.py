# ui/hud.py
import pygame

class HUD:
    def __init__(self, scene):
        # HUD sederhana atau kosong
        self.scene = scene
        self.font = pygame.font.SysFont("arial", 16)
    
    def draw(self, screen):
        # Kosongkan karena sudah ada draw_game_header()
        pass  # Tidak menggambar apa-apa