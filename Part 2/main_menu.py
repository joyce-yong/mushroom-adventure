import pygame
import sys
import time
import subprocess

pygame.init()
pygame.mixer.init()

# --- Screen Setup ---
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mushroom Adventure")

# --- Colors ---
WHITE = (255, 255, 255)
LIGHT_BLUE = (150, 200, 255)
DARK_BLUE = (20, 40, 80)
BLACK = (0, 0, 0)

# --- Load Background & Music ---
try:
    background = pygame.image.load(
        "C:\\Users\\PC\\Desktop\\school apu\\Sem 2\\Imaging and Special Effects (082025-MTG)\\Mushroom Adventure\\space_background_pack\\space_background_pack\\Assets\\Blue Version\\blue-preview.png"
    ).convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except:
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(DARK_BLUE)

try:
    pygame.mixer.music.load("C:\\Users\\PC\\Music\\music bgm\\lofi-chill-374877.mp3")
    pygame.mixer.music.play(-1)
except:
    print("⚠️ No background music found.")

# --- Fonts ---
title_font = pygame.font.Font(None, 100)
button_font = pygame.font.Font(None, 60)
small_font = pygame.font.Font(None, 36)
story_font = pygame.font.Font(None, 30)


# --- Button Class ---
class Button:
    def __init__(self, text, y_pos, action=None):
        self.text = text
        self.action = action
        self.y_pos = y_pos
        self.base_color = WHITE
        self.hover_color = LIGHT_BLUE
        self.scale = 1.0
        self.rect = None

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect and self.rect.collidepoint(mouse_pos)
        color = self.hover_color if is_hovered else self.base_color
        self.scale = 1.1 if is_hovered else 1.0

        text_surface = button_font.render(self.text, True, color)
        text_surface = pygame.transform.rotozoom(text_surface, 0, self.scale)
        self.rect = text_surface.get_rect(center=(WIDTH // 2, self.y_pos))
        surface.blit(text_surface, self.rect)

    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect and self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                pygame.time.delay(200)
                if self.action:
                    self.action()


# --- Story Screen (with Typewriter Effect) ---
def show_story():
    story_lines = [
        "In the universe, there is a mushroom race called Spore Fitters.",
        "They have powerful evolutionary abilities, but cannot reproduce on their own.",
        "They can only parasitize other organisms to survive.",
        "So, after discovering other life forms in the universe,",
        "a brave mushroom began his journey.",
        "Your mission: reach the safe zone before the ice melts and the dead return.",
        "",
        "Press any key to begin your journey..."
    ]

    pygame.mixer.music.fadeout(1000)
    story_bg = pygame.Surface((WIDTH, HEIGHT))
    story_bg.fill((10, 20, 40))
    screen.blit(story_bg, (0, 0))
    pygame.display.flip()

    def typewriter_text(text, x, y, color=LIGHT_BLUE, delay=0.03):
        """Draw text letter by letter with typewriter effect."""
        current_text = ""
        for char in text:
            current_text += char
            text_surface = story_font.render(current_text, True, color)
            text_rect = text_surface.get_rect(center=(x, y))
            screen.blit(story_bg, (0, 0))  # redraw bg
            # draw previous lines
            for i, prev in enumerate(story_lines[:story_lines.index(text)]):
                prev_surface = story_font.render(prev, True, color)
                prev_rect = prev_surface.get_rect(center=(WIDTH // 2, 180 + i * 40))
                screen.blit(prev_surface, prev_rect)
            screen.blit(text_surface, text_rect)
            pygame.display.flip()
            pygame.time.delay(int(delay * 1000))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    # --- Typewriter sequence ---
    for i, line in enumerate(story_lines):
        typewriter_text(line, WIDTH // 2, 180 + i * 40)
        time.sleep(0.2)

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                waiting = False
        pygame.display.flip()

    # --- Jump to Level1.py ---
    # When player presses a key, start the Level1
    pygame.quit()
    subprocess.run(["python", "level1.py"])
    sys.exit()


# --- Instructions Screen ---
def instructions():
    showing = True
    while showing:
        screen.fill(DARK_BLUE)
        lines = [
            "🎯 How to Play:",
            "- Move with WASD",
            "- Aim and shoot with mouse",
            "- Press 1, 2, 3 to change bullet type",
            "- Collect blue mushroom for Ice Bullet",
            "",
            "Press ESC to return to menu"
        ]
        for i, line in enumerate(lines):
            text = small_font.render(line, True, WHITE)
            screen.blit(text, (100, 150 + i * 50))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                showing = False


# --- Exit Game ---
def exit_game():
    pygame.quit()
    sys.exit()


# --- Buttons ---
buttons = [
    Button("Start Game", 300, show_story),
    Button("Instructions", 400, instructions),
    Button("Exit Game", 500, exit_game)
]


# --- Main Menu ---
def main_menu():
    running = True
    clock = pygame.time.Clock()

    while running:
        screen.blit(background, (0, 0))
        title_surface = title_font.render("Mushroom Adventure", True, WHITE)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, 150))
        screen.blit(title_surface, title_rect)

        for button in buttons:
            button.draw(screen)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    button.check_click()


# --- Run ---
if __name__ == "__main__":
    main_menu()
