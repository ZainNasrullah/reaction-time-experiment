import pygame
import pygame.gfxdraw
import numpy as np

pygame.init()
display_width = 800
display_height = 600
circle_radius = 20
font_size = 30

gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("Reaction Time Test")
clock = pygame.time.Clock()

black = (0, 0, 0)
white = (255, 255, 255)
orange = (255, 127, 0)
font = pygame.font.SysFont("Comic Sans MS", font_size)


class Circle:
    def __init__(self, surface, radius):
        self.surface = surface
        self.radius = radius
        self.x =  np.random.randint(self.radius, surface.get_width() - self.radius)
        self.y = np.random.randint(self.radius, surface.get_height() - self.radius)
        self.color = (255, 127, 0) # orange
        self.x_hitbox = (self.x - self.radius, self.x + self.radius)
        self.y_hitbox = (self.y - self.radius, self.y + self.radius)

    def render_self(self):
        pygame.gfxdraw.aacircle(self.surface, self.x, self.y, self.radius, self.color)
        pygame.gfxdraw.filled_circle(self.surface, self.x, self.y, self.radius, self.color)

    def render_text(self, text):
        label = font.render(text, 1, white)
        text_rect = label.get_rect(center=(self.x, self.y))
        self.surface.blit(label, text_rect)

    def check_hitbox(self, position):
        x_flag = self.x_hitbox[0] < position[0] < self.x_hitbox[1]
        y_flag = self.y_hitbox[0] < position[1] < self.y_hitbox[1]
        return x_flag and y_flag


run = True
circle = Circle(gameDisplay, radius=20)
start_time = None
score = 0

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
        if event.type == pygame.KEYDOWN:
            if start_time:
                time_elapsed = start_time - pygame.time.get_ticks()
                print(time_elapsed)

            mouse_position = pygame.mouse.get_pos()
            if circle.check_hitbox(mouse_position) and event.unicode == 'q':
                score +=1
            else:
                score -=1

            circle = Circle(gameDisplay, radius=20)
            print(score)
            start_time = pygame.time.get_ticks()


    gameDisplay.fill(white)
    circle.render_self()
    circle.render_text("Q")
    pygame.display.update()
    clock.tick(60)


pygame.quit()
