import pygame
import random
import config
import characterClass


from sprite_groups import enemy_group, player_lasers, enemy_lasers






# background y scroll
scroll_y = 0

def draw_scrolling_bg(surface, image, state, speed=4):
    state['y'] += speed
    height = surface.get_height()

    if state['y'] >= height:
        state['y'] = 0
        
    surface.blit(image, (0, state['y'] - height))
    surface.blit(image, (0, state['y']))


#create player object
player = characterClass.Character('player', 800, 700, 2, 10)

SPAWN_EVENT = pygame.USEREVENT + 1
SPAWN_SINGLE_EVENT = pygame.USEREVENT + 2 # for staggered spawns

spawn_interval = 12000 # 12 sec (60000 for 1 min)
pygame.time.set_timer(SPAWN_EVENT, spawn_interval)

wave_count = 1
pending_spawns = 0 # track how many enemies are left in current wave

def spawn_enemy():
    x = random.randint(80, config.SCREEN_WIDTH - 80)
    y = -50 # spawn above screen
    enemy_type = random.choice(['enemy1', 'enemy2', 'enemy3'])
    enemy = characterClass.Character(enemy_type, x, y, 0.5, 1)
    enemy_group.add(enemy)
    
    if random.randint(1, 2) == 1:
        enemy.flip = True
    else:
        enemy.flip = False




playing = True
while playing:
    config.frameRate.tick(config.FPS) # get time and frame rate (loop rate)
    config.game_window.fill(config.BLACK)
    
    
    
    draw_scrolling_bg(config.game_window, config.scale_bg, config.scroll_state, speed=3)
    
    
    player.draw()
    player.update(player)
        
   
    # update and draw enemies
    for enemy in enemy_group:
        enemy.update_enemy(config.SCREEN_HEIGHT)
        enemy.draw()



    # lasers
    for laser in player_lasers:
        laser.update()
        laser.draw()
    # if player shoots
    if config.shooting:
        player.shoot_laser(
            target_enemy_group=enemy_group
        )
    player.update_lasers()

    # ai lasers
    for enemy in enemy_group:
        enemy.update_lasers()
        enemy.update(player)
        enemy.ai_shoot(player, enemy_group) # ai_shooting



    # movement 
    player.movement(config.moving_left, config.moving_right, config.moving_up, config.moving_down)
    
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
            
            if event.key == pygame.K_ESCAPE: playing = False
            
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:  config.moving_left = False
            if event.key == pygame.K_RIGHT: config.moving_right = False
            if event.key == pygame.K_UP:    config.moving_up = False
            if event.key == pygame.K_DOWN:  config.moving_down = False
            if event.key == pygame.K_a: config.shooting = False
            



        # _______ Spawn enemy waves ________
        if event.type == SPAWN_EVENT:# 12s
            pending_spawns = wave_count # number to spawn this wave
            wave_count += 1             # next wave is 1 larger
            spawn_enemy()
            pending_spawns -= 1         # we spawned one so less pending now
            if pending_spawns > 0:
                pygame.time.set_timer(SPAWN_SINGLE_EVENT, 1000) # 100ms delay between enemies
                
        # _____ Stagger enemy spawns _____\
        if event.type == SPAWN_SINGLE_EVENT:
            spawn_enemy()               # create enemy
            pending_spawns -= 1
            if pending_spawns <= 0:
                pygame.time.set_timer(SPAWN_SINGLE_EVENT, 0) # stop stagger timer
        
            
            
            

    pygame.display.update()

pygame.quit()