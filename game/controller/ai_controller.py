import os
from tkinter import messagebox

from game.ai.puzzle_hint_solver import PuzzleHintSolver
from game.ai.rl_agent import RLAgent
from game.ai.puzzle_env import PuzzleEnv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class AIController:
    """Coordinates AI hint and auto-solve features."""

    def __init__(self, control):
        self.control = control
        self._ai_after_id = None

    def show_hint(self):
        solver = PuzzleHintSolver(self.control.matrix, self.control.SIZE)
        best_move = solver.get_hint()

        if best_move is None:
            messagebox.showinfo("AI Hint", "No hint available!",
                                parent=self.control.pz)
            return
        self.control.move_by_direction(best_move)

    def solve_with_rl(self):
        agent = RLAgent()
        q_table_path = os.path.join(BASE_DIR, "res", "data", "qtable.pkl")
        agent.load_q_table(q_table_path)

        env = PuzzleEnv(self.control.SIZE)
        env.load_current_board(self.control.matrix)

        def step():
            if env.is_solved():
                self._ai_after_id = None
                messagebox.showinfo("AI Solve",
                                    "AI Q-Learning solved the puzzle!",
                                    parent=self.control.pz)
                return

            state = env.get_state()
            action = agent.choose_action(state)
            env.apply_action_to_board(self.control.matrix, action)
            self._ai_after_id = self.control.pz.after(300, step)

        step()

    def stop_ai(self):
        if self._ai_after_id is not None:
            self.control.pz.after_cancel(self._ai_after_id)
            self._ai_after_id = None
            print("AI stopped manually.")
