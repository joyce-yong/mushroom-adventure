# ui_cursor.py
import pygame
import os

# === CONFIG ===
CURSOR_IMAGE_PATH = os.path.join("character", "mushroom0.png")  # 鼠标图片路径
CURSOR_HOTSPOT = (0, 0)  # 鼠标热点（指针尖的位置）
_initialized = False
cursor_img = None


def _lazy_init():
    """仅在有显示窗口后初始化"""
    global cursor_img, _initialized

    if _initialized:
        return

    # 检查是否已经有窗口
    if not pygame.display.get_surface():
        return  # 没有窗口就不加载

    pygame.mouse.set_visible(False)

    try:
        cursor_img = pygame.image.load(CURSOR_IMAGE_PATH).convert_alpha()
        print("[ui_cursor] ✅ Custom cursor loaded successfully.")
    except Exception as e:
        print(f"[ui_cursor] ⚠️ Failed to load cursor image: {e}")
        cursor_img = None

    _initialized = True


def _draw_cursor():
    """绘制光标（每帧自动调用）"""
    _lazy_init()  # 只有在窗口存在后才会真正加载图片
    if not cursor_img:
        return
    screen = pygame.display.get_surface()
    if screen:
        mx, my = pygame.mouse.get_pos()
        screen.blit(cursor_img, (mx - CURSOR_HOTSPOT[0], my - CURSOR_HOTSPOT[1]))


def _hook_display_flip():
    """Hook pygame.display.flip()，确保鼠标每帧都绘制"""
    original_flip = pygame.display.flip

    def new_flip():
        _draw_cursor()
        original_flip()

    pygame.display.flip = new_flip


def _auto_setup():
    if not pygame.get_init():
        pygame.init()
    _hook_display_flip()


_auto_setup()
