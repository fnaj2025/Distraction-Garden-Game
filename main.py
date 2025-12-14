# main.py
import pygame
from settings import WIDTH, HEIGHT, FPS
from scenes.home_scene import HomeScene
from audio_manager import AudioManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Distraction Garden")
        self.width = WIDTH
        self.height = HEIGHT
        self.clock = pygame.time.Clock()
        self.scene = HomeScene(self)
        self.previous_scene_surface = None
        self.running = True
        self.dt = 0
        self.audio = AudioManager()
        self.audio.play_music("sounds/background_music.mp3")
        
        
        
    def change_scene(self, new_scene):
        # simpan tampilan lama (dipakai QuestionScene)
        self.previous_scene_surface = self.screen.copy()
        self.scene = new_scene

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.scene.handle_event(event)

            self.scene.update(dt)
            self.scene.render(self.screen)
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    Game().run()
