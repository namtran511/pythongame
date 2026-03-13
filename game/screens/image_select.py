"""
image_select.py
---------------
Game Setup screen: each player picks an image, plus difficulty / score / timer.

handle_event returns:
  None                              — nothing happened yet
  "back"                            — return to main menu
  ("start", tiles_p1, tiles_p2)    — both players are ready; start the game
"""

import pygame
from game.ui.button import Button
from game.constants import (
    BG_COLOR, ACCENT, TEXT_COLOR, MUTED_TEXT, P1_COLOR, P2_COLOR,
    WIN_COLOR, PANEL_BG, DIFFICULTY_GRID, BOARD_SIZE,
    BTN_COLOR, BTN_HOVER,
)
from game.puzzle.image_processor import (
    pick_image_file, load_and_slice, make_default_tiles, build_full_preview,
)

_PREVIEW = 180


class ImageSelectScreen:

    _DIFF_ACTIVE = {
        "Easy":   (50,  160, 80),
        "Medium": (50,  130, 180),
        "Hard":   (180, 60,  60),
    }

    def __init__(self, screen: pygame.Surface, options: dict):
        self.screen  = screen
        self.options = options
        W, H = screen.get_size()
        cx   = W // 2

        self._font_h1   = pygame.font.SysFont("Arial", 30, bold=True)
        self._font_h2   = pygame.font.SysFont("Arial", 18)
        self._font_btn  = pygame.font.SysFont("Arial", 17, bold=True)
        self._font_val  = pygame.font.SysFont("Arial", 24, bold=True)
        self._font_tiny = pygame.font.SysFont("Arial", 14)

        self._rebuild_tiles_state()

        # ── Player columns (top half) ────────────────────────────────────────
        p1x = W // 4 - _PREVIEW // 2
        p2x = 3 * W // 4 - _PREVIEW // 2
        col_btn_y = 300
        col_btn_h = 38

        self._btn_p1_pick    = Button((p1x, col_btn_y,                  _PREVIEW, col_btn_h), "Pick Image",   self._font_btn)
        self._btn_p1_default = Button((p1x, col_btn_y + col_btn_h + 6,  _PREVIEW, col_btn_h), "Use Defaults", self._font_btn,
                                       color=(50, 110, 55), hover_color=(70, 145, 75))

        self._btn_p2_pick    = Button((p2x, col_btn_y,                  _PREVIEW, col_btn_h), "Pick Image",   self._font_btn)
        self._btn_p2_default = Button((p2x, col_btn_y + col_btn_h + 6,  _PREVIEW, col_btn_h), "Use Defaults", self._font_btn,
                                       color=(50, 110, 55), hover_color=(70, 145, 75))

        self._prev_rect = {
            1: pygame.Rect(p1x, 90, _PREVIEW, _PREVIEW),
            2: pygame.Rect(p2x, 90, _PREVIEW, _PREVIEW),
        }

        # ── Settings (vertical stack, centred) ───────────────────────────────
        sy = 420   # first section Y

        # Difficulty
        bw, bh = 100, 38
        self._diff_btns: dict[str, Button] = {}
        for i, name in enumerate(DIFFICULTY_GRID):
            x = cx - 165 + i * 115
            self._diff_btns[name] = Button(
                (x, sy + 28, bw, bh), name, self._font_btn,
                color=(55, 55, 100), hover_color=(75, 75, 140),
            )
        self._diff_label_y   = sy + 8
        self._diff_note_y    = sy + 76

        # Score limit
        sly = sy + 110
        self._score_label_y  = sly
        self._score_dec = Button((cx - 74, sly + 22, 40, 40), "−", self._font_val)
        self._score_inc = Button((cx + 34, sly + 22, 40, 40), "+", self._font_val)
        self._score_val_y    = sly + 42

        # Timer toggle
        tmy = sly + 90
        self._timer_label_y  = tmy
        self._timer_toggle   = Button((cx - 55, tmy + 22, 110, 36), "", self._font_btn)

        # Timer duration
        tdy = tmy + 72
        self._tdur_label_y   = tdy
        self._timer_dec = Button((cx - 74, tdy + 22, 40, 40), "−", self._font_val)
        self._timer_inc = Button((cx + 34, tdy + 22, 40, 40), "+", self._font_val)
        self._tdur_val_y     = tdy + 42

        # ── Footer buttons ───────────────────────────────────────────────────
        self._btn_back = Button(
            (20, H - 66, 140, 46), "◀  BACK", self._font_btn,
            color=(70, 55, 115), hover_color=(100, 85, 155),
        )
        bw_start = 220
        self._btn_start = Button(
            (cx - bw_start // 2, H - 66, bw_start, 46), "▶  START GAME", self._font_btn,
            color=(45, 140, 50), hover_color=(65, 180, 70),
        )

    # ─── Public interface ─────────────────────────────────────────────────────

    def handle_event(self, event):
        if self._btn_back.handle_event(event):
            return "back"

        if self._btn_p1_pick.handle_event(event):
            self._pick(1)
        if self._btn_p1_default.handle_event(event):
            self._use_default(1)
        if self._btn_p2_pick.handle_event(event):
            self._pick(2)
        if self._btn_p2_default.handle_event(event):
            self._use_default(2)

        for name, btn in self._diff_btns.items():
            if btn.handle_event(event):
                if self.options["difficulty"] != name:
                    self.options["difficulty"] = name
                    self._on_difficulty_change()

        if self._score_dec.handle_event(event):
            self.options["score_limit"] = max(1, self.options["score_limit"] - 1)
        if self._score_inc.handle_event(event):
            self.options["score_limit"] = min(10, self.options["score_limit"] + 1)

        if self._timer_toggle.handle_event(event):
            self.options["timer_enabled"] = not self.options["timer_enabled"]
        if self._timer_dec.handle_event(event):
            self.options["timer_secs"] = max(30, self.options["timer_secs"] - 30)
        if self._timer_inc.handle_event(event):
            self.options["timer_secs"] = min(600, self.options["timer_secs"] + 30)

        if self._ready[1] and self._ready[2]:
            if self._btn_start.handle_event(event):
                return ("start", self._tiles[1], self._tiles[2])
        return None

    def draw(self) -> None:
        W, H  = self.screen.get_size()
        mouse = pygame.mouse.get_pos()
        cx    = W // 2
        self.screen.fill(BG_COLOR)

        # ── Title ────────────────────────────────────────────────────────────
        t = self._font_h1.render("GAME SETUP", True, ACCENT)
        self.screen.blit(t, t.get_rect(center=(cx, 35)))

        # ── Player columns ───────────────────────────────────────────────────
        pygame.draw.line(self.screen, (55, 55, 90), (cx, 55), (cx, 380), 1)

        for p, col, label_color in ((1, W // 4, P1_COLOR), (2, 3 * W // 4, P2_COLOR)):
            lbl = self._font_h1.render(f"PLAYER {p}", True, label_color)
            self.screen.blit(lbl, lbl.get_rect(center=(col, 70)))

            pr = self._prev_rect[p]
            if self._preview[p]:
                self.screen.blit(self._preview[p], pr.topleft)
            else:
                pygame.draw.rect(self.screen, PANEL_BG, pr, border_radius=4)
                hint = self._font_h2.render("no image", True, MUTED_TEXT)
                self.screen.blit(hint, hint.get_rect(center=pr.center))
            pygame.draw.rect(self.screen, (70, 70, 110), pr, 2, border_radius=4)

            if self._ready[p]:
                st = self._font_h2.render("Ready", True, WIN_COLOR)
            else:
                st = self._font_h2.render("Not ready", True, MUTED_TEXT)
            self.screen.blit(st, st.get_rect(center=(col, 284)))

            if self._error[p]:
                err = self._font_tiny.render(self._error[p], True, (230, 80, 80))
                self.screen.blit(err, err.get_rect(center=(col, 372)))

        self._btn_p1_pick.draw(self.screen, mouse)
        self._btn_p1_default.draw(self.screen, mouse)
        self._btn_p2_pick.draw(self.screen, mouse)
        self._btn_p2_default.draw(self.screen, mouse)

        # ── Separator ────────────────────────────────────────────────────────
        pygame.draw.line(self.screen, (55, 55, 90), (40, 400), (W - 40, 400), 1)

        # ── Difficulty ───────────────────────────────────────────────────────
        self._label("DIFFICULTY", cx, self._diff_label_y)
        for name, btn in self._diff_btns.items():
            active = self.options["difficulty"] == name
            btn.color = self._DIFF_ACTIVE.get(name, BTN_COLOR) if active else (55, 55, 100)
            btn.hover_color = tuple(min(c + 25, 255) for c in btn.color)
            btn.draw(self.screen, mouse)
        n = DIFFICULTY_GRID[self.options["difficulty"]]
        note = self._font_tiny.render(f"{n}x{n} grid  ({n*n-1} tiles)", True, MUTED_TEXT)
        self.screen.blit(note, note.get_rect(center=(cx, self._diff_note_y)))

        # ── Score Limit ──────────────────────────────────────────────────────
        self._label("SCORE LIMIT", cx, self._score_label_y)
        self._score_dec.draw(self.screen, mouse)
        val = self._font_val.render(str(self.options["score_limit"]), True, ACCENT)
        self.screen.blit(val, val.get_rect(center=(cx, self._score_val_y)))
        self._score_inc.draw(self.screen, mouse)

        # ── Timer ────────────────────────────────────────────────────────────
        self._label("TIMER", cx, self._timer_label_y)
        enabled = self.options["timer_enabled"]
        self._timer_toggle.text        = "ON" if enabled else "OFF"
        self._timer_toggle.color       = (45, 130, 55) if enabled else (130, 50, 50)
        self._timer_toggle.hover_color = (65, 160, 75) if enabled else (160, 70, 70)
        self._timer_toggle.draw(self.screen, mouse)

        # ── Time per round ───────────────────────────────────────────────────
        self._label("TIME PER ROUND", cx, self._tdur_label_y)
        self._timer_dec.draw(self.screen, mouse)
        m, s   = divmod(self.options["timer_secs"], 60)
        t_text = self._font_val.render(f"{m:02d}:{s:02d}", True, ACCENT)
        self.screen.blit(t_text, t_text.get_rect(center=(cx, self._tdur_val_y)))
        self._timer_inc.draw(self.screen, mouse)

        # ── Footer ───────────────────────────────────────────────────────────
        self._btn_back.draw(self.screen, mouse)
        if self._ready[1] and self._ready[2]:
            self._btn_start.draw(self.screen, mouse)
        else:
            hint = self._font_h2.render(
                "Both players must select an image (or defaults) to start.",
                True, MUTED_TEXT,
            )
            self.screen.blit(hint, hint.get_rect(center=(cx, H - 42)))

    # ─── Private ──────────────────────────────────────────────────────────────

    def _rebuild_tiles_state(self) -> None:
        n = DIFFICULTY_GRID[self.options["difficulty"]]
        self._n   = n
        self._tsz = BOARD_SIZE // n
        self._tiles   = {1: None, 2: None}
        self._preview = {1: None, 2: None}
        self._ready   = {1: False, 2: False}
        self._error   = {1: "",   2: ""}

    def _on_difficulty_change(self) -> None:
        self._rebuild_tiles_state()

    def _pick(self, player: int) -> None:
        self._error[player] = ""
        path = pick_image_file()
        if not path:
            return
        try:
            tiles = load_and_slice(path, self._n, self._tsz)
            self._tiles[player]   = tiles
            self._preview[player] = build_full_preview(tiles, self._n, self._tsz, _PREVIEW)
            self._ready[player]   = True
        except Exception as exc:
            self._error[player] = f"Could not load: {exc}"

    def _use_default(self, player: int) -> None:
        self._error[player] = ""
        tiles = make_default_tiles(self._n, self._tsz)
        self._tiles[player]   = tiles
        self._preview[player] = build_full_preview(tiles, self._n, self._tsz, _PREVIEW)
        self._ready[player]   = True

    def _label(self, text: str, cx: int, y: int) -> None:
        surf = self._font_h2.render(text, True, MUTED_TEXT)
        self.screen.blit(surf, surf.get_rect(center=(cx, y)))
