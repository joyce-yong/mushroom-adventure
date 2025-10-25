import pygame
from ui_cursor import GameCursor  # ✅ 导入我们刚写的模块

pygame.init()

# --- 基本设置 ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Custom Cursor Example")
clock = pygame.time.Clock()

# --- 创建自定义鼠标对象 ---
cursor = GameCursor("character/mushroom0.png", offset=(0, 0))

# --- 游戏主循环 ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- 背景 ---
    screen.fill((40, 40, 50))

    # --- 这里可以绘制游戏元素（例如玩家、敌人等） ---
    # e.g. screen.blit(player_img, player_rect)

    # --- 绘制鼠标 ---
    cursor.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
