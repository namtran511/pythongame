import random


class PuzzleEnv:
    """N-puzzle environment for both GUI interaction and RL training."""

    def __init__(self, size: int):
        self.size = size
        self.board = [[0] * size for _ in range(size)]

    def load_current_board(self, matrix):
        """Load board state from the GUI button matrix."""
        for i in range(self.size):
            for j in range(self.size):
                text = matrix[i][j].cget("text")
                self.board[i][j] = 0 if text == "" else int(text)

    def get_state(self) -> str:
        return ",".join(str(val) for row in self.board for val in row) + ","

    def is_solved(self) -> bool:
        count = 1
        for i in range(self.size):
            for j in range(self.size):
                if i == self.size - 1 and j == self.size - 1:
                    if self.board[i][j] != 0:
                        return False
                else:
                    if self.board[i][j] != count:
                        return False
                    count += 1
        return True

    def apply_action_to_board(self, matrix, action: str):
        """Apply action to both the GUI buttons and the internal board."""
        x, y = self._find_empty()
        moves = {"UP": (1, 0), "DOWN": (-1, 0), "LEFT": (0, 1), "RIGHT": (0, -1)}
        if action in moves:
            dx, dy = moves[action]
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                self._swap_gui(matrix, x, y, nx, ny)
                self.load_current_board(matrix)

    def _swap_gui(self, matrix, x1, y1, x2, y2):
        temp_text = matrix[x1][y1].cget("text")
        temp_bg = matrix[x1][y1].cget("bg")
        matrix[x1][y1].config(text=matrix[x2][y2].cget("text"),
                              bg=matrix[x2][y2].cget("bg"))
        matrix[x2][y2].config(text=temp_text, bg=temp_bg)

    def step(self, action: str) -> int:
        """Execute action on the internal board only. Returns reward."""
        x, y = self._find_empty()
        moves = {"UP": (1, 0), "DOWN": (-1, 0), "LEFT": (0, 1), "RIGHT": (0, -1)}
        if action not in moves:
            return -5

        dx, dy = moves[action]
        nx, ny = x + dx, y + dy
        if 0 <= nx < self.size and 0 <= ny < self.size:
            self.board[x][y], self.board[nx][ny] = self.board[nx][ny], self.board[x][y]
            return 100 if self.is_solved() else -1
        return -5

    def _find_empty(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    return i, j
        return -1, -1

    def reset(self):
        """Randomize the board."""
        nums = list(range(self.size * self.size))
        random.shuffle(nums)
        k = 0
        for i in range(self.size):
            for j in range(self.size):
                self.board[i][j] = nums[k]
                k += 1
