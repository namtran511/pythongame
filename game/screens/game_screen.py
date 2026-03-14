"""
game_screen.py
--------------
Puzzle game supporting both 1-player and 2-player (split-screen) modes.

Layout (2-player)
-----------------
  Player 1 board — left half
  Player 2 board — right half
  Centre strip   — score, round indicator, timer

Layout (1-player)
-----------------
  Player 1 board — centred
  Score / moves / timer shown above and below the board

Round flow (2-player)
---------------------
  Both players solve simultaneously.  First to solve earns a point.
  If the timer expires the player with the most tiles in correct
  positions gets the point (tie -> Player 1).
  First to `score_limit` wins the match.

Round flow (1-player)
---------------------
  Player solves their own puzzle.  Solving earns a point.
  Timer expiry is a loss for the round (opponent "phantom" wins).
  First to `score_limit` wins or loses the match.

handle_event / update / draw follow the same pattern as other screens.
Returns 'menu' from handle_event when the user clicks "Main Menu".
"""

import time
import pygame

from game.puzzle.board import Board
from game.puzzle.image_processor import build_full_preview, make_default_tiles
from game.ui.button import Button
from game.constants import (
    BG_COLOR, ACCENT, TEXT_COLOR, MUTED_TEXT,
    P1_COLOR, P2_COLOR, WIN_COLOR,
    DIFFICULTY_GRID, BOARD_SIZE,
    LEFT_BOARD_X, RIGHT_BOARD_X, BOARD_Y,
    WINDOW_WIDTH, WINDOW_HEIGHT,
)


class GameScreen:

    def __init__(
        self,
        screen: pygame.Surface,
        options: dict,
        tiles_p1: list,
        tiles_p2: list,   # may be None in single-player mode
        move_sfx=None,
    ):
        self.screen      = screen
        self.options     = options
        self._raw_p1     = tiles_p1
        self._raw_p2     = tiles_p2
        self._move_sfx   = move_sfx
        self._multiplayer = options.get("multiplayer", True)
        W, H             = screen.get_size()

        self._font_huge  = pygame.font.SysFont("Arial", 54, bold=True)
        self._font_big   = pygame.font.SysFont("Arial", 38, bold=True)
        self._font_hud   = pygame.font.SysFont("Arial", 22, bold=True)
        self._font_small = pygame.font.SysFont("Arial", 16)
        self._font_btn   = pygame.font.SysFont("Arial", 19, bold=True)

        n          = DIFFICULTY_GRID[options["difficulty"]]
        self._n    = n
        self._tsz  = BOARD_SIZE // n
        board_px   = n * self._tsz

        # Board rects
        if self._multiplayer:
            self._rect_p1 = pygame.Rect(LEFT_BOARD_X,  BOARD_Y, board_px, board_px)
            self._rect_p2 = pygame.Rect(RIGHT_BOARD_X, BOARD_Y, board_px, board_px)
        else:
            # Centre the single board
            cx_board = (W - board_px) // 2
            self._rect_p1 = pygame.Rect(cx_board, BOARD_Y, board_px, board_px)
            self._rect_p2 = None    # not used in single-player

        # Match state
        self._score       = {1: 0, 2: 0}   # player 2 = "phantom" in single mode
        self._score_limit = options["score_limit"]
        self._round       = 1

        # Timer
        self._timer_on   = options["timer_enabled"]
        self._timer_full = options["timer_secs"]
        self._time_left  = float(self._timer_full)
        self._last_tick  = time.monotonic()

        # Phase flags
        self._round_over = False
        self._game_over  = False
        self._rnd_winner = None   # 1 or 2
        self._winner     = None   # 1 or 2

        # ── Toolbar ──────────────────────────────────────────────────────────
        btn_w, btn_h = 120, 40
        self._btn_back = Button(
            (16, H - btn_h - 14, btn_w, btn_h), "◀  Back", self._font_btn,
            color=(0, 160, 200), hover_color=(0, 220, 255), active_color=(0, 110, 150),
        )
        self._btn_restart = Button(
            (16 + btn_w + 10, H - btn_h - 14, btn_w, btn_h), "Restart", self._font_btn,
            color=(200, 0, 130), hover_color=(255, 0, 160), active_color=(140, 0, 90),
        )

        cx = W // 2
        self._btn_next = Button(
            (cx - 115, H - 78, 230, 52), "▶  NEXT ROUND", self._font_btn,
            color=(0, 180, 60), hover_color=(57, 255, 20), active_color=(0, 120, 40),
        )
        self._btn_menu_final = Button(
            (cx - 115, H - 78, 230, 52), "◀  MAIN MENU", self._font_btn,
            color=(130, 0, 200), hover_color=(180, 0, 255), active_color=(90, 0, 140),
        )

        # ── Reference thumbnails ──────────────────────────────────────────────
        _REF = 130
        self._ref_p1   = build_full_preview(tiles_p1, n, self._tsz, _REF)
        self._ref_p2   = build_full_preview(tiles_p2, n, self._tsz, _REF) if tiles_p2 else None
        self._ref_size = _REF

        self._start_round()

    # ─── Public interface ─────────────────────────────────────────────────────

    def handle_event(self, event) -> str | None:
        if self._game_over:
            if self._btn_menu_final.handle_event(event):
                return "menu"
            return None

        if self._round_over:
            if self._btn_next.handle_event(event):
                self._start_round()
            return None

        if self._btn_back.handle_event(event):
            return "setup"
        if self._btn_restart.handle_event(event):
            self._start_round()
            return None

        # Route mouse events to board(s)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._rect_p1.collidepoint(event.pos):
                self._board1.handle_mousedown(event.pos)
            if self._multiplayer and self._rect_p2 and self._rect_p2.collidepoint(event.pos):
                self._board2.handle_mousedown(event.pos)

        elif event.type == pygame.MOUSEMOTION:
            if self._board1._drag:
                self._board1.handle_mousemove(event.pos)
            if self._multiplayer and self._board2._drag:
                self._board2.handle_mousemove(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            moved1 = self._board1.handle_mouseup(event.pos)
            moved2 = self._board2.handle_mouseup(event.pos) if self._multiplayer else False
            if (moved1 or moved2) and self._move_sfx:
                self._move_sfx.play()
            self._check_win_conditions()

        return None

    def update(self) -> None:
        if self._game_over or self._round_over:
            return

        if self._timer_on:
            now              = time.monotonic()
            self._time_left -= now - self._last_tick
            self._last_tick  = now
            if self._time_left <= 0:
                self._time_left = 0.0
                self._on_time_up()

    def draw(self) -> None:
        W, H  = self.screen.get_size()
        mouse = pygame.mouse.get_pos()
        self.screen.fill(BG_COLOR)

        cx = W // 2

        if self._multiplayer:
            self._draw_multiplayer(W, H, cx, mouse)
        else:
            self._draw_single(W, H, cx, mouse)

        # ── Overlays ──────────────────────────────────────────────────────────
        if self._round_over and not self._game_over:
            self._draw_overlay(f"Round {self._round - 1} over!", self._rnd_winner)
            self._btn_next.draw(self.screen, mouse)

        if self._game_over:
            self._draw_overlay("MATCH OVER", self._winner, final=True)
            self._btn_menu_final.draw(self.screen, mouse)

    # ─── Draw helpers ─────────────────────────────────────────────────────────

    def _draw_multiplayer(self, W, H, cx, mouse):
        # Board glows
        for board_rect, glow in ((self._rect_p1, P1_COLOR), (self._rect_p2, P2_COLOR)):
            pygame.draw.rect(self.screen, glow, board_rect.inflate(6, 6), 2, border_radius=4)
            dim_glow = tuple(c // 3 for c in glow)
            pygame.draw.rect(self.screen, dim_glow, board_rect.inflate(10, 10), 1, border_radius=6)

        self._board1.draw(self.screen)
        self._board2.draw(self.screen)

        # Player labels above boards
        for board_rect, color, label in (
            (self._rect_p1, P1_COLOR, "◈  PLAYER 1"),
            (self._rect_p2, P2_COLOR, "PLAYER 2  ◈"),
        ):
            lbl = self._font_hud.render(label, True, color)
            self.screen.blit(lbl, lbl.get_rect(centerx=board_rect.centerx, bottom=board_rect.top - 6))

        # Score (centre top)
        score_surf = self._font_huge.render(
            f"{self._score[1]}  :  {self._score[2]}", True, TEXT_COLOR)
        self.screen.blit(score_surf, score_surf.get_rect(center=(cx, 36)))
        p1s = self._font_small.render("P1", True, P1_COLOR)
        p2s = self._font_small.render("P2", True, P2_COLOR)
        sr  = score_surf.get_rect(center=(cx, 36))
        self.screen.blit(p1s, p1s.get_rect(right=sr.left - 6, centery=36))
        self.screen.blit(p2s, p2s.get_rect(left=sr.right + 6,  centery=36))
        pygame.draw.line(self.screen, (0, 255, 240), (cx - 80, 60), (cx + 80, 60), 1)
        rnd_txt = self._font_small.render(
            f"Round {self._round}   —   first to {self._score_limit}", True, MUTED_TEXT)
        self.screen.blit(rnd_txt, rnd_txt.get_rect(center=(cx, 70)))

        # Toolbar
        if not self._round_over and not self._game_over:
            self._btn_back.draw(self.screen, mouse)
            self._btn_restart.draw(self.screen, mouse)

        # Move counters
        for board, rect, color in (
            (self._board1, self._rect_p1, P1_COLOR),
            (self._board2, self._rect_p2, P2_COLOR),
        ):
            m = self._font_hud.render(f"Moves: {board.moves}", True, color)
            self.screen.blit(m, m.get_rect(centerx=rect.centerx, top=rect.bottom + 6))

        # Reference thumbnails
        ref_y_top = self._rect_p1.bottom + 30
        for ref_img, board_rect, color, label_txt in (
            (self._ref_p1, self._rect_p1, P1_COLOR, "GOAL ▼"),
            (self._ref_p2, self._rect_p2, P2_COLOR, "GOAL ▼"),
        ):
            rs  = self._ref_size
            rx  = board_rect.centerx - rs // 2
            ry  = ref_y_top + 18
            lbl = self._font_small.render(label_txt, True, color)
            self.screen.blit(lbl, lbl.get_rect(centerx=board_rect.centerx, bottom=ry - 2))
            self.screen.blit(ref_img, (rx, ry))
            border_rect = pygame.Rect(rx - 2, ry - 2, rs + 4, rs + 4)
            pygame.draw.rect(self.screen, color, border_rect, 2, border_radius=4)
            pygame.draw.rect(self.screen, tuple(c // 3 for c in color),
                             border_rect.inflate(4, 4), 1, border_radius=6)

        # Timer
        if self._timer_on:
            secs    = max(0, int(self._time_left))
            mm, ss  = divmod(secs, 60)
            t_color = (255, 0, 80) if self._time_left < 30 else (0, 255, 240)
            t_surf  = self._font_hud.render(f"⏱  {mm:02d}:{ss:02d}", True, t_color)
            _, H    = self.screen.get_size()
            self.screen.blit(t_surf, t_surf.get_rect(center=(cx, H - 30)))

    def _draw_single(self, W, H, cx, mouse):
        # Board glow
        pygame.draw.rect(self.screen, P1_COLOR, self._rect_p1.inflate(6, 6), 2, border_radius=4)
        dim_glow = tuple(c // 3 for c in P1_COLOR)
        pygame.draw.rect(self.screen, dim_glow, self._rect_p1.inflate(10, 10), 1, border_radius=6)

        self._board1.draw(self.screen)

        # Player label above board
        lbl = self._font_hud.render("◈  PLAYER 1", True, P1_COLOR)
        self.screen.blit(lbl, lbl.get_rect(centerx=self._rect_p1.centerx, bottom=self._rect_p1.top - 6))

        # Score (top-centre)  shows "Wins: X / Y"
        score_surf = self._font_hud.render(
            f"Wins: {self._score[1]}  /  {self._score_limit}", True, ACCENT)
        self.screen.blit(score_surf, score_surf.get_rect(center=(cx, 36)))
        rnd_txt = self._font_small.render(f"Round {self._round}", True, MUTED_TEXT)
        self.screen.blit(rnd_txt, rnd_txt.get_rect(center=(cx, 62)))

        # Move counter below board
        m = self._font_hud.render(f"Moves: {self._board1.moves}", True, P1_COLOR)
        self.screen.blit(m, m.get_rect(centerx=self._rect_p1.centerx, top=self._rect_p1.bottom + 6))

        # Reference thumbnail below move counter
        rs  = self._ref_size
        rx  = self._rect_p1.centerx - rs // 2
        ry  = self._rect_p1.bottom + 30
        lbl_g = self._font_small.render("GOAL ▼", True, P1_COLOR)
        self.screen.blit(lbl_g, lbl_g.get_rect(centerx=self._rect_p1.centerx, bottom=ry - 2))
        self.screen.blit(self._ref_p1, (rx, ry))
        border_rect = pygame.Rect(rx - 2, ry - 2, rs + 4, rs + 4)
        pygame.draw.rect(self.screen, P1_COLOR, border_rect, 2, border_radius=4)

        # Timer
        if self._timer_on:
            secs    = max(0, int(self._time_left))
            mm, ss  = divmod(secs, 60)
            t_color = (255, 0, 80) if self._time_left < 30 else (0, 255, 240)
            t_surf  = self._font_hud.render(f"⏱  {mm:02d}:{ss:02d}", True, t_color)
            self.screen.blit(t_surf, t_surf.get_rect(center=(cx, H - 30)))

        # Toolbar
        if not self._round_over and not self._game_over:
            self._btn_back.draw(self.screen, mouse)
            self._btn_restart.draw(self.screen, mouse)

    # ─── Private helpers ──────────────────────────────────────────────────────

    def _start_round(self) -> None:
        self._board1 = Board(
            [t.copy() for t in self._raw_p1],
            self._n, self._rect_p1, self._tsz,
        )
        if self._multiplayer and self._raw_p2:
            self._board2 = Board(
                [t.copy() for t in self._raw_p2],
                self._n, self._rect_p2, self._tsz,
            )
        else:
            # Dummy board2 for code paths that reference it
            self._board2 = None

        self._time_left  = float(self._timer_full)
        self._last_tick  = time.monotonic()
        self._round_over = False
        self._rnd_winner = None

    def _check_win_conditions(self) -> None:
        if self._round_over:
            return

        p1 = self._board1.solved

        if self._multiplayer and self._board2:
            p2 = self._board2.solved
            if p1 and p2:
                w = 1 if self._board1.moves <= self._board2.moves else 2
                self._end_round(w)
            elif p1:
                self._end_round(1)
            elif p2:
                self._end_round(2)
        else:
            # Single-player: win on solve
            if p1:
                self._end_round(1)

    def _end_round(self, winner: int) -> None:
        self._score[winner] += 1
        self._rnd_winner     = winner
        self._round         += 1
        self._round_over     = True
        if self._score[winner] >= self._score_limit:
            self._game_over = True
            self._winner    = winner

    def _on_time_up(self) -> None:
        if self._round_over:
            return
        if self._multiplayer and self._board2:
            c1 = self._count_correct(self._board1)
            c2 = self._count_correct(self._board2)
            self._end_round(1 if c1 >= c2 else 2)
        else:
            # Single-player: time up = phantom player (2) wins the round
            self._end_round(2)

    @staticmethod
    def _count_correct(board: Board) -> int:
        count = 0
        for r in range(board.n):
            for c in range(board.n):
                expected = r * board.n + c
                if r == board.n - 1 and c == board.n - 1:
                    if board.grid[r][c] == board.EMPTY:
                        count += 1
                elif board.grid[r][c] == expected:
                    count += 1
        return count

    def _draw_overlay(self, heading: str, winner: int | None,
                      final: bool = False) -> None:
        W, H = self.screen.get_size()
        dim  = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((10, 0, 30, 190))
        self.screen.blit(dim, (0, 0))

        cx, cy = W // 2, H // 2 - 80

        shadow = self._font_big.render(heading, True, (100, 0, 80))
        self.screen.blit(shadow, shadow.get_rect(center=(cx + 3, cy + 3)))
        hdg = self._font_big.render(heading, True, ACCENT)
        self.screen.blit(hdg, hdg.get_rect(center=(cx, cy)))

        if winner:
            if self._multiplayer:
                color    = P1_COLOR if winner == 1 else P2_COLOR
                win_text = f"Player {winner} wins!"
            else:
                # Single player
                if winner == 1:
                    color    = WIN_COLOR
                    win_text = "You solved it! ✔"
                else:
                    color    = (255, 60, 60)
                    win_text = "Time's up! ✘"
            ws_shad = self._font_huge.render(win_text, True, tuple(c // 4 for c in color))
            self.screen.blit(ws_shad, ws_shad.get_rect(center=(cx + 4, cy + 76)))
            ws = self._font_huge.render(win_text, True, color)
            self.screen.blit(ws, ws.get_rect(center=(cx, cy + 72)))

        if final:
            if self._multiplayer:
                sc_text = f"Final score  {self._score[1]} – {self._score[2]}"
            else:
                wins = self._score[1]
                if self._winner == 1:
                    sc_text = f"You won {wins} round{'s' if wins > 1 else ''}!  🎉"
                else:
                    sc_text = f"Better luck next time!  Wins: {wins}"
            sc = self._font_hud.render(sc_text, True, (0, 255, 240))
            self.screen.blit(sc, sc.get_rect(center=(cx, cy + 148)))
