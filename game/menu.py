import pygame # type: ignore
import os
import config

# ___ Menu Setup ___
menu_images = []
for i in range(19): # flash 19 images in order
    menu_bg = pygame.image.load(os.path.join(f'img/menu/{i}.png')).convert()
    menu_bg = pygame.transform.scale(menu_bg, (config.screen_width, config.screen_height))
    menu_images.append(menu_bg)

# helper function to create UI buttons
def draw_button(text, x, y, width, height, inactive_col, active_col):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, width, height)
    color = active_col if rect.collidepoint(mouse) else inactive_col
    pygame.draw.rect(config.game_window, color, rect, border_radius=10)

    txt_surface = config.button_font.render(text, True, config.WHITE)
    text_rect = txt_surface.get_rect(center=(x + width // 2, y + height // 2))
    config.game_window.blit(txt_surface, text_rect)

    if rect.collidepoint(mouse) and click[0] == 1:
        return True
    return False


# ___ Menu screen ___

def menu_screen():
    
    in_menu = True
    global is_paused

    idx = 0  # index of current menu image
    last_switch = pygame.time.get_ticks()
    switch_interval = 100  # time until next image

    while in_menu:
        now = pygame.time.get_ticks()
        if now - last_switch >= switch_interval:
            idx = (idx + 1) % len(menu_images)  # next in list
            last_switch = now # reset time to current time to track next switch

        # draw current image
        config.game_window.blit(menu_images[idx], (0, 0))

        # --- Draw buttons ---
        play_pressed = draw_button("Play", 650, 50, 350, 100, (0, 80, 0), (0, 200, 0))
        sound_pressed = draw_button("Sound", 250, 50, 350, 100, (0, 80, 80), (0, 200, 200))
        exit_pressed = draw_button("Exit", 1050, 50, 350, 100, (80, 0, 0), (255, 60, 60))

        # draw score
        drawText(f'Score: {config.score}', config.fontLarge, config.CAYAN, 740, 180)

        # handle buttons actions and menu state
        if play_pressed:
            return "play"
        if sound_pressed:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                is_paused = True
            else:
                pygame.mixer.music.unpause()
                is_paused = False
        if exit_pressed:
            pygame.quit()
            exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        pygame.display.update()
        config.frameRate.tick(30) # half the frames of game 30 vs 60


# ___ Story Intro ___



# drawa text for UI
def drawText(text, font, text_col, text_x, text_y):
    img = font.render(text, True, text_col)
    config.game_window.blit(img, (text_x, text_y))