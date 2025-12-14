class BaseScene:
    def __init__(self, game):
        self.game = game

    def handle_event(self, event):
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement handle_event()"
        )

    def update(self, dt):
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement update()"
        )

    def render(self, screen):
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement render()"
        )
