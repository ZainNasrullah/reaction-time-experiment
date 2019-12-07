import pygame
import pygame.gfxdraw
import numpy as np


class GameConfig:
    def __init__(self):

        # general config
        pygame.init()
        self.display_width = 800
        self.display_height = 600
        self.circle_radius = 20
        self.font_size = 30
        self.bar_width = 40
        self.font_color = (255, 255, 255)  # white
        self.background_color = (255, 255, 255)  # white

        # setup display and font
        self.display = pygame.display.set_mode(
            (self.display_width, self.display_height)
        )
        pygame.display.set_caption("Reaction Time Test")
        self.font = pygame.font.SysFont("Comic Sans MS", self.font_size)

        # set starting values
        self.start_time = None
        self.run = True
        self.score = 0
        self.n_iter = 0
        self.clock = pygame.time.Clock()

    def fill_background(self, color=None):
        if color is None:
            color = self.background_color
        self.display.fill(color)
        pygame.draw.rect(
            self.display, (255, 127, 0), (0, 0, self.display_width, self.bar_width)
        )

    def print_score(self):
        text = f"Score: {self.score}/{self.n_iter + 1}"
        label = self.font.render(text, 1, self.font_color)
        text_rect = label.get_rect(center=(self.display_width / 2, 20))
        self.display.blit(label, text_rect)

    def event_handler(self, circle, selected_key):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
                return circle, None, None, None

            if event.type == pygame.KEYDOWN:
                if self.start_time:
                    time_elapsed = pygame.time.get_ticks() - self.start_time
                    print(time_elapsed)
                else:
                    time_elapsed = None

                mouse_position = pygame.mouse.get_pos()
                if (
                    circle.check_hitbox(mouse_position)
                    and event.unicode == selected_key
                ):
                    self.score += 1
                    correct_flag = 1
                else:
                    correct_flag = 0

                self.print_score()
                circle = Circle(self.display, radius=20, font=self.font)
                print(self.score)
                self.start_time = pygame.time.get_ticks()
                return circle, time_elapsed, event.unicode, correct_flag

        return circle, None, None, None

    def quit(self):
        pygame.quit()


class Circle:
    def __init__(self, surface, radius, font):
        self.surface = surface
        self.radius = radius
        self.font = font
        self.font_color = (255, 255, 255)  # white
        self.x = np.random.randint(self.radius, surface.get_width() - self.radius)
        self.y = np.random.randint(
            self.radius + 40, surface.get_height() - self.radius
        )
        self.color = (255, 127, 0)  # orange
        self.x_hitbox = (self.x - self.radius, self.x + self.radius)
        self.y_hitbox = (self.y - self.radius, self.y + self.radius)

    def render_self_with_text(self, text, color=None):
        if color is None:
            color = self.color

        self.circle_shell = pygame.gfxdraw.aacircle(
            self.surface, self.x, self.y, self.radius, color
        )
        self.circle_fill = pygame.gfxdraw.filled_circle(
            self.surface, self.x, self.y, self.radius, color
        )
        label = self.font.render(text, 1, self.font_color)
        text_rect = label.get_rect(center=(self.x, self.y))
        self.surface.blit(label, text_rect)

    def check_hitbox(self, position):
        x_flag = self.x_hitbox[0] < position[0] < self.x_hitbox[1]
        y_flag = self.y_hitbox[0] < position[1] < self.y_hitbox[1]
        return x_flag and y_flag
