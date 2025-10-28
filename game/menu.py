import pygame, os, sys, config, math, random

from cursor import Cursor
from vfx_galaxy import GalaxyBackground
from vfx_transition import Transition
from vfx_cybergrid import CyberGrid
from vfx_bionebula import BioNebula


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

# helper function to load and scale the background image (result screen)
def load_result_bg(filename):
    path = os.path.join('img', 'result', filename) 
    try:
        image = pygame.image.load(path).convert()
        return pygame.transform.scale(image, (config.screen_width, config.screen_height))
    except pygame.error as e:
        print(f"Error loading result background image '{filename}': {e}")
        fallback = pygame.Surface((config.screen_width, config.screen_height))
        fallback.fill(config.BLACK)
        return fallback



# ___ Level select screen ___
def level_select():
    in_select = True
    cursor = Cursor("img/cursor", frame_rate=120)
    cursor.load_frames("img/cursor", scale_factor=1.5)

    galaxy = GalaxyBackground(config.screen_width, config.screen_height, num_stars=120)
    clock = pygame.time.Clock()


    title_text = "SELECT LEVEL"
    title_y = int(config.screen_height * 0.15)

    num_levels = 2
    y_pos = int(config.screen_height * 0.50)

    button_width = 250
    gap = 200
    total_width = (num_levels * button_width) + ((num_levels - 1) * gap)

    x_start = (config.screen_width - total_width) // 2

    while in_select:
        dt = clock.tick(60) / 1000.0
        time_ms = pygame.time.get_ticks()

        # --- draw sci-fi background ---
        config.game_window.fill((10, 10, 25))  # base dark color
        galaxy.update(dt, time_ms)
        galaxy.draw(config.game_window, time_ms)
        

        title_surface = config.title_font.render(title_text, True, config.WHITE)
        title_rect = title_surface.get_rect(center=(config.screen_width // 2, title_y))
        config.game_window.blit(title_surface, title_rect)

        x_offset = x_start + (button_width / 2)
        
        
        float_offset = int(math.sin(time_ms * 0.002) * 10)  # smooth float motion
        level1_pressed = draw_button("Level 1", x_offset, y_pos + float_offset, config.WHITE, config.CAYAN)
        x_offset += button_width + gap
        level2_pressed = draw_button("Level 2", x_offset, y_pos + float_offset, config.WHITE, config.CAYAN)

        if level1_pressed:
            click_pos = (x_start + button_width/2, y_pos)
            galaxy.spawn_ripple(click_pos)
            trans = Transition(config.game_window)
            
            while trans.warp_out(click_pos): 
                config.game_window.fill((10, 10, 25))
                galaxy.draw(config.game_window, time_ms)
                trans.draw() 
                pygame.display.flip()
                clock.tick(60)
            return 1 

        if level2_pressed:
            click_pos = (x_start + button_width/2 + button_width + gap, y_pos)
            galaxy.spawn_ripple(click_pos)
            trans = Transition(config.game_window)

            while trans.warp_out(click_pos):
                config.game_window.fill((10, 10, 25))
                galaxy.draw(config.game_window, time_ms)
                trans.draw() 
                pygame.display.flip()
                clock.tick(60)
            return 2 

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "menu"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                cursor.spawn_spores(pygame.mouse.get_pos())
            
        for spore in cursor.spores[:]:
            if not spore.update():
                cursor.spores.remove(spore)
            else:
                spore.draw(config.game_window)
            
        cursor.update()
        cursor.draw(config.game_window)

        pygame.display.update()
        config.frameRate.tick(30) 


# ___ Story screen ___
def show_story():
    # story_bg = pygame.Surface((config.screen_width, config.screen_height))
    # story_bg.fill((12, 20, 40))
    nebula = BioNebula(config.screen_width, config.screen_height, num_spores=80)


    title_font = config.title_font
    story_font = config.story_font

    title_text = "MUSHMUSH: ORIGINS"
    title_surface = title_font.render(title_text, True, config.WHITE)
    title_rect = title_surface.get_rect(center=(config.screen_width // 2, int(config.screen_height * 0.15)))

    instruction_font = config.fontLarge
    instruction_surface = instruction_font.render("Press ESC to return to menu", True, config.WHITE)
    instruction_rect = instruction_surface.get_rect(center=(config.screen_width // 2, int(config.screen_height * 0.9)))

    story_text = [
        "We are the Spore Fitters, a fragmented fungal mind that requires",
        "a host. Though we possess ultimate evolutionary power, our true",
        "strength is fragile. You, MushMush, are the seeker:",
        "a lone spore carrying the colony's last hope.",
        "",
        "Your target: The resource-rich sectors held by Humans. Their ships",
        "are now your enemies. Bypass their forces and dodge the space debris.",
        "Your mission: Reach the Cryogenic Safe Zone."
    ]

    story_lines = []
    line_height = 55
    story_start_y = int(config.screen_height * 0.30)
    typing_speed = 30

    cursor = Cursor("img/cursor", frame_rate=120)
    cursor.load_frames("img/cursor", scale_factor=1.5)
    clock = pygame.time.Clock()

    current_line = 0
    current_char = 0
    last_type_time = pygame.time.get_ticks()

    showing_story = True
    while showing_story:
        # config.game_window.blit(story_bg, (0, 0))
        dt = clock.tick(60) / 1000.0
        nebula.update(dt)
        nebula.draw(config.game_window)

        config.game_window.blit(title_surface, title_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                showing_story = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                cursor.spawn_spores(pygame.mouse.get_pos())

        # typing effect
        if current_line < len(story_text):
            now = pygame.time.get_ticks()
            if now - last_type_time > typing_speed:
                current_char += 1
                if current_char > len(story_text[current_line]):
                    story_lines.append(story_text[current_line])
                    current_line += 1
                    current_char = 0
                last_type_time = now

        for i, line in enumerate(story_lines):
            line_surface = story_font.render(line, True, config.CAYAN)
            line_rect = line_surface.get_rect(center=(config.screen_width // 2, story_start_y + i * line_height))
            config.game_window.blit(line_surface, line_rect)

        if current_line < len(story_text):
            typing_surface = story_font.render(story_text[current_line][:current_char], True, config.CAYAN)
            typing_rect = typing_surface.get_rect(center=(config.screen_width // 2, story_start_y + current_line * line_height))
            config.game_window.blit(typing_surface, typing_rect)

        config.game_window.blit(instruction_surface, instruction_rect)

        for spore in cursor.spores[:]:
            if not spore.update():
                cursor.spores.remove(spore)
            else:
                spore.draw(config.game_window)

        cursor.update()
        cursor.draw(config.game_window)

        pygame.display.update()
        clock.tick(60)

    return "menu"


# ___ Controls screen ___
def controls():
    showing = True
    cursor = Cursor("img/cursor", frame_rate=120)
    cursor.load_frames("img/cursor", scale_factor=1.5)
    clock = pygame.time.Clock()
    
    grid_bg = CyberGrid(config.screen_width, config.screen_height, spacing=60) 

    title_text = "CONTROLS"
    title_y = int(config.screen_height * 0.15)
    # ... (rest of variable setup)
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
        dt = clock.tick(60) / 1000.0 
        
        # Update the Background
        config.game_window.fill((10, 20, 40)) # Base dark color
        grid_bg.update(dt) # Update the pulse time
        grid_bg.draw(config.game_window) # Draw the grid

        # Draw UI Elements (Title, Text, etc.)
        title_surface = config.title_font.render(title_text, True, config.WHITE) 
        title_rect = title_surface.get_rect(center=(config.screen_width // 2, title_y))
        config.game_window.blit(title_surface, title_rect)
        
        for i, action_line in enumerate(actions):
             y_pos = controls_start_y + i * line_height

             # draw action (left column, right-aligned)
             action_text = config.story_font.render(action_line, True, config.CAYAN)
             action_rect = action_text.get_rect(topright=(actions_x, y_pos) )
             config.game_window.blit(action_text, action_rect)

             # draw input (right column, left-aligned)
             input_text = config.story_font.render(inputs[i], True, config.CAYAN)
             input_rect = input_text.get_rect(topleft=(inputs_x, y_pos))
             config.game_window.blit(input_text, input_rect)

        instruction_y = controls_start_y + len(actions) * line_height + 100
        instruction_surface = config.fontLarge.render(instruction_text, True, config.WHITE)
        instruction_rect = instruction_surface.get_rect(center=(config.screen_width // 2, instruction_y))
        config.game_window.blit(instruction_surface, instruction_rect)


        # 3. Draw Cursor & Spores
        for spore in cursor.spores[:]:
            if not spore.update():
                cursor.spores.remove(spore)
            else:
                spore.draw(config.game_window)

        cursor.update()
        cursor.draw(config.game_window)

        pygame.display.flip()
        
        # 4. Handle Events
        for event in pygame.event.get():
             if event.type == pygame.QUIT:
                 pygame.quit()
                 sys.exit()
             elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                 showing = False
             elif event.type == pygame.MOUSEBUTTONDOWN:
                 cursor.spawn_spores(pygame.mouse.get_pos())
                 
    return "menu"


# ___ Menu screen ___
def menu_screen():
    in_menu = True
    global is_paused

    idx = 0  # index of current menu image
    last_switch = pygame.time.get_ticks()
    switch_interval = 100  # time until next image

    cursor = Cursor("img/cursor", frame_rate=120)
    cursor.load_frames("img/cursor", scale_factor=1.5)

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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                cursor.spawn_spores(pygame.mouse.get_pos())

        for spore in cursor.spores[:]:
            if not spore.update():
                cursor.spores.remove(spore)
            else:
                spore.draw(config.game_window)

        cursor.update()
        cursor.draw(config.game_window)

        pygame.display.update()
        config.frameRate.tick(30) # half the frames of game 30 vs 60



# ___ Result screen ___
def result_screen():
    is_win = config.score >= getattr(config, 'target_score', 0)

    if is_win:
        title_text = "MISSION COMPLETED"
        title_color = config.CAYAN
        background_image = load_result_bg('win.png')
    else:
        title_text = "MISSION FAILED"
        title_color = config.RED
        background_image = load_result_bg('lose.png')

    title_y = int(config.screen_height * 0.25)
    
    score_text = f"Score: {config.score} / {getattr(config, 'target_score', 0)}"
    score_y = int(config.screen_height * 0.45)
    
    instruction_text = "Press Space to return to menu"
    instruction_y = int(config.screen_height * 0.70)

    cursor = Cursor("img/cursor", frame_rate=120)
    cursor.load_frames("img/cursor", scale_factor=1.5)

    clock = pygame.time.Clock()
    waiting = True

    while waiting:
        # background
        config.game_window.blit(background_image, (0, 0))
        
        # draw title
        title_surface = config.title_font.render(title_text, True, title_color)
        title_rect = title_surface.get_rect(center=(config.screen_width // 2, title_y))
        config.game_window.blit(title_surface, title_rect)
        
        # draw score
        score_surface = config.score_fontLarge.render(score_text, True, config.PURPLE)
        score_rect = score_surface.get_rect(center=(config.screen_width // 2, score_y))
        config.game_window.blit(score_surface, score_rect)
        
        # draw instruction
        instruction_surface = config.fontLarge.render(instruction_text, True, config.WHITE)
        instruction_rect = instruction_surface.get_rect(center=(config.screen_width // 2, instruction_y))
        config.game_window.blit(instruction_surface, instruction_rect)

        # update and draw cursor
        for spore in cursor.spores[:]:
            if not spore.update():
                cursor.spores.remove(spore)
            else:
                spore.draw(config.game_window)
        
        cursor.update()
        cursor.draw(config.game_window)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                cursor.spawn_spores(pygame.mouse.get_pos())
    
        pygame.display.flip()
        clock.tick(60)
    
    return "menu"


# drawa text for UI
def drawText(text, font, text_col, text_x, text_y):
    img = font.render(text, True, text_col)
    config.game_window.blit(img, (text_x, text_y))
