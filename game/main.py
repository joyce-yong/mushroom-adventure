import pygame # type: ignore
import os, gc
from pygame import mixer # type: ignore
import random


import config
import menu
import characterClass
from spaceObjects import Asteroid, BlackHole
from projectiles import LaserLine
from sprite_groups import (
    enemy_group, 
    player_lasers,  
    heavyLaser_group, 
    rockets_group, 
    asteroid_group, 
    enemy_beam_group, 
    explosion_group,
    blackholes_group,
    enemy_lasers,
    plasma_group)
from level_config import get_level_config, load_background_images
from vfx_transition import Transition # <-- Standard transition (for level warp)
from vfx_level_star import FastStarVFX
from vfx_player_thruster import ThrusterVFX
from vfx_level_transition import LevelTransition # <-- Win/Lose transition (with color)
from vfx_level_comet import Comet

# music for game
def play_music(song_path):
    try:
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.set_volume(0.6) # main song volume
        pygame.mixer.music.play() # play the song without looping
        print(f"Playing music: {song_path}") # for song print and debug
    except Exception as e:
        print(f"Error loading music: {e}")

current_song = 'song1' # Track the current song
is_paused = False # Track if the game music is paused or not
song2_path = os.path.join('audio', 'Cyberpunk Background Music.mp3')
song1_path = os.path.join('audio', 'Dark Techno EBM Background Music.mp3')

# Play initial song on start
play_music(song1_path)



def draw_scrolling_bg(surface, background_list, state, speed=3):
    screen_width = surface.get_width()
    screen_height = surface.get_height()
    state['y'] += speed
    
    num_images = len(background_list) # keep track of our list of images to loop
    total_height = screen_height * num_images # get the total height of all pictures
    
    if state['y'] >= total_height:
        state['y'] -= total_height
        
    # add first image again to loop seamlessly
    imgs_to_draw = background_list + [background_list[0]] 
    
    for i, img in enumerate(imgs_to_draw):
        y_pos = state['y'] - i * screen_height # preserve original scroll direction
        
        if y_pos < screen_height and y_pos + screen_height > 0:
            # create rectangle for screen size to check if we should draw img or not / do not draw all images only the one on screen
            source_rect = pygame.Rect(0, 0, screen_width, screen_height) 
            
            if y_pos < 0:
                source_rect.top = -y_pos
                source_rect.height = screen_height + y_pos
            elif y_pos + screen_height > screen_height:
                source_rect.height = screen_height - y_pos
                
            surface.blit(img, (0, max(y_pos, 0)), area=source_rect)



def spawn_enemy(level_config):
    x = random.randint(80, config.SCREEN_WIDTH - 80)
    y = -80 # spawn above screen

    enemy_type = random.choices(
        level_config['enemy_types'],
        weights=level_config['enemy_weights'],
        k=1
    )[0]

    enemy = characterClass.Character(enemy_type, x, y, 0.5, 1)
    enemy_group.add(enemy)
    
    enemy.flip = random.choice([True, False])

STAR_COUNT = 150 # Number of fast-moving stars
STAR_SPEED = 10 # Star scroll speed (faster than background speed of 2)
STAR_COLOR = config.WHITE # Use WHITE for simplicity, or config.CAYAN for sci-fi

def initialize_star_field(screen_width, screen_height, count):
    stars = []
    for _ in range(count):
        stars.append({
            'x': random.randint(0, screen_width),
            'y': random.randint(0, screen_height),
            'size': random.randint(1, 2) # Vary size for a better effect
        })
    return stars

# Global variable to store and manage the star field state
star_field_state = {'stars': initialize_star_field(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, STAR_COUNT)}



# ____ main ____
def start_game(level_number=2):
    global current_song
    global player, thruster_vfx, star_vfx, health_bar, shield_bar, level_background_list, wave_count 
    
    # Get level configuration
    level_config = get_level_config(level_number)
    print(f"Starting {level_config['name']}")
    config.target_score = level_config.get('target_score', 0)

    star_vfx = FastStarVFX(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

    initial_comet_count = 1
    global comets, comet_spawn_timer
    comets = [Comet(config.SCREEN_WIDTH, config.SCREEN_HEIGHT) for _ in range(initial_comet_count)]
    comet_spawn_interval = 240 
    comet_spawn_timer = 0
    
    # Load background
    level_background_list = load_background_images(level_config)


    # --- Ensure global sprite groups exist and are fresh (use .empty() to keep same Group objects) ---
    enemy_group.empty()
    asteroid_group.empty()
    rockets_group.empty()
    explosion_group.empty()
    heavyLaser_group.empty()
    blackholes_group.empty()
    player_lasers.empty()
    enemy_beam_group.empty()
    enemy_lasers.empty()
    plasma_group.empty()

    # --- Create fresh player & UI objects for this run ---
    # create player object
    player = characterClass.Character('player', 950, 750, 2, 10)
    thruster_vfx = ThrusterVFX(player)

    # ensure player's projectile container is a Group and linked
    player.lasers = player_lasers
    player.asteroid_group = asteroid_group
    player.enemy_group = enemy_group

    # create player laserLine
    player_beam = LaserLine(player, is_player=True)
    player_beam.asteroid_group = asteroid_group
    player_beam.enemy_group = enemy_group
    player_beam.blackholes_group = blackholes_group

    health_bar = characterClass.HealthBar(55, 797, player.health, player.health)
    shield_bar = characterClass.HealthBar(55, 817, player.shield, player.shield)

    # reset input flags so stale state doesn't persist
    config.moving_left = config.moving_right = config.moving_up = config.moving_down = False
    config.shooting = config.heavy_shooting = config.rocket = config.laserLine_fire = config.plasma_shooting = False
    config.score = 0

    # clear pending events from last game played
    pygame.event.clear()

    # Game state variables
    playing = True
    scroll_speed = 2
    scroll_y = 0 # background y scroll
    wave_count = 1
    pending_spawns = 0 # track how many enemies are left in current wave

    # Spawn events (use local event ids so no conflict)
    SPAWN_EVENT = pygame.USEREVENT + 1
    SPAWN_SINGLE_EVENT = pygame.USEREVENT + 2
    spawn_interval = level_config['enemy_spawn_interval']
    pygame.time.set_timer(SPAWN_EVENT, spawn_interval)


    while playing:
        config.frameRate.tick(config.FPS) # get time and frame rate (loop rate)
        config.game_window.fill(config.BLACK)

        if player.health <= 0:
            print("You died, health is: ", player.health, ", with a score of:", config.score)
            
            # --- START OF DEATH TRANSITION LOGIC (First Check) ---
            mission_complete = config.score >= config.target_score
            outcome_color = "green" if mission_complete else "red"
            
            global transition
            # *** FIX: Use LevelTransition here with outcome_color ***
            transition = LevelTransition(config.game_window, outcome_color=outcome_color)
            
            # Return a temporary state to trigger the transition effect in the main loop
            return "death_transition"
            # --- END OF DEATH TRANSITION LOGIC ---
        
        draw_scrolling_bg(config.game_window, level_background_list, config.scroll_state, speed=2)
        
        # 2. Update and Draw the new Fast Star VFX (ADD/REPLACE OLD LOGIC WITH THIS)
        star_vfx.update()
        star_vfx.draw(config.game_window)

        comet_spawn_timer += 1
        if comet_spawn_timer > comet_spawn_interval:
            comets.append(Comet(config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            comet_spawn_timer = 0
            
        # Update & draw comets
        for comet in comets:
            comet.update(scroll_speed)
            comet.draw(config.game_window)

        is_moving = config.moving_left or config.moving_right or config.moving_up or config.moving_down
        thruster_vfx.update(is_moving, scroll_speed)

        # black Hole and Quark star (only if enabled for this level)
        if level_config['blackholes_enabled'] and random.random() < 0.00125:
            bh = BlackHole()
            blackholes_group.add(bh)
        # blackhole and quark group maps for gravity effects
        groups_map = {
            'player': player,
            'enemy_group': enemy_group,
            'asteroids': asteroid_group,
            'player_lasers': player_lasers ,
            'enemy_lasers': enemy_lasers,
            'rockets_group': rockets_group,
        }
        for bh in list(blackholes_group):
            bh.update(groups_map)
            bh.draw(config.game_window)


 
        # __ Explosions for death __
        for exp in explosion_group:
            explosion_group.update()
            exp.draw(config.game_window)

        for rocket in rockets_group:
            rocket.update()
            rocket.draw()
        
        if config.rocket and level_config['weapons']['rocket']:
            player.shoot_rocket(enemy_group, rockets_group, asteroid_group)
        
        if random.random() < level_config['asteroid_spawn_rate']:
            x = random.randint(50, config.SCREEN_WIDTH - 50)
            asteroid = Asteroid(x, -50, scale=1.0, health=20)
            asteroid_group.add(asteroid)
            
        for asteroid in asteroid_group:
            asteroid.update(asteroid_group, player)
            asteroid.draw(config.game_window)


        # update and draw enemies
        for enemy in enemy_group:
            enemy.update_enemy(config.SCREEN_HEIGHT)
            enemy.draw()
            enemy.update_lasers()
            enemy.update(player)
            enemy.ai_shoot(player, enemy_group, asteroid_group) # ai_shooting plain laser
            enemy.ai_shoot_heavy(player, enemy_group, asteroid_group)
            enemy.ai_shoot_rocket(player, rockets_group, asteroid_group)
            if enemy.character_type == "enemy4":
                enemy.ai_shoot_laserline(player, asteroid_group=asteroid_group, laserline_group=enemy_beam_group, blackholes=blackholes_group)
            if enemy.character_type == "enemy5":
                enemy.ai_shoot_enemy5(player, enemy_group, asteroid_group)
            if enemy.character_type == "enemy6":
                enemy.ai_shoot_plasma(player, asteroid_group, plasma_group)
            if enemy.character_type == "enemy7":  
                enemy.ai_enemy7_shoot(player, enemy_group, asteroid_group, rockets_group, plasma_group)

            


        # enemy laserline
        for beam in enemy_beam_group:
            beam.update(asteroid_group, enemy_group, player, blackholes_group)
            beam.draw(config.game_window)

        # lasers
        for laser in player_lasers:
            laser.update()
            laser.draw()
        # if player shoots (only if weapon is enabled for this level)
        if config.shooting and level_config['weapons']['laser']:
            player.shoot_laser(
                target_player=player,
                target_enemy_group=enemy_group,
                asteroid_group=asteroid_group
            )
        player.update_lasers()

        # laserline player shooting (only if weapon is enabled for this level)
        if level_config['weapons']['laser_line']:
            if config.laserLine_fire: # if we are shooting
                player_beam.trigger(True)
            else:
                player_beam.trigger(False)
            player_beam.update(asteroid_group, enemy_group, player, blackholes_group)
            player_beam.draw(config.game_window)

        # plasma shot (only if weapon is enabled for this level)
        if config.plasma_shooting and level_config['weapons']['plasma']:
            player.shoot_plasma(enemy_group, asteroid_group, rockets_group)
        for plasma in plasma_group:
            plasma.update()
            plasma.draw()



        # heavy laser (only if weapon is enabled for this level)
        heavyLaser_group.draw(config.game_window)
        heavyLaser_group.update()
        
        if getattr(config, "heavy_shooting", False) and level_config['weapons']['heavy_laser']:
            player.shoot_heavy(
                target_player=player,
                target_enemy_group=enemy_group,
                asteroid_group=asteroid_group
            )

        # check for death after blackhole updates (blackholes can instantly kill player)
        if player.health <= 0:
            print("You died, health is: ", player.health, ", with a score of:", config.score)
            
            # --- START OF DEATH TRANSITION LOGIC (Second Check) ---
            mission_complete = config.score >= config.target_score
            outcome_color = "green" if mission_complete else "red"
            
            # *** FIX: Use LevelTransition here with outcome_color ***
            transition = LevelTransition(config.game_window, outcome_color=outcome_color)
            
            # Return a temporary state to trigger the transition effect in the main loop
            return "death_transition"
            # --- END OF DEATH TRANSITION LOGIC ---
            
        thruster_vfx.draw(config.game_window)
        
        player.draw()
        player.update(player)

        
        # movement 
        player.movement(config.moving_left, config.moving_right, config.moving_up, config.moving_down)


        # ___ UI ____
        # health
        health_bar.draw(player.health, shield=False)
        menu.drawText(f'Health:', config.font, config.WHITE, 10, 790)
        # shield
        shield_bar.draw(player.shield, shield=True)
        menu.drawText(f'Shield:', config.font, config.WHITE, 10, 810)
        # score
        menu.drawText(f'Score: {config.score} / {config.target_score}', config.font, config.WHITE, 10, 830)
        # wave count
        menu.drawText(f'Waves: {wave_count}', config.font, config.RED, 10, 870)



        if getattr(config, "motherShip_boss_active", False):
            boss_present = any(e.character_type == "enemy8" for e in enemy_group) # keep track if there is a carrier mothership in the group(exist)
            if boss_present:
                config.motherShip_boss_active = True
            # Only clear the flag if it was active and there are NO boss enemies left
            elif not boss_present and config.mothership_wave < wave_count : # if now carrier boss and we are in diffrent wave than boss spawn wave
                config.motherShip_boss_active = False
        


        # music switching logic
        if not is_paused:
            if not pygame.mixer.music.get_busy(): # check if song is still playing
                if current_song == 'song1':
                    current_song = 'song2'
                    play_music(song1_path)
                elif current_song == 'song2':
                    current_song = 'song3'
                    play_music(song2_path)
                else:
                    current_song = 'song1'
                    play_music(song1_path)
            

        # Run garbage collector here to clean old object where it can
        gc.enable()
        gc.collect(True) 

        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
                
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: config.moving_left = True 
                if event.key == pygame.K_RIGHT: config.moving_right = True
                if event.key == pygame.K_UP:    config.moving_up = True
                if event.key == pygame.K_DOWN:  config.moving_down = True
                if event.key == pygame.K_a: config.shooting = True
                if event.key == pygame.K_d: config.heavy_shooting = True
                if event.key == pygame.K_s: config.rocket = True
                if event.key == pygame.K_w: config.laserLine_fire = True
                if event.key == pygame.K_q: config.plasma_shooting = True
                
                if event.key == pygame.K_ESCAPE: 
                    return "menu"
                
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:  config.moving_left = False
                if event.key == pygame.K_RIGHT: config.moving_right = False
                if event.key == pygame.K_UP:    config.moving_up = False
                if event.key == pygame.K_DOWN:  config.moving_down = False
                if event.key == pygame.K_a: config.shooting = False
                if event.key == pygame.K_d: config.heavy_shooting = False
                if event.key == pygame.K_s: config.rocket = False
                if event.key == pygame.K_w: config.laserLine_fire = False
                if event.key == pygame.K_q: config.plasma_shooting = False
                
 
            # _______ Spawn enemy waves ________
            if event.type == SPAWN_EVENT: # 12s
                # if next wave is a mothership (only if enabled for this level)
                if (level_config['mothership_enabled'] and 
                    not getattr(config, "motherShip_boss_active", False) and 
                    wave_count in config.motherShip_boss_waves):
                    mx = config.SCREEN_WIDTH
                    my = 120
                    mothership = characterClass.Mothership(mx, my, scale=0.75, velocity=1.2)
                    enemy_group.add(mothership)
                    config.motherShip_boss_active = True
                    config.mothership_wave = wave_count # keep track of wave count to only spawn once per wave, if left out we spawn new enemy when old one dies
                
                else:
                    # Calculate how many enemies to spawn this wave
                    enemies_to_spawn = wave_count * level_config['wave_size_multiplier']
                    pending_spawns = enemies_to_spawn
                    wave_count += 1          # next wave is 1 larger
                    spawn_enemy(level_config)
                    pending_spawns -= 1          # we spawned one so less pending now
                    if pending_spawns > 0:
                        pygame.time.set_timer(SPAWN_SINGLE_EVENT, 1000) # 100ms delay between enemies
                    
            # _____ Stagger enemy spawns _____
            if event.type == SPAWN_SINGLE_EVENT:
                spawn_enemy(level_config) # create enemy
                pending_spawns -= 1
                if pending_spawns <= 0:
                    pygame.time.set_timer(SPAWN_SINGLE_EVENT, 0) # stop stagger timer
            
                            
        pygame.display.update()

    return "menu"


# # Main Loop Controller
transition = None #
game_state = "menu"
current_level = 2

while game_state != "exit":
    if game_state == "menu":
        config.channel_8.stop()
        config.channel_7.stop()
        pygame.event.clear()
        game_state = menu.menu_screen()
        pygame.event.clear()

    elif game_state == "play":
        game_state = start_game(current_level)

    elif game_state == "level_select":
        pygame.event.clear()
        selected_level = menu.level_select()
        if isinstance(selected_level, int):
            current_level = selected_level
            # Use the standard Transition for level warp-in
            transition = Transition(config.game_window) 
            game_state = "transition_in" 
        elif selected_level == "menu":
            game_state = "menu"
    # fade in
    elif game_state == "transition_in":
        level_config = get_level_config(current_level)
        level_background_list = load_background_images(level_config)
        is_running = transition.warp_in()
        config.game_window.fill(config.BLACK)
        draw_scrolling_bg(config.game_window, level_background_list, config.scroll_state, speed=0)

        transition.draw()
        
        pygame.display.update()
        config.frameRate.tick(config.FPS)
        
        if not is_running:
            game_state = "play"
            transition = None
    
    # --- New Death Transition State ---
    elif game_state == "death_transition":
        config.frameRate.tick(config.FPS)
        
        # 1. Draw the Background (Bottom Layer)
        draw_scrolling_bg(config.game_window, level_background_list, config.scroll_state, speed=0) 
        
        # 2. Draw all Game Objects (Middle Layers) in the correct order
        star_vfx.draw(config.game_window)
        thruster_vfx.draw(config.game_window)

        # Draw Sprite Groups (The final explosion/laser frame)
        blackholes_group.draw(config.game_window)
        explosion_group.draw(config.game_window)
        rockets_group.draw(config.game_window)
        asteroid_group.draw(config.game_window)
        enemy_group.draw(config.game_window)
        for beam in enemy_beam_group:
            beam.draw(config.game_window)
        
        player_lasers.draw(config.game_window)
        plasma_group.draw(config.game_window)
        heavyLaser_group.draw(config.game_window)
        
        # Draw the Player (where it died)
        player.draw() 
        
        # Draw the UI (On top of game action)
        health_bar.draw(player.health, shield=False)
        menu.drawText(f'Health:', config.font, config.WHITE, 10, 790)
        shield_bar.draw(player.shield, shield=True)
        menu.drawText(f'Shield:', config.font, config.WHITE, 10, 810)
        menu.drawText(f'Score: {config.score} / {config.target_score}', config.font, config.WHITE, 10, 830)
        menu.drawText(f'Waves: {wave_count}', config.font, config.RED, 10, 870) 
        
        
        # 3. Run and Draw the Transition (TOP LAYER)
        # We now know 'transition' is a LevelTransition object created in start_game
        is_running = transition.warp_out() 
        transition.draw() 
        
        pygame.display.update()
        
        if not is_running:
            transition.reset_to_max() 
            game_state = "result_transition_in"
    
    elif game_state == "result_transition_in":
        config.frameRate.tick(config.FPS)
        
        config.game_window.fill(config.BLACK) 
        is_running = transition.warp_in()
        transition.draw()
        
        pygame.display.update()
        
        if not is_running:
            transition = None
            game_state = "result_screen"
            
    # --- Existing Result Screen State ---
    elif game_state == "result_screen":
        game_state = menu.result_screen()

pygame.quit()