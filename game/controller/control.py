import os

from game.model.point2d import Point2D
from game.sound_manager.sound_effect import SoundEffect
from game.controller.time_controller import TimeController
from game.controller.puzzle_board_manager import PuzzleBoardManager
from game.controller.game_manager import GameManager
from game.controller.ai_controller import AIController

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Control:
    """Central controller coordinating game logic, UI, AI, and sound."""

    def __init__(self, puzzle_window):
        self.pz = puzzle_window
        self.SIZE = 3
        self.matrix = None
        self.move_count = 0
        self.started = False
        self.is_start_game = True
        self.is_start_game_flag = 0

        self.sound = SoundEffect()
        self.sound_move_path = os.path.join(BASE_DIR, "res", "SoundEffect", "move.wav")

        self.time_controller = TimeController(self)
        self.puzzle_board_manager = PuzzleBoardManager(self)
        self.game_manager = GameManager(self)
        self.ai_controller = AIController(self)

        self.puzzle_board_manager.add_board()

    def check_win(self) -> bool:
        if self.matrix[self.SIZE - 1][self.SIZE - 1].cget("text") != "":
            return False
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if i == self.SIZE - 1 and j == self.SIZE - 1:
                    return True
                if self.matrix[i][j].cget("text") != str(i * self.SIZE + j + 1):
                    return False
        return True

    def move_button(self, button):
        """Move a tile into the empty space."""
        p = self.puzzle_board_manager.get_empty_pos()
        button_text = button.cget("text")
        button_bg = button.cget("bg")

        self.matrix[p.x][p.y].config(text=button_text, bg=button_bg)
        button.config(text="", bg="white")

        self.move_count += 1
        self.pz.info_panel.move_count_label.config(text=str(self.move_count))

        self.sound.set_file(self.sound_move_path)
        self.sound.play()

    def check_move(self, button) -> bool:
        """Check if the clicked tile is adjacent to the empty space."""
        if button.cget("text") == "":
            return False

        p = self.puzzle_board_manager.get_empty_pos()
        clicked_point = None

        btn_text = button.cget("text")
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if self.matrix[i][j].cget("text") == btn_text:
                    clicked_point = Point2D(i, j)
                    break
            if clicked_point:
                break

        if clicked_point is None:
            return False

        if p.x == clicked_point.x and abs(p.y - clicked_point.y) == 1:
            return True
        if p.y == clicked_point.y and abs(p.x - clicked_point.x) == 1:
            return True
        return False

    def move_by_direction(self, direction: str):
        """Move the empty space in the given direction."""
        p = self.puzzle_board_manager.get_empty_pos()
        x, y = p.x, p.y

        if direction == "UP" and x < self.SIZE - 1:
            self.move_button(self.matrix[x + 1][y])
        elif direction == "DOWN" and x > 0:
            self.move_button(self.matrix[x - 1][y])
        elif direction == "LEFT" and y < self.SIZE - 1:
            self.move_button(self.matrix[x][y + 1])
        elif direction == "RIGHT" and y > 0:
            self.move_button(self.matrix[x][y - 1])

    def reset_game(self):
        self.game_manager.reset_game()

    def start_game(self):
        self.game_manager.start_game()

    def new_game(self):
        self.game_manager.new_game()

    def ai_support(self):
        self.ai_controller.show_hint()

    def ai_solve(self):
        self.ai_controller.solve_with_rl()

    def stop_ai(self):
        self.ai_controller.stop_ai()
