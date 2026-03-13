"""
board.py
--------
Sliding-puzzle board: grid state, shuffle, win-check, and drag-and-drop
rendering with pygame.

Drag mechanics
--------------
* Mouse-down on a tile that is adjacent to the empty slot starts a drag.
* The tile follows the cursor but is clamped to move *only toward* the
  empty slot and no further than one tile_size away.
* Mouse-up commits the move if the tile has been pulled past the midpoint;
  otherwise the tile snaps back.
"""

import pygame
import random


class Board:
    EMPTY = -1  # sentinel value for the empty slot

    def __init__(
        self,
        tiles: list,         # flat list of n*n-1 pygame.Surface objects
        n: int,              # grid size (3, 4, or 5)
        rect: pygame.Rect,   # on-screen bounding box for the whole board
        tile_size: int,      # pixel size of each square tile
    ):
        self.tiles     = tiles
        self.n         = n
        self.rect      = pygame.Rect(rect)
        self.tile_size = tile_size
        self.moves     = 0
        self.solved    = False

        # Build grid in solved order; last cell starts as the empty slot.
        flat        = list(range(n * n - 1)) + [self.EMPTY]
        self.grid   = [flat[i * n : (i + 1) * n] for i in range(n)]

        self._shuffle()

        # ── Drag state ──────────────────────────────────────────────────────
        self._drag            = False
        self._drag_pos        = None   # (row, col) of the tile being dragged
        self._drag_dir        = None   # 'H' (horizontal) or 'V' (vertical)
        self._drag_origin     = (0, 0) # pixel top-left of tile at drag start
        self._drag_px         = (0, 0) # current pixel top-left during drag
        self._drag_mouse_start = (0, 0)

    # ─── Public interface ─────────────────────────────────────────────────────

    def handle_mousedown(self, pos) -> None:
        """Start a drag if pos lands on a tile adjacent to the empty slot."""
        if self.solved:
            return
        er, ec = self._empty_pos()
        mx, my = pos
        for r in range(self.n):
            for c in range(self.n):
                if self.grid[r][c] == self.EMPTY:
                    continue
                tr = self._cell_rect(r, c)
                if not tr.collidepoint(mx, my):
                    continue
                adj_h = (r == er and abs(c - ec) == 1)
                adj_v = (c == ec and abs(r - er) == 1)
                if adj_h or adj_v:
                    self._drag             = True
                    self._drag_pos         = (r, c)
                    self._drag_dir         = "H" if adj_h else "V"
                    self._drag_origin      = (tr.x, tr.y)
                    self._drag_px          = (tr.x, tr.y)
                    self._drag_mouse_start = pos
                return   # only one tile can be under the cursor

    def handle_mousemove(self, pos) -> None:
        """Update the dragged tile's pixel position, clamped to valid range."""
        if not self._drag:
            return
        r, c   = self._drag_pos
        er, ec = self._empty_pos()
        ox, oy = self._drag_origin
        mx, my = pos
        smx, smy = self._drag_mouse_start

        if self._drag_dir == "H":
            # sign: +1 if empty is to the right, -1 if to the left
            sign = 1 if ec > c else -1
            dx   = (mx - smx) * sign
            dx   = max(0, min(self.tile_size, dx))
            self._drag_px = (ox + dx * sign, oy)
        else:  # "V"
            sign = 1 if er > r else -1
            dy   = (my - smy) * sign
            dy   = max(0, min(self.tile_size, dy))
            self._drag_px = (ox, oy + dy * sign)

    def handle_mouseup(self, _pos) -> bool:
        """
        Commit the move if the tile passed the midpoint, else snap back.
        Returns True if a move was committed.
        """
        if not self._drag:
            return False

        r, c   = self._drag_pos
        er, ec = self._empty_pos()
        ox, oy = self._drag_origin
        moved  = False

        if self._drag_dir == "H":
            if abs(self._drag_px[0] - ox) >= self.tile_size // 2:
                self.grid[er][ec], self.grid[r][c] = self.grid[r][c], self.grid[er][ec]
                self.moves += 1
                moved = True
        else:
            if abs(self._drag_px[1] - oy) >= self.tile_size // 2:
                self.grid[er][ec], self.grid[r][c] = self.grid[r][c], self.grid[er][ec]
                self.moves += 1
                moved = True

        self._drag     = False
        self._drag_pos = None
        if moved:
            self.solved = self._check_win()
        return moved

    def draw(self, surface) -> None:
        """Render the entire board onto *surface*."""
        pygame.draw.rect(surface, (10, 10, 25), self.rect)

        drag_r = self._drag_pos[0] if self._drag else None
        drag_c = self._drag_pos[1] if self._drag else None

        for r in range(self.n):
            for c in range(self.n):
                idx = self.grid[r][c]
                tr  = self._cell_rect(r, c)

                if idx == self.EMPTY:
                    pygame.draw.rect(surface, (20, 20, 45), tr)
                    pygame.draw.rect(surface, (50, 50, 80),  tr, 1)
                    continue

                if self._drag and r == drag_r and c == drag_c:
                    continue   # drawn on top after the loop

                surface.blit(self.tiles[idx], (tr.x, tr.y))
                pygame.draw.rect(surface, (60, 60, 90), tr, 1)

        # Draw the dragged tile last so it floats above everything else
        if self._drag and drag_r is not None:
            idx = self.grid[drag_r][drag_c]
            px, py = self._drag_px
            surface.blit(self.tiles[idx], (px, py))
            drag_rect = pygame.Rect(px, py, self.tile_size, self.tile_size)
            pygame.draw.rect(surface, (255, 215, 0), drag_rect, 3)

        # Light green overlay when solved
        if self.solved:
            overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            overlay.fill((100, 255, 150, 55))
            surface.blit(overlay, self.rect.topleft)

    def force_solve(self) -> None:
        """Instantly arrange all tiles into the solved state."""
        idx = 0
        for r in range(self.n):
            for c in range(self.n):
                if r == self.n - 1 and c == self.n - 1:
                    self.grid[r][c] = self.EMPTY
                else:
                    self.grid[r][c] = idx
                    idx += 1
        self.solved = True

    # ─── Private helpers ──────────────────────────────────────────────────────

    def _cell_rect(self, row: int, col: int) -> pygame.Rect:
        x = self.rect.x + col * self.tile_size
        y = self.rect.y + row * self.tile_size
        return pygame.Rect(x, y, self.tile_size, self.tile_size)

    def _empty_pos(self) -> tuple:
        for r in range(self.n):
            for c in range(self.n):
                if self.grid[r][c] == self.EMPTY:
                    return r, c
        raise RuntimeError("Board has no empty cell — this should never happen.")

    def _shuffle(self) -> None:
        """Perform 1 000 random valid moves so the puzzle is solvable."""
        for _ in range(1000):
            er, ec = self._empty_pos()
            dirs   = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(dirs)
            for dr, dc in dirs:
                nr, nc = er + dr, ec + dc
                if 0 <= nr < self.n and 0 <= nc < self.n:
                    self.grid[er][ec], self.grid[nr][nc] = (
                        self.grid[nr][nc], self.grid[er][ec]
                    )
                    break

    def _check_win(self) -> bool:
        idx = 0
        for r in range(self.n):
            for c in range(self.n):
                if r == self.n - 1 and c == self.n - 1:
                    return self.grid[r][c] == self.EMPTY
                if self.grid[r][c] != idx:
                    return False
                idx += 1
        return True
