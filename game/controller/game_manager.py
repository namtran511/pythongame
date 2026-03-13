class GameManager:
    """Manages game states: start, reset, and new game."""

    def __init__(self, control):
        self.control = control

    def start_game(self):
        ctrl = self.control
        if not ctrl.started:
            ctrl.started = True
            ctrl.pz.control_panel.new_game_btn.config(text="Reset")
            ctrl.time_controller.start()
        else:
            ctrl.started = False
        ctrl.is_start_game_flag = 1
        ctrl.is_start_game = True
        ctrl.move_count = 0
        ctrl.pz.info_panel.move_count_label.config(text="0")

    def reset_game(self):
        ctrl = self.control
        ctrl.puzzle_board_manager.add_board()
        ctrl.time_controller.reset()
        ctrl.move_count = 0
        ctrl.pz.info_panel.move_count_label.config(text="0")
        ctrl.pz.control_panel.new_game_btn.config(text="New Game")
        ctrl.is_start_game_flag = 0
        ctrl.started = False

    def new_game(self):
        ctrl = self.control
        ctrl.puzzle_board_manager.add_board()
        ctrl.puzzle_board_manager.mix_button()
        ctrl.pz.control_panel.new_game_btn.config(text="Reset")
        ctrl.is_start_game_flag = 0
