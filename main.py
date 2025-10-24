# main_mushroom.py
# 主文件（Mushroom mode），保留 Space UI（menu.py + config.py）
import pygame
import random
import math
import time

import config
import menu

# 尽量兼容不同项目组织：尝试从可能的模块导入 Enemy / Explosion
try:
    from spaceObjects import Enemy  # 常见命名
except Exception:
    try:
        from shipClass import Enemy
    except Exception:
        try:
            from Level1 import Enemy
        except Exception:
            Enemy = None  # 如果都没有，后面会用简单占位实现

import config1
import main_menu

pygame.init()

# ---------------- helper: try to import Explosion if provided by project ----------------
ExplosionClass = None
try:
    # some projects may export an Explosion sprite class
    from shipClass import Explosion as ExplosionClass
except Exception:
    try:
        from spaceObjects import Explosion as ExplosionClass
    except Exception:
        ExplosionClass = None

# ---------------- Screen & shared objects ----------------
GAME_WINDOW = config1.game_window
FPS = getattr(config1, "FPS", 60)
clock = config1.frameRate

SCREEN_W = config1.SCREEN_WIDTH
SCREEN_H = config1.SCREEN_HEIGHT

# ---------------- draw_scrolling_bg (reuse the same logic used in original main.py) ----------------
def draw_scrolling_bg(surface, background_list, state, speed=3):
    screen_width = surface.get_width()
    screen_height = surface.get_height()
    state['y'] += speed
    num_images = len(background_list)
    total_height = screen_height * num_images
    if state['y'] >= total_height:
        state['y'] -= total_height
    imgs_to_draw = background_list + [background_list[0]]
    for i, img in enumerate(imgs_to_draw):
        y_pos = state['y'] - i * screen_height
        if y_pos < screen_height and y_pos + screen_height > 0:
            source_rect = pygame.Rect(0, 0, screen_width, screen_height)
            if y_pos < 0:
                source_rect.top = -y_pos
                source_rect.height = screen_height + y_pos
            elif y_pos + screen_height > screen_height:
                source_rect.height = screen_height - y_pos
            surface.blit(img, (0, max(y_pos, 0)), area=source_rect)

# ---------------- Player (mushroom) ----------------
class Player:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.speed = 400.0
        self.image = None
        try:
            img = pygame.image.load("img/player/mushroom.png").convert_alpha()
            # scale to reasonable size relative to screen height
            target_h = int(0.08 * SCREEN_H)
            scale = target_h / img.get_height()
            self.image = pygame.transform.scale(img, (int(img.get_width()*scale), int(img.get_height()*scale)))
            self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        except Exception as e:
            print("Couldn't load player image:", e)
            self.image = None
            self.rect = pygame.Rect(int(self.pos.x)-16, int(self.pos.y)-16, 32, 32)
        self.health = 100
        self.max_health = 100
        self.invuln_until = 0

    def update_rect(self):
        if isinstance(self.rect, pygame.Rect):
            self.rect.center = (int(self.pos.x), int(self.pos.y))

    def move(self, dt, left, right, up, down):
        dx = 0
        dy = 0
        if left: dx -= 1
        if right: dx += 1
        if up: dy -= 1
        if down: dy += 1
        if dx != 0 or dy != 0:
            v = pygame.Vector2(dx, dy)
            v = v.normalize() * self.speed * dt
            self.pos += v
            # clamp horizontally in visible area
            self.pos.x = max(40, min(SCREEN_W - 40, self.pos.x))
            self.pos.y = max(120, min(SCREEN_H - 40, self.pos.y))
            self.update_rect()

    def draw(self, surf):
        if self.image:
            surf.blit(self.image, self.image.get_rect(center=(int(self.pos.x), int(self.pos.y))))
        else:
            pygame.draw.circle(surf, (200,255,200), (int(self.pos.x), int(self.pos.y)), 18)

    def take_damage(self, dmg):
        now = pygame.time.get_ticks()
        if now < self.invuln_until:
            return
        self.health -= dmg
        self.invuln_until = now + 400
        if self.health < 0:
            self.health = 0

# ---------------- Projectiles ----------------
class PlayerBullet:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, -900.0)
        self.radius = 6
        self.damage = 25
        self.active = True

    def update(self, dt):
        if not self.active: return
        self.pos += self.vel * dt
        if self.pos.y < -50: self.active = False

    def draw(self, surf):
        if not self.active: return
        pygame.draw.circle(surf, (255,220,120), (int(self.pos.x), int(self.pos.y)), self.radius)
        # glow
        pygame.draw.circle(surf, (255,180,80), (int(self.pos.x), int(self.pos.y)), self.radius+1, 1)

class PlayerLaser:
    def __init__(self):
        self.cooldown = 0.25
        self.timer = 0.0
        self.active = False
        self.duration = 0.09
        self.life = 0.0
        self.start = pygame.Vector2()
        self.end = pygame.Vector2()
        self.damage = 40

    def try_fire(self, start):
        if self.timer > 0:
            return False
        self.start = start.copy()
        self.end = pygame.Vector2(self.start.x, -1000)  # straight up
        self.timer = self.cooldown
        self.active = True
        self.life = self.duration
        return True

    def update(self, dt):
        if self.timer > 0: self.timer -= dt
        if self.active:
            self.life -= dt
            if self.life <= 0:
                self.active = False

    def draw(self, surf):
        if not self.active: return
        glow = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        pygame.draw.line(glow, (120,180,255,90), self.start, self.end, 22)
        pygame.draw.line(glow, (200,220,255,200), self.start, self.end, 8)
        pygame.draw.line(glow, (255,255,255,220), self.start, self.end, 2)
        surf.blit(glow, (0,0))

class IceShot:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, -520)
        self.radius = 9
        self.damage = 30
        self.freeze_ms = 2000
        self.active = True

    def update(self, dt):
        if not self.active: return
        self.pos += self.vel * dt
        if self.pos.y < -50: self.active = False

    def draw(self, surf):
        if not self.active: return
        tip = (int(self.pos.x), int(self.pos.y - 10))
        left = (int(self.pos.x - 6), int(self.pos.y + 8))
        right = (int(self.pos.x + 6), int(self.pos.y + 8))
        pygame.draw.polygon(surf, (180,240,255), [tip, left, right])
        pygame.draw.polygon(surf, (255,255,255), [tip, left, right], 1)

class EnemyBullet:
    def __init__(self, x, y, angle_rad):
        speed = 260.0
        self.pos = pygame.Vector2(x,y)
        self.vel = pygame.Vector2(math.cos(angle_rad), math.sin(angle_rad)) * speed
        self.radius = 6
        self.damage = 12
        self.active = True

    def update(self, dt):
        if not self.active: return
        self.pos += self.vel * dt
        if (self.pos.y > SCREEN_H + 80) or (self.pos.x < -80) or (self.pos.x > SCREEN_W + 80):
            self.active = False

    def draw(self, surf):
        if not self.active: return
        pygame.draw.circle(surf, (255,100,100), (int(self.pos.x), int(self.pos.y)), self.radius)
        pygame.draw.circle(surf, (255,200,180), (int(self.pos.x), int(self.pos.y)), self.radius, 1)

# ---------------- Small helper: spawn enemy / call its shoot if available ----------------
def spawn_enemy_instance():
    if Enemy is None:
        # fallback: simple local enemy-like object
        class LocalEnemy:
            def __init__(self):
                base_img = pygame.Surface((36,36), pygame.SRCALPHA)
                pygame.draw.polygon(base_img, (180,100,120), [(18,0),(36,36),(0,36)])
                self.image = base_img
                self.pos = pygame.Vector2(random.randint(60, SCREEN_W-60), -40)
                self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
                self.hp = 60
                self.dead = False
                self.speed = random.uniform(80, 160)
                self.last_shot = 0
                self.shoot_interval = random.uniform(1.1,2.5)
            def update(self, dt):
                self.pos.y += self.speed * dt
                self.rect.center = (int(self.pos.x), int(self.pos.y))
            def draw(self, surf):
                surf.blit(self.image, self.rect)
            def take_damage(self, dmg, freeze=False):
                self.hp -= dmg
                if self.hp <= 0:
                    self.dead = True
                    return ExplosionInstance(self.pos)
                return None
            def can_shoot(self):
                return (time.time() - self.last_shot) >= self.shoot_interval
            def shoot(self, target_pos):
                self.last_shot = time.time()
                self.shoot_interval = random.uniform(1.0, 2.6)
                # create bullet mostly downward with slight angle to target
                dx = (target_pos.x - self.pos.x) + random.uniform(-40,40)
                dy = (target_pos.y - self.pos.y)
                ang = math.atan2(dy, dx)
                return EnemyBullet(self.pos.x, self.pos.y, ang)
        return LocalEnemy()
    else:
        # construct project Enemy() using project signature assumed
        try:
            e = Enemy()
            return e
        except Exception:
            # fallback similar
            return spawn_enemy_instance()

# ---------------- Explosion fallback (if project does not provide it) ----------------
class ExplosionInstance:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.timer = 0.0
        self.life = 0.6
        self.particles = [[random.uniform(-8, 8), random.uniform(-8, 8), random.uniform(40, 220)] for _ in range(22)]

    def update(self, dt):
        self.timer += dt
        # ✅ 粒子更新在这里
        for p in self.particles:
            p[0] += p[0] * 0.02
            p[1] += p[1] * 0.02
            p[2] -= 150 * dt
        return self.timer < self.life or any(p[2] > 0 for p in self.particles)

    def draw(self, surf):
        t = self.timer / self.life
        radius = 8 + 80 * t
        alpha = int(255 * (1 - t))
        surf_s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf_s, (255, 200, 80, alpha), (int(radius), int(radius)), int(radius))
        surf.blit(surf_s, (self.pos.x - radius, self.pos.y - radius), special_flags=pygame.BLEND_ADD)
        # ✅ draw 里只画，不动粒子
        for p in self.particles:
            pygame.draw.circle(surf, (255, 220, 120), (int(self.pos.x + p[0]), int(self.pos.y + p[1])), 2)


# ---------------- Main game state & lists ----------------
player = Player(SCREEN_W // 2, SCREEN_H - 200)
player_bullets = []
player_laser = PlayerLaser()
player_ices = []
enemy_bullets = []
enemies = []
explosions = []

spawn_accum = 0.0
spawn_interval = 1.2

# input flags
moving_left = moving_right = moving_up = moving_down = False

# Game loop entry (called when user selects Play)
def run_mushroom_level():
    global spawn_accum, enemies, enemy_bullets, player_bullets, player_ices, explosions
    spawn_accum = 0.0
    enemies = []
    enemy_bullets = []
    player_bullets = []
    player_ices = []
    explosions = []
    player.health = player.max_health
    player.pos.x = SCREEN_W // 2
    player.pos.y = SCREEN_H - 200

    playing = True
    game_over = False

    while playing:
        clock.tick(FPS)
        dt = clock.get_time() / 1000.0

        # process events
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    # go back to menu
                    return "menu"
                if not game_over:
                    if ev.key == pygame.K_a:  # A: normal bullet
                        player_bullets.append(PlayerBullet(player.pos.x, player.pos.y - 30))
                    if ev.key == pygame.K_s:  # S: laser
                        fired = player_laser.try_fire(player.pos)
                        if fired:
                            # detect collisions: hits all enemies crossing the vertical line
                            for en in list(enemies):
                                try:
                                    r = en.rect
                                except Exception:
                                    r = None
                                if r and r.collidepoint(player.pos.x, player.pos.y - 50):
                                    exp = None
                                    try:
                                        exp = en.take_damage(player_laser.damage)
                                    except Exception:
                                        pass
                                    if exp:
                                        explosions.append(exp if ExplosionClass is None else ExplosionClass(en.rect.center))
                                        try:
                                            enemies.remove(en)
                                        except Exception:
                                            pass
                    if ev.key == pygame.K_d:  # D: ice shot
                        player_ices.append(IceShot(player.pos.x, player.pos.y - 30))

            if ev.type == pygame.KEYUP:
                pass

        # input movement state
        keys = pygame.key.get_pressed()
        moving_left = keys[pygame.K_LEFT]
        moving_right = keys[pygame.K_RIGHT]
        moving_up = keys[pygame.K_UP]
        moving_down = keys[pygame.K_DOWN]

        if not game_over:
            # update movement
            player.move(dt, moving_left, moving_right, moving_up, moving_down)

            # update bullets
            for b in player_bullets[:]:
                b.update(dt)
                if not b.active:
                    try: player_bullets.remove(b)
                    except: pass
                else:
                    # collide with enemies
                    for en in list(enemies):
                        # many Enemy classes have rect attribute; try to use it
                        rect = getattr(en, "rect", None)
                        if rect and rect.collidepoint(b.pos.x, b.pos.y):
                            try:
                                exp = en.take_damage(b.damage)
                            except Exception:
                                exp = None
                            b.active = False
                            try: player_bullets.remove(b)
                            except: pass
                            if exp:
                                # if project has ExplosionClass, it probably expects different args; try to add returned
                                explosions.append(exp)
                                try: enemies.remove(en)
                                except: pass
                            break

            # update ice shots
            for ib in player_ices[:]:
                ib.update(dt)
                if not ib.active:
                    try: player_ices.remove(ib)
                    except: pass
                    continue
                for en in list(enemies):
                    rect = getattr(en, "rect", None)
                    # rect collision check fallback: if no rect, use pos approximate
                    collided = False
                    if rect and rect.collidepoint(int(ib.pos.x), int(ib.pos.y)):
                        collided = True
                    else:
                        # fallback if enemy has pos attr
                        ep = getattr(en, "pos", None)
                        if ep:
                            if (ep - ib.pos).length() < 24:
                                collided = True
                    if collided:
                        try:
                            exp = en.take_damage(ib.damage, freeze=True)
                        except Exception:
                            exp = None
                        ib.active = False
                        try: player_ices.remove(ib)
                        except: pass
                        if exp:
                            explosions.append(exp)
                            try: enemies.remove(en)
                            except: pass
                        break

            # update laser
            player_laser.update(dt)
            if player_laser.active:
                # damage any enemy under the laser vertical band
                for en in list(enemies):
                    rect = getattr(en, "rect", None)
                    if rect and rect.clipline((player_laser.start.x, 0, player_laser.start.x, SCREEN_H)):
                        try:
                            exp = en.take_damage(player_laser.damage)
                        except Exception:
                            exp = None
                        if exp:
                            explosions.append(exp)
                            try: enemies.remove(en)
                            except: pass

            # update enemies & their bullets
            for en in list(enemies):
                try:
                    en.update(dt)
                except TypeError:
                    # some Enemy.update expect different args
                    try:
                        en.update()
                    except Exception:
                        pass
                # if enemy has its own shoot method, try to use it; else do downward shots
                if getattr(en, "dead", False):
                    try:
                        enemies.remove(en)
                    except:
                        pass
                    continue
                # enemy shooting: if class provides can_shoot() and shoot(), use them
                shot = None
                if hasattr(en, "can_shoot") and hasattr(en, "shoot"):
                    try:
                        if en.can_shoot():
                            # en.shoot may expect target or groups; try calls with player.pos
                            shot = en.shoot(player.pos)
                    except Exception:
                        shot = None
                else:
                    # fallback: shoot downward occasionally
                    # use attribute last_shot and shoot interval if exist
                    last = getattr(en, "last_shot", None)
                    interval = getattr(en, "shoot_interval", None)
                    now = time.time()
                    if last is None:
                        en.last_shot = now
                        en.shoot_interval = random.uniform(1.0, 3.0)
                    if (time.time() - en.last_shot) > en.shoot_interval:
                        en.last_shot = time.time()
                        # angle mostly downward + small random offset
                        ang = math.pi/2 + random.uniform(-0.20, 0.20)
                        shot = EnemyBullet(getattr(en, "pos", pygame.Vector2(getattr(en,"rect",pygame.Rect(0,0,0,0)).center)).x,
                                           getattr(en, "pos", pygame.Vector2(getattr(en,"rect",pygame.Rect(0,0,0,0)).center)).y,
                                           ang)
                if shot is not None:
                    # if en.shoot returned an EnemyBullet instance -> append
                    if isinstance(shot, EnemyBullet):
                        enemy_bullets.append(shot)
                    else:
                        # maybe en.shoot added bullets to groups; ignore
                        pass

            # update enemy bullets
            for eb in enemy_bullets[:]:
                eb.update(dt)
                if not eb.active:
                    try: enemy_bullets.remove(eb)
                    except: pass
                else:
                    # simple collision with player (circle)
                    if (pygame.Vector2(eb.pos) - player.pos).length() < (eb.radius + 16):
                        player.take_damage(eb.damage)
                        try: enemy_bullets.remove(eb)
                        except: pass

            # update explosions
            for ex in explosions[:]:
                alive = True
                try:
                    alive = ex.update(dt)
                except Exception:
                    # fallback assume object finishes quickly
                    try:
                        # if ExplosionClass is provided and its instance has update method
                        alive = ex.update(dt)
                    except:
                        alive = False
                if not alive:
                    try: explosions.remove(ex)
                    except: pass

            # spawn new enemies
            spawn_accum += dt
            if spawn_accum >= spawn_interval:
                spawn_accum = 0.0
                kind = random.choices(["basic","fast","tank"], weights=[0.6,0.3,0.1])[0]
                en = spawn_enemy_instance()
                # attempt to set kind if supported
                try:
                    if hasattr(en, "kind"):
                        en.kind = kind
                except:
                    pass
                enemies.append(en)

            # if player dead
            if player.health <= 0:
                game_over = True

        # draw everything (keep UI look consistent with space)
        # draw scrolling background from config
        try:
            draw_scrolling_bg(GAME_WINDOW, config.background_list, config.scroll_state, speed=2)
        except Exception:
            GAME_WINDOW.fill((6,6,12))

        # draw game objects
        for en in enemies:
            try:
                en.draw(GAME_WINDOW)
            except Exception:
                # fallback draw rect
                rect = getattr(en, "rect", None)
                if rect:
                    pygame.draw.rect(GAME_WINDOW, (200,80,80), rect)
        for eb in list(enemy_bullets):
            eb.draw(GAME_WINDOW)
        for b in list(player_bullets):
            b.draw(GAME_WINDOW)
        for ib in list(player_ices):
            ib.draw(GAME_WINDOW)
        player_laser.draw(GAME_WINDOW)
        player.draw(GAME_WINDOW)
        for ex in list(explosions):
            try:
                ex.draw(GAME_WINDOW)
            except Exception:
                pass

        # HUD: keep similar to space UI
        try:
            config.game_window = GAME_WINDOW  # ensure menu.drawText uses same surface
            menu.drawText(f'Health: {player.health}/{player.max_health}', config.font, config.WHITE, 10, 10)
            menu.drawText(f'Score: {sum(getattr(e, "score_value", 0) for e in enemies)}', config.font, config.WHITE, 10, 40)
        except Exception:
            # fallback text
            FONT = pygame.font.SysFont(None, 36)
            GAME_WINDOW.blit(FONT.render(f"HP: {player.health}", True, (255,255,255)), (10,10))

        # if game over -> draw overlay + buttons
        if game_over:
            # darken screen a bit
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0,0,0,120))
            GAME_WINDOW.blit(overlay, (0,0))
            # Game Over text (center)
            large = pygame.font.SysFont(None, 96)
            txt = large.render("GAME OVER", True, (255,200,100))
            txt_r = txt.get_rect(center=(SCREEN_W//2, SCREEN_H//2 - 80))
            GAME_WINDOW.blit(txt, txt_r)
            small = pygame.font.SysFont(None, 44)
            sub = small.render(f"Your HP: 0", True, (240,240,240))
            sub_r = sub.get_rect(center=(SCREEN_W//2, SCREEN_H//2 - 30))
            GAME_WINDOW.blit(sub, sub_r)

            # Draw Play Again and Back buttons using menu.draw_button style
            # positions similar to original menu style (centered)
            btn_w, btn_h = 360, 90
            play_x = SCREEN_W//2 - btn_w - 20
            back_x = SCREEN_W//2 + 20
            y = SCREEN_H//2 + 30
            # colors: reuse menu colors visually (green / cyan / red style)
            play_pressed = menu.draw_button("Play Again", play_x, y, btn_w, btn_h, (0,80,0), (0,200,0))
            back_pressed = menu.draw_button("Back", back_x, y, btn_w, btn_h, (80,0,0), (255,60,60))

            pygame.display.update()

            if play_pressed:
                # restart by re-entering the run loop: just reset state and continue
                return run_mushroom_level()
            if back_pressed:
                return "menu"

            # small cap on FPS while in game over screen
            clock.tick(30)
            continue

        pygame.display.update()

    return "menu"

# If run as script, show menu first (use space menu)
if __name__ == "__main__":
    # simple controller to allow entering menu/play
    state = "menu"
    while True:
        if state == "menu":
            state = menu.menu_screen()  # uses your existing menu; expects "play" to start
        if state == "play":
            res = run_mushroom_level()
            state = res
