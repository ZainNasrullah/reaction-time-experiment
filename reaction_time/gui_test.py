import pygame
import pygame.gfxdraw
import numpy as np


class GameConfig:
    def __init__(self):
        pygame.init()
        self.display_width = 800
        self.display_height = 600
        self.circle_radius = 20
        self.font_size = 30
        self.background_color = (255, 255, 255)

        self.display = pygame.display.set_mode(
            (self.display_width, self.display_height)
        )
        self.font = pygame.font.SysFont("Comic Sans MS", self.font_size)

        pygame.display.set_caption("Reaction Time Test")
        self.clock = pygame.time.Clock()

    def fill_background(self, color=(255, 255, 255)):
        self.display.fill(color)

    def quit(self):
        pygame.quit()


class Circle:
    def __init__(self, surface, radius, font):
        self.surface = surface
        self.radius = radius
        self.font = font
        self.font_color = (255, 255, 255) # white
        self.x = np.random.randint(self.radius, surface.get_width() - self.radius)
        self.y = np.random.randint(self.radius, surface.get_height() - self.radius)
        self.color = (255, 127, 0)  # orange
        self.x_hitbox = (self.x - self.radius, self.x + self.radius)
        self.y_hitbox = (self.y - self.radius, self.y + self.radius)

    def render_self_with_text(self, text):
        pygame.gfxdraw.aacircle(self.surface, self.x, self.y, self.radius, self.color)
        pygame.gfxdraw.filled_circle(
            self.surface, self.x, self.y, self.radius, self.color
        )
        label = self.font.render(text, 1, self.font_color)
        text_rect = label.get_rect(center=(self.x, self.y))
        self.surface.blit(label, text_rect)

    def check_hitbox(self, position):
        x_flag = self.x_hitbox[0] < position[0] < self.x_hitbox[1]
        y_flag = self.y_hitbox[0] < position[1] < self.y_hitbox[1]
        return x_flag and y_flag


game = GameConfig()
circle = Circle(game.display, radius=20, font=game.font)

start_time = None
score = 0

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
        if event.type == pygame.KEYDOWN:
            if start_time:
                time_elapsed = pygame.time.get_ticks() - start_time
                print(time_elapsed)

            mouse_position = pygame.mouse.get_pos()
            if circle.check_hitbox(mouse_position) and event.unicode == "q":
                score += 1
            else:
                score -= 1

            circle = Circle(game.display, radius=20, font=game.font)
            print(score)
            start_time = pygame.time.get_ticks()

    game.fill_background()
    circle.render_self_with_text("Q")
    pygame.display.update()
    game.clock.tick(60)


game.quit()
