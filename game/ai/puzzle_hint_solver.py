class PuzzleHintSolver:
    """Manhattan-distance heuristic hint solver for n-puzzle."""

    def __init__(self, matrix, size: int):
        self.size = size
        self.board = [[0] * size for _ in range(size)]
        self._convert_matrix(matrix)

    def _convert_matrix(self, matrix):
        for i in range(self.size):
            for j in range(self.size):
                text = matrix[i][j].cget("text")
                self.board[i][j] = 0 if text == "" else int(text)

    def get_hint(self):
        """Return the best next move based on Manhattan heuristic."""
        zx, zy = self._find_zero()
        if zx == -1:
            return None

        directions = [(-1, 0, "UP"), (1, 0, "DOWN"), (0, -1, "LEFT"), (0, 1, "RIGHT")]
        best_move = None
        min_h = float("inf")

        for dx, dy, name in directions:
            nx, ny = zx + dx, zy + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                new_board = [row[:] for row in self.board]
                new_board[zx][zy] = new_board[nx][ny]
                new_board[nx][ny] = 0
                h = self._heuristic(new_board)
                if h < min_h:
                    min_h = h
                    best_move = name

        return best_move

    def _heuristic(self, board) -> int:
        manhattan = 0
        for i in range(self.size):
            for j in range(self.size):
                val = board[i][j]
                if val != 0:
                    target_x = (val - 1) // self.size
                    target_y = (val - 1) % self.size
                    manhattan += abs(i - target_x) + abs(j - target_y)
        return manhattan

    def _find_zero(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    return i, j
        return -1, -1
