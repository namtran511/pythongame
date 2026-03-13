import tkinter as tk

from game.view.panels import TitlePanel, InfoPanel, ControlPanel, GameBoardPanel


class PuzzleWindow(tk.Toplevel):
    """Main game window containing the puzzle board and controls."""

    def __init__(self, master, main_menu):
        super().__init__(master)
        self.master_root = master
        self.main_menu = main_menu

        self.title("Puzzle Game")
        self.geometry("850x850")
        self.configure(bg="#E8E8E8")

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 850) // 2
        y = (self.winfo_screenheight() - 850) // 2
        self.geometry(f"+{x}+{y}")

        self.title_panel = TitlePanel(self)
        self.info_panel = InfoPanel(self)
        self.control_panel = ControlPanel(self)
        self.game_board_panel = GameBoardPanel(self)

        self.title_panel.pack(side=tk.TOP, fill=tk.X)
        self.game_board_panel.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        bottom_frame = tk.Frame(self, bg="white")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.info_panel.pack(in_=bottom_frame, fill=tk.X)
        self.control_panel.pack(in_=bottom_frame, fill=tk.X)

        from game.controller.control import Control

        self.control = Control(self)

        from game.view.puzzle_action import PuzzleAction

        self.action = PuzzleAction(self)

        self.control_panel.new_game_btn.config(command=self.action.on_new_game)
        self.control_panel.out_game_btn.config(command=self.action.on_out_game)
        self.control_panel.ai_support_btn.config(command=self.action.on_ai_support)
        self.control_panel.ai_solve_btn.config(command=self.action.on_ai_solve)
        self.control_panel.stop_ai_btn.config(command=self.action.on_stop_ai)

        # Start with a shuffled, playable game as soon as the window opens
        self.control.new_game()
        self.control.start_game()

        self.info_panel.level_combo.bind(
            "<<ComboboxSelected>>", self._on_level_change
        )
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_level_change(self, _event):
        self.control.reset_game()

    def _on_close(self):
        self.control.stop_ai()
        self.control.time_controller.stop()
        self.destroy()
        self.main_menu.deiconify()
