"""
main.py  —  Puzzle Game entry point
====================================
Pygame-based sliding-puzzle game with:
  • Professional main menu
  • Options (difficulty, score limit, timer)
  • Per-player image upload  (tkinter filedialog)
  • 2-player split-screen
  • Drag-and-drop tile movement

Run:
    python main.py
"""

import os
import sys
import pygame

from game.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
    DEFAULT_DIFFICULTY, DEFAULT_SCORE_LIMIT,
    DEFAULT_TIMER_ENABLED, DEFAULT_TIMER_SECS,
)
from game.screens.main_menu     import MainMenu
from game.screens.options_screen import OptionsScreen
from game.screens.image_select  import ImageSelectScreen
from game.screens.game_screen   import GameScreen

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    pygame.init()
    pygame.mixer.init()
    pygame.display.set_caption("Puzzle Game — 2-Player Split Screen")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock  = pygame.time.Clock()

    # Shared options dict — mutated in-place by screens
    options = {
        "difficulty":    DEFAULT_DIFFICULTY,
        "score_limit":   DEFAULT_SCORE_LIMIT,
        "timer_enabled": DEFAULT_TIMER_ENABLED,
        "timer_secs":    DEFAULT_TIMER_SECS,
        "music_volume":  80,     # 0-100
        "move_volume":   70,     # 0-100
        "brightness":    100,
    }

    # ── Background music ─────────────────────────────────────────────────────
    music_path = os.path.join(BASE_DIR, "res", "SoundEffect", "soundgame.wav")
    if os.path.isfile(music_path):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(options["music_volume"] / 100)
        pygame.mixer.music.play(-1)   # loop forever

    # ── Move sound effect ────────────────────────────────────────────────────
    move_path = os.path.join(BASE_DIR, "res", "SoundEffect", "move.wav")
    move_sfx  = None
    if os.path.isfile(move_path):
        move_sfx = pygame.mixer.Sound(move_path)
        move_sfx.set_volume(options["move_volume"] / 100)

    # ── Screen state machine ──────────────────────────────────────────────────
    state: str    = "menu"
    current       = MainMenu(screen)

    while True:
        events = pygame.event.get()

        # Always handle quit first
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # ── Menu ─────────────────────────────────────────────────────────────
        if state == "menu":
            for event in events:
                result = current.handle_event(event)
                if result == "play":
                    current = ImageSelectScreen(screen, options)
                    state   = "image_select"
                elif result == "options":
                    current = OptionsScreen(screen, options)
                    state   = "options"
                elif result == "exit":
                    pygame.quit()
                    sys.exit()

        # ── Options ───────────────────────────────────────────────────────────
        elif state == "options":
            for event in events:
                result = current.handle_event(event)
                if result == "back":
                    current = MainMenu(screen)
                    state   = "menu"

        # ── Image selection ───────────────────────────────────────────────────
        elif state == "image_select":
            for event in events:
                result = current.handle_event(event)
                if result == "back":
                    current = MainMenu(screen)
                    state   = "menu"
                elif result is not None and isinstance(result, tuple) and result[0] == "start":
                    _, tiles_p1, tiles_p2 = result
                    current = GameScreen(screen, options, tiles_p1, tiles_p2,
                                         move_sfx=move_sfx)
                    state   = "game"

        # ── In-game ───────────────────────────────────────────────────────────
        elif state == "game":
            current.update()
            for event in events:
                result = current.handle_event(event)
                if result == "menu":
                    current = MainMenu(screen)
                    state   = "menu"
                elif result == "setup":
                    current = ImageSelectScreen(screen, options)
                    state   = "image_select"

        # ── Sync music volume ─────────────────────────────────────────────────
        vol = options.get("music_volume", 80) / 100
        pygame.mixer.music.set_volume(vol)

        # ── Sync move sound volume ────────────────────────────────────────────
        if move_sfx:
            move_sfx.set_volume(options.get("move_volume", 70) / 100)

        # ── Draw & flip ───────────────────────────────────────────────────────
        current.draw()

        # Global brightness dim (skip for the options screen which handles its own)
        if state != "options":
            brightness = options.get("brightness", 100)
            if brightness < 100:
                W, H  = screen.get_size()
                dim   = pygame.Surface((W, H), pygame.SRCALPHA)
                alpha = int(255 * (1 - brightness / 100))
                dim.fill((0, 0, 0, alpha))
                screen.blit(dim, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
