"""
main_menu.py
------------
Pygame-based main menu screen.
Returns a navigation string from handle_event: 'play' | 'options' | 'exit'
"""

import math
import pygame
from game.ui.button import Button
from game.constants import (
    BG_COLOR, ACCENT, MUTED_TEXT, BTN_COLOR, BTN_HOVER, BTN_ACTIVE,
    WINDOW_WIDTH, WINDOW_HEIGHT,
)

TITLE = "PUZZLE"


class MainMenu:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        W, H = screen.get_size()

        # Arial Black has much better letter spacing than Impact
        self._font_title = pygame.font.SysFont("Arial Black", 96, bold=True)
        self._font_sub   = pygame.font.SysFont("Arial",   20)
        self._font_btn   = pygame.font.SysFont("Arial",   22, bold=True)

        self._tick = 0  # animation counter

        bw, bh = 270, 56
        cx     = W // 2

        # Cyan PLAY button
        self.btn_play    = Button(
            (cx - bw // 2, 420, bw, bh), "▶  PLAY GAME", self._font_btn,
            color=(0, 180, 220), hover_color=(0, 240, 255), active_color=(0, 130, 170),
        )
        # Purple OPTIONS button
        self.btn_options = Button(
            (cx - bw // 2, 492, bw, bh), "⚙  OPTIONS", self._font_btn,
            color=(130, 0, 200), hover_color=(180, 0, 255), active_color=(90, 0, 140),
        )
        # Hot red/pink EXIT button
        self.btn_exit    = Button(
            (cx - bw // 2, 564, bw, bh), "✕  EXIT", self._font_btn,
            color=(200, 0, 70), hover_color=(255, 0, 100), active_color=(140, 0, 50),
        )

        self._bg = self._build_bg(W, H)

    # ─── Public interface ─────────────────────────────────────────────────────

    def handle_event(self, event) -> str | None:
        """Return 'play', 'options', 'exit', or None."""
        if self.btn_play.handle_event(event):
            return "play"
        if self.btn_options.handle_event(event):
            return "options"
        if self.btn_exit.handle_event(event):
            return "exit"
        return None

    def draw(self) -> None:
        self._tick += 1
        W, H  = self.screen.get_size()
        mouse = pygame.mouse.get_pos()

        self.screen.blit(self._bg, (0, 0))

        # ── Animated title ────────────────────────────────────────────────────
        self._draw_title(W)

        # Subtitle
        sub = self._font_sub.render(
            "2-Player Split-Screen  •  Custom Images  •  Drag & Drop", True, MUTED_TEXT)
        self.screen.blit(sub, sub.get_rect(center=(W // 2, 360)))

        # Neon cyan divider line
        pygame.draw.line(self.screen, (0, 255, 240),
                         (W // 2 - 260, 390), (W // 2 + 260, 390), 2)
        pygame.draw.line(self.screen, (0, 100, 100),
                         (W // 2 - 260, 388), (W // 2 + 260, 388), 1)
        pygame.draw.line(self.screen, (0, 100, 100),
                         (W // 2 - 260, 392), (W // 2 + 260, 392), 1)

        self.btn_play.draw(self.screen, mouse)
        self.btn_options.draw(self.screen, mouse)
        self.btn_exit.draw(self.screen, mouse)

    # ─── Title rendering ──────────────────────────────────────────────────────

    def _draw_title(self, W: int) -> None:
        t     = self._tick
        pulse = 0.75 + 0.25 * math.sin(t * 0.05)
        cy    = 220

        # Measure the text first
        title_surf = self._font_title.render(TITLE, True, (255, 255, 255))
        tw, th     = title_surf.get_size()
        tx         = W // 2 - tw // 2
        ty         = cy - th // 2

        # ── Dark panel behind text for contrast ───────────────────────────────
        pad_x, pad_y = 36, 18
        panel = pygame.Surface((tw + pad_x * 2, th + pad_y * 2), pygame.SRCALPHA)
        panel.fill((5, 0, 20, 200))
        self.screen.blit(panel, (tx - pad_x, ty - pad_y))

        # ── Neon pink border around panel ─────────────────────────────────────
        border_col = (int(255 * pulse), 0, int(180 * pulse))
        pygame.draw.rect(self.screen, border_col,
                         (tx - pad_x, ty - pad_y, tw + pad_x * 2, th + pad_y * 2),
                         2, border_radius=10)

        # ── Simple drop shadow (2px down/right) ───────────────────────────────
        shadow = self._font_title.render(TITLE, True, (180, 0, 120))
        self.screen.blit(shadow, (tx + 2, ty + 2))

        # ── Main white text ───────────────────────────────────────────────────
        self.screen.blit(title_surf, (tx, ty))

    # ─── Background ───────────────────────────────────────────────────────────

    @staticmethod
    def _build_bg(W: int, H: int) -> pygame.Surface:
        surf = pygame.Surface((W, H))
        surf.fill(BG_COLOR)
        # Purple dot-grid
        for y in range(0, H, 50):
            for x in range(0, W, 50):
                pygame.draw.circle(surf, (50, 0, 80), (x, y), 1)
        # Horizontal scanlines
        scan = pygame.Surface((W, 1), pygame.SRCALPHA)
        scan.fill((0, 0, 0, 40))
        for y in range(0, H, 4):
            surf.blit(scan, (0, y))
        # Vertical neon edge glow
        for i in range(8):
            a = max(0, 80 - i * 10)
            eg = pygame.Surface((1, H), pygame.SRCALPHA)
            eg.fill((160, 0, 220, a))
            surf.blit(eg, (i, 0))
            surf.blit(eg, (W - 1 - i, 0))
        return surf

