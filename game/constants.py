# ─── Window ──────────────────────────────────────────────────────────────────
WINDOW_WIDTH  = 1300
WINDOW_HEIGHT = 900
FPS           = 60

# ─── Colors — Gen-Z Cyberpunk ─────────────────────────────────────────────────
BG_COLOR    = (5,   2,   18)    # void black / deep space
PANEL_BG    = (14,  7,   35)    # dark purple-void
BTN_COLOR   = (160, 0,   220)   # electric purple
BTN_HOVER   = (210, 0,   255)   # neon magenta-violet
BTN_ACTIVE  = (110, 0,   160)   # deep violet pressed
BTN_TEXT    = (255, 255, 255)
ACCENT      = (255, 0,   200)   # hot magenta / neon pink
TEXT_COLOR  = (220, 240, 255)   # ice white
MUTED_TEXT  = (130, 80,  200)   # muted violet
P1_COLOR    = (0,   255, 240)   # electric cyan
P2_COLOR    = (255, 50,  180)   # neon pink/magenta
WIN_COLOR   = (57,  255, 20)    # neon green (classic cyberpunk)
EMPTY_CELL  = (4,   1,   12)    # near-black void
DRAG_BORDER = (0,   255, 240)   # cyan glow drag
TILE_BORDER = (100, 0,   180)   # purple tile edge

# ─── Puzzle board ─────────────────────────────────────────────────────────────
# Both boards use the same pixel width; tile_size is derived at runtime as
# BOARD_SIZE // n  (so the board pixel width = tile_size * n ≤ BOARD_SIZE).
BOARD_SIZE = 500

DIFFICULTY_GRID = {
    "Easy":   3,
    "Medium": 4,
    "Hard":   5,
}

# ─── Layout (pixel positions for the two boards) ──────────────────────────────
LEFT_BOARD_X  = 40
RIGHT_BOARD_X = 760
BOARD_Y       = 110
CENTER_X      = WINDOW_WIDTH // 2   # 650

# ─── Default game options ─────────────────────────────────────────────────────
DEFAULT_DIFFICULTY    = "Medium"
DEFAULT_SCORE_LIMIT   = 3      # first player to solve N puzzles wins the match
DEFAULT_TIMER_ENABLED = True
DEFAULT_TIMER_SECS    = 180    # seconds per puzzle round
DEFAULT_MULTIPLAYER   = True   # True = 2-player, False = 1-player
