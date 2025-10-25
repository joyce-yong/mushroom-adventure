import pygame
import ui_cursor

pygame.init()
screen = pygame.display.set_mode((800, 600))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((50, 50, 50))
    pygame.display.flip()  # 🧊自动画出 mushroom 光标
pygame.quit()
