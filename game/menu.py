import pygame # type: ignore
import os
import sys
import config

# ___ Menu Setup ___
menu_images = []
for i in range(19): # flash 19 images in order
    menu_bg = pygame.image.load(os.path.join(f'img/menu/{i}.png')).convert()
    menu_bg = pygame.transform.scale(menu_bg, (config.screen_width, config.screen_height))
    menu_images.append(menu_bg)

# helper function to create UI buttons
def draw_button(text, x_center, y_pos, base_color=config.WHITE, hover_color=config.CAYAN):
    mouse_pos = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    base_text_surface = config.button_font.render(text, True, base_color)
    text_rect = base_text_surface.get_rect(center=(x_center, y_pos))
    is_hovered = text_rect.collidepoint(mouse_pos)
    scale = 1.1 if is_hovered else 1.0
    color = hover_color if is_hovered else base_color

    final_text_surface = config.button_font.render(text, True, color)
    final_text_surface = pygame.transform.rotozoom(final_text_surface, 0, scale)
    final_text_rect = final_text_surface.get_rect(center=(x_center, y_pos))
    
    config.game_window.blit(final_text_surface, final_text_rect)

    if is_hovered and click[0] == 1:
        pygame.time.delay(200) 
        return True
    
    return False


# ___ Level select screen ___
def level_select():
    in_select = True

    title_text = "SELECT LEVEL"
    title_y = int(config.screen_height * 0.15)

    num_levels = 2
    y_pos = int(config.screen_height * 0.50)

    button_width = 250
    gap = 200
    total_width = (num_levels * button_width) + ((num_levels - 1) * gap)

    x_start = (config.screen_width - total_width) // 2

    while in_select:
        config.game_window.fill((12, 20, 40))

        title_surface = config.title_font.render(title_text, True, config.WHITE)
        title_rect = title_surface.get_rect(center=(config.screen_width // 2, title_y))
        config.game_window.blit(title_surface, title_rect)

        x_offset = x_start + (button_width / 2)

        level1_pressed = draw_button("Level 1", x_offset, y_pos, config.WHITE, config.CAYAN)
        x_offset += button_width + gap

        level2_pressed = draw_button("Level 2", x_offset, y_pos, config.WHITE, config.CAYAN)

        if level1_pressed:
            return 1
        if level2_pressed:
            return 2
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "menu"

        pygame.display.update()
        config.frameRate.tick(30) 


# ___ Story screen ___
def show_story():
    story_lines = [
        "We are the Spore Fitters, a fragmented fungal mind that requires",
        "a host. Though we possess ultimate evolutionary power, our true",
        "strength is fragile. You, MushMush, are the seeker:",
        "a lone spore carrying the colony's last hope.",
        "",
        "Your target: The resource-rich sectors held by Humans. Their ships",
        "are now your enemies. Bypass their forces and dodge the space debris.",
        "Your mission: Reach the Cryogenic Safe Zone."
    ]
    instruction_text = "Press ESC to return to menu"

    title_text = "MUSHMUSH: ORIGINS"
    title_y = int(config.screen_height * 0.15)
    story_start_y = int(config.screen_height * 0.30)
    line_height = 55

    story_bg = pygame.Surface((config.screen_width, config.screen_height))
    story_bg.fill((10, 20, 40))
    config.game_window.blit(story_bg, (0, 0))

    title_surface = config.title_font.render(title_text, True, config.WHITE)
    title_rect = title_surface.get_rect(center=(config.screen_width // 2, title_y))
    config.game_window.blit(title_surface, title_rect)
    pygame.display.flip()

    def typewriter_text(text, line_index, color=config.CAYAN, delay=0.03):
        x = config.screen_width // 2
        y = story_start_y + line_index * line_height
        current_text = ""

        def redraw_static():
            config.game_window.blit(story_bg, (0, 0))
            config.game_window.blit(title_surface, title_rect)
            
            # draw previous lines
            for i, prev in enumerate(story_lines[:line_index]):
                prev_surface = config.story_font.render(prev, True, color)
                prev_rect = prev_surface.get_rect(center=(x, story_start_y + i * line_height))
                config.game_window.blit(prev_surface, prev_rect) 

        for char in text:
            current_text += char
            text_surface = config.story_font.render(current_text, True, color)
            text_rect = text_surface.get_rect(center=(x, y))

            redraw_static()
            config.game_window.blit(text_surface, text_rect)
            pygame.display.flip()
            pygame.time.delay(int(delay * 1000))

            # check for events during typing to allow quick exit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    # typewriter sequence
    for i, line in enumerate(story_lines):
        typewriter_text(line, i)
        pygame.time.delay(400)

    instruction_y = story_start_y + len(story_lines) * line_height + 100

    story_bg.fill((10, 20, 40))
    config.game_window.blit(story_bg, (0, 0))
    config.game_window.blit(title_surface, title_rect)

    # redraw all completed story lines
    for i, line in enumerate(story_lines):
        x = config.screen_width // 2
        y = story_start_y + i * line_height
        line_surface = config.story_font.render(line, True, config.CAYAN)
        line_rect = line_surface.get_rect(center=(x, y))
        config.game_window.blit(line_surface, line_rect)

    instruction_surface = config.fontLarge.render(instruction_text, True, config.WHITE)
    instruction_rect = instruction_surface.get_rect(center=(config.screen_width // 2, instruction_y))
    config.game_window.blit(instruction_surface, instruction_rect)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                waiting = False

    return "menu"


# ___ Controls screen ___
def controls():
    showing = True

    title_text = "CONTROLS"
    title_y = int(config.screen_height * 0.15)

    controls_start_y = int(config.screen_height * 0.35)
    line_height = 55

    actions_x = config.screen_width // 2 - 50
    inputs_x = config.screen_width // 2 + 50

    instruction_text = "Press ESC to return to menu"

    actions = [
        "Move Player:",
        "Laser:",
        "Heavy Laser:",
        "Mushroom Rocket:",
        "Laser Line:",
        "Plasma Fire:"
    ]
    inputs = [
        "Arrow Keys",
        "A Key",
        "D Key",
        "S Key",
        "W Key",
        "Q Key"
    ]

    while showing:
        config.game_window.fill((10, 20, 40))

        title_surface = config.title_font.render(title_text, True, config.WHITE) 
        title_rect = title_surface.get_rect(center=(config.screen_width // 2, title_y))
        config.game_window.blit(title_surface, title_rect)
        
        for i, action_line in enumerate(actions):
            y_pos = controls_start_y + i * line_height

            # draw action (left column, left-aligned)
            action_text = config.story_font.render(action_line, True, config.CAYAN)
            action_rect = action_text.get_rect(topright=(actions_x, y_pos) )
            config.game_window.blit(action_text, action_rect)

            # draw input (right column)
            input_text = config.story_font.render(inputs[i], True, config.CAYAN)
            input_rect = input_text.get_rect(topleft=(inputs_x, y_pos))
            config.game_window.blit(input_text, input_rect)

        instruction_y = controls_start_y + len(actions) * line_height + 100
        instruction_surface = config.fontLarge.render(instruction_text, True, config.WHITE)
        instruction_rect = instruction_surface.get_rect(center=(config.screen_width // 2, instruction_y))
        config.game_window.blit(instruction_surface, instruction_rect)

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                showing = False

    return "menu"


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

        # draw buttons
        num_buttons = 4
        y_pos = int(config.screen_height * 0.80)

        total_width = int(config.screen_width * 0.75)
        x_spacing = total_width // (num_buttons - 1) if num_buttons > 1 else 0
        x_start = int(config.screen_width - total_width) // 2
        x_offset = x_start

        start_pressed = draw_button("Start", x_offset, y_pos, config.WHITE, config.CAYAN)
        x_offset += x_spacing

        story_pressed = draw_button("Story", x_offset, y_pos, config.WHITE, config.CAYAN)
        x_offset += x_spacing

        controls_pressed = draw_button("Controls", x_offset, y_pos, config.WHITE, config.CAYAN)
        x_offset += x_spacing

        quit_pressed = draw_button("Quit", x_offset, y_pos, config.WHITE, (255, 60, 60))

        # draw score
        #drawText(f'Score: {config.score}', config.fontLarge, config.CAYAN, 740, 180)

        # handle buttons actions and menu state
        if start_pressed:
            return "level_select"
        if story_pressed:
            show_story()
        if controls_pressed:
            controls()
        if quit_pressed:
            pygame.quit()
            exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        pygame.display.update()
        config.frameRate.tick(30) # half the frames of game 30 vs 60



# ___ Result screen ___
def result_screen():
    title_text = "MISSION FAILED"
    title_y = int(config.screen_height * 0.25)
    
    # get the final score
    final_score = config.score
    
    score_text = f"Score: {final_score}"
    score_y = int(config.screen_height * 0.45)
    
    instruction_text = "Press Space to return to menu"
    instruction_y = int(config.screen_height * 0.70)
    
    # background
    result_bg = pygame.Surface((config.screen_width, config.screen_height))
    result_bg.fill((20, 10, 20))
    config.game_window.blit(result_bg, (0, 0))
    
    # draw title
    title_surface = config.title_font.render(title_text, True, config.RED)
    title_rect = title_surface.get_rect(center=(config.screen_width // 2, title_y))
    config.game_window.blit(title_surface, title_rect)
    
    # draw score
    score_surface = config.fontLarge.render(score_text, True, config.CAYAN)
    score_rect = score_surface.get_rect(center=(config.screen_width // 2, score_y))
    config.game_window.blit(score_surface, score_rect)
    
    # draw instruction
    instruction_surface = config.fontLarge.render(instruction_text, True, config.WHITE)
    instruction_rect = instruction_surface.get_rect(center=(config.screen_width // 2, instruction_y))
    config.game_window.blit(instruction_surface, instruction_rect)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
    
    return "menu"


# drawa text for UI
def drawText(text, font, text_col, text_x, text_y):
    img = font.render(text, True, text_col)
    config.game_window.blit(img, (text_x, text_y))