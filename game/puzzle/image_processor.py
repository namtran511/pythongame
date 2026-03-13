"""
image_processor.py
------------------
Utilities for loading a player-selected image, cropping it to a square,
slicing it into N×N tiles, and generating default numbered tiles as a fallback.
"""

import pygame


# ─── Public API ───────────────────────────────────────────────────────────────

def pick_image_file() -> str | None:
    """
    Open a tkinter file-dialog and return the selected path, or None if the
    user cancelled.  pygame display must already be initialised before calling
    this so the dialog does not steal focus permanently.
    """
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename(
        title="Select puzzle image",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
            ("All files",   "*.*"),
        ],
    )
    root.destroy()
    return path if path else None


def load_and_slice(image_path: str, n: int, tile_size: int) -> list:
    """
    Load the image at *image_path*, centre-crop it to a square, scale it to
    ``n * tile_size`` × ``n * tile_size`` pixels, and return a flat list of
    ``n*n - 1`` pygame.Surface tiles in row-major order (the last position,
    which will be the empty slot, is excluded).

    Raises pygame.error / FileNotFoundError on bad paths or unsupported formats.
    """
    img = pygame.image.load(image_path).convert()
    img = _crop_to_square(img)
    total = n * tile_size
    img = pygame.transform.scale(img, (total, total))

    tiles = []
    for row in range(n):
        for col in range(n):
            if row == n - 1 and col == n - 1:
                continue   # skip the last slot (will be empty)
            rect = pygame.Rect(col * tile_size, row * tile_size, tile_size, tile_size)
            tiles.append(img.subsurface(rect).copy())
    return tiles


def make_default_tiles(n: int, tile_size: int) -> list:
    """
    Generate ``n*n - 1`` colourful numbered tiles when no image is selected.
    Each tile has a distinct hue and a bold number in the centre.
    """
    total = n * n - 1
    font  = pygame.font.SysFont("Arial", tile_size // 3, bold=True)
    tiles = []
    for i in range(total):
        surf  = pygame.Surface((tile_size, tile_size))
        hue   = int(360 * i / total)
        color = _hsv_to_rgb(hue, 0.60, 0.82)
        surf.fill(color)

        # Subtle darker border inside the tile
        pygame.draw.rect(surf, tuple(max(0, c - 40) for c in color),
                         (0, 0, tile_size, tile_size), 3)

        label = font.render(str(i + 1), True, (255, 255, 255))
        surf.blit(label, label.get_rect(center=(tile_size // 2, tile_size // 2)))
        tiles.append(surf)
    return tiles


def build_full_preview(tiles: list, n: int, tile_size: int,
                       preview_size: int = 200) -> pygame.Surface:
    """
    Compose a full n×n grid (n*n-1 tiles + blank corner) and scale it down to
    *preview_size* × *preview_size* for the image-selection screen.
    """
    full = pygame.Surface((n * tile_size, n * tile_size))
    full.fill((20, 20, 40))
    for i, tile in enumerate(tiles):
        r, c = divmod(i, n)
        full.blit(tile, (c * tile_size, r * tile_size))
    return pygame.transform.smoothscale(full, (preview_size, preview_size))


# ─── Private helpers ──────────────────────────────────────────────────────────

def _crop_to_square(surface: pygame.Surface) -> pygame.Surface:
    """Centre-crop *surface* to a square using the shorter dimension."""
    w, h = surface.get_size()
    side = min(w, h)
    x    = (w - side) // 2
    y    = (h - side) // 2
    return surface.subsurface(pygame.Rect(x, y, side, side)).copy()


def _hsv_to_rgb(h: int, s: float, v: float) -> tuple:
    """Convert HSV (h: 0-360, s/v: 0-1) to an (R, G, B) tuple (0-255)."""
    h_norm = h / 360.0
    i  = int(h_norm * 6)
    f  = h_norm * 6 - i
    p  = v * (1 - s)
    q  = v * (1 - f * s)
    t  = v * (1 - (1 - f) * s)
    table = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]
    r, g, b = table[i % 6]
    return (int(r * 255), int(g * 255), int(b * 255))
