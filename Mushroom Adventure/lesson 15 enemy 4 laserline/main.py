import pygame
import os
from pygame import mixer
import random
import config
import shipClass

from sprite_groups import (
    enemy_group,
    player_lasers,
    heavyLaser_group,
    rockets_group,
    asteroid_group,
    enemy_beam_group,
    icebullet_group
)
from asteroid import Asteroid
from projectiles import LaserLine, IceBullet

font = pygame.font.SysFont('', 25)

# create player object
player = shipClass.Ship('player', 800, 700, 1, 10)

# create player laserLine
player_beam = LaserLine(player, is_player=True)

# draw a text for ui
def drawText(text, font_obj, text_col, text_x, text_y):
    img = font_obj.render(text, True, text_col)
    config.game_window.blit(img, (text_x, text_y))

# healthbar
health_bar = shipClass.HealthBar(10, 10, player.health, player.health)

# music for game
def play_music(song_path):
    try:
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.set_volume(0.6)  # main song volume
        pygame.mixer.music.play()  # play the song without looping
        print(f"Playing music: {song_path}")  # for song print and debug
    except Exception as e:
        print(f"Error loading music: {e}")

current_song = 'song1'  # Track the current song
is_paused = False  # Track if the game music is paused or not
song1_path = os.path.join('audio', 'Cyberpunk Gaming Energy by Infraction [No Copyright Music]  Let us Play [q-3xl6u34Ho].mp3')

# Play initial song on start
play_music(song1_path)

# background y scroll
scroll_y = 0

def draw_scrolling_bg(surface, image, state, speed=3):
    state['y'] += speed
    height = surface.get_height()

    if state['y'] >= height:
        state['y'] = 0

    surface.blit(image, (0, state['y'] - height))
    surface.blit(image, (0, state['y']))

SPAWN_EVENT = pygame.USEREVENT + 1
SPAWN_SINGLE_EVENT = pygame.USEREVENT + 2  # for staggered spawns

spawn_interval = 12000  # 12 sec (60000 for 1 min)
pygame.time.set_timer(SPAWN_EVENT, spawn_interval)

wave_count = 1
pending_spawns = 0  # track how many enemies are left in current wave

def spawn_enemy():
    x = random.randint(80, config.SCREEN_WIDTH - 80)
    y = -50  # spawn above screen

    enemy_type = random.choices(
        ['enemy1', 'enemy2', 'enemy3', 'enemy4', 'enemy5'],
        weights=[3, 3, 3, 2, 1],  # enemy 1,2,3 is 3 times more likley to spawn
        k=1
    )[0]

    enemy = shipClass.Ship(enemy_type, x, y, 0.5, 1)
    enemy_group.add(enemy)
    enemy.flip = random.choice([True, False])


playing = True
while playing:
    # capture dt in milliseconds so projectile updates that expect dt work correctly
    dt_ms = config.frameRate.tick(config.FPS)  # get time and frame rate (loop rate)
    dt = dt_ms / 1000.0

    config.game_window.fill(config.BLACK)

    if player.health <= 0:
        playing = False
        print("You died, health is: ", player.health, ", with a score of:", config.score)

    # draw scrolling background - note: uses whatever config.scale_bg (or similar) you already set
    # keep your original call (if config.scale_bg is missing, swap to config.background_list[0] or similar)
    # I'm preserving your original call to avoid changing unrelated behavior.
    draw_scrolling_bg(config.game_window, config.scale_bg, config.scroll_state, speed=3)

    # player
    player.draw()
    player.update(player)

    # rockets
    for rocket in list(rockets_group):
        rocket.update()
        rocket.draw()

    if config.rocket:
        player.shoot_rocket(enemy_group, rockets_group, asteroid_group)

    # random asteroid spawn
    if random.random() < 0.005:
        x = random.randint(50, config.SCREEN_WIDTH - 50)
        asteroid = Asteroid(x, -50, scale=1.0, health=20)
        asteroid_group.add(asteroid)

    # update asteroids
    for asteroid in list(asteroid_group):
        asteroid.update(asteroid_group, player)
        asteroid.draw(config.game_window)

    # update and draw enemies
    for enemy in list(enemy_group):
        enemy.update_enemy(config.SCREEN_HEIGHT)
        enemy.draw()
        enemy.update_lasers()
        enemy.update(player)

        # AI firing logic
        enemy.ai_shoot(player, enemy_group, asteroid_group)  # ai_shooting plain laser
        enemy.ai_shoot_heavy(player, enemy_group, asteroid_group)
        enemy.ai_shoot_rocket(player, rockets_group, asteroid_group)

        if enemy.character_type == "enemy4":
            enemy.ai_shoot_laserline(player, asteroid_group=asteroid_group, laserline_group=enemy_beam_group)
        if enemy.character_type == "enemy5":
            enemy.ai_shoot_enemy5(player, enemy_group, asteroid_group)

    # enemy laserline
    for beam in list(enemy_beam_group):
        beam.update(asteroid_group, enemy_group, player)
        beam.draw(config.game_window)

    # player normal lasers
    for laser in list(player_lasers):
        laser.update()
        laser.draw()

    # if player shoots normal laser
    if config.shooting:
        player.shoot_laser(
            target_enemy_group=enemy_group,
            asteroid_group=asteroid_group
        )
    player.update_lasers()

    # ---- Ice bullets (player) ----
    # update and draw ice/freezing bullets (projectiles.IceBullet expects update(dt) style)
    for ib in list(icebullet_group):
        try:
            # IceBullet implementations may have different update signatures;
            # attempt to call with dt first, fallback to parameterless update()
            ib.update(dt)
        except TypeError:
            ib.update()
        # many IceBullet/FreezeBullet classes provide draw method, else blit image if available
        if hasattr(ib, "draw"):
            ib.draw(config.game_window)
        else:
            if hasattr(ib, "image") and hasattr(ib, "rect"):
                config.game_window.blit(ib.image, ib.rect)

    # laserline player shooting (beam)
    if config.laserLine_fire:  # if we are shooting
        player_beam.trigger(True)
    else:
        player_beam.trigger(False)
    player_beam.update(asteroid_group, enemy_group, player)
    player_beam.draw(config.game_window)

    # heavy lasers group
    heavyLaser_group.draw(config.game_window)
    heavyLaser_group.update()

    if getattr(config, "heavy_shooting", False):
        player.shoot_heavy(
            target_player=player,
            target_enemy_group=enemy_group,
            asteroid_group=asteroid_group
        )

    # movement
    player.movement(config.moving_left, config.moving_right, config.moving_up, config.moving_down)

    # ---- UI ----
    health_bar.draw(player.health)
    drawText(f'Score: {config.score}', font, config.WHITE, 10, 25)

    # music switching logic
    if not is_paused:
        if not pygame.mixer.music.get_busy():  # check if song is still playing
            current_song = 'song1'
            play_music(song1_path)

    # events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                config.moving_left = True
            if event.key == pygame.K_RIGHT:
                config.moving_right = True
            # if event.key == pygame.K_UP:
            #     config.moving_up = True
            # if event.key == pygame.K_DOWN:
            #     config.moving_down = True
            if event.key == pygame.K_a:
                config.shooting = True
            if event.key == pygame.K_d:
                config.heavy_shooting = True
            if event.key == pygame.K_s:
                config.rocket = True
            if event.key == pygame.K_w:
                config.laserLine_fire = True

            # fire freeze/ice bullet with F (player only)
            if event.key == pygame.K_f:
                # use the Ship method that creates freeze bullet (shoot_freeze / shoot_ice)
                # your Ship class must implement shoot_freeze(target_enemy_group)
                try:
                    player.shoot_freeze(enemy_group)
                except Exception:
                    # fallback: create IceBullet directly if needed (expects pos or args)
                    try:
                        ib = IceBullet(player.rect.center)
                        icebullet_group.add(ib)
                        if hasattr(config, 'icebullet_fx'):
                            config.channel_13.play(config.icebullet_fx)
                    except Exception:
                        pass

            if event.key == pygame.K_ESCAPE:
                playing = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                config.moving_left = False
            if event.key == pygame.K_RIGHT:
                config.moving_right = False
            if event.key == pygame.K_UP:
                config.moving_up = False
            if event.key == pygame.K_DOWN:
                config.moving_down = False
            if event.key == pygame.K_a:
                config.shooting = False
            if event.key == pygame.K_d:
                config.heavy_shooting = False
            if event.key == pygame.K_s:
                config.rocket = False
            if event.key == pygame.K_w:
                config.laserLine_fire = False

        # _______ Spawn enemy waves ________
        if event.type == SPAWN_EVENT:  # 12s
            pending_spawns = wave_count  # number to spawn this wave
            wave_count += 1  # next wave is 1 larger
            spawn_enemy()
            pending_spawns -= 1  # we spawned one so less pending now
            if pending_spawns > 0:
                pygame.time.set_timer(SPAWN_SINGLE_EVENT, 1000)  # 100ms delay between enemies

        # _____ Stagger enemy spawns _____
        if event.type == SPAWN_SINGLE_EVENT:
            spawn_enemy()  # create enemy
            pending_spawns -= 1
            if pending_spawns <= 0:
                pygame.time.set_timer(SPAWN_SINGLE_EVENT, 0)  # stop stagger timer

    pygame.display.update()

pygame.quit()
