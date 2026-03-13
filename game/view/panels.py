import tkinter as tk
from tkinter import ttk

from game.fileserver.w_file import read_file


class TitlePanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#E8E8E8")
        self.title_label = tk.Label(
            self,
            text="PUZZLE GAME SIMPLE",
            font=("MV Boli", 25, "bold"),
            bg="#E8E8E8",
        )
        self.title_label.pack(pady=10)


class InfoPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")

        font = ("Arial", 14)

        row = tk.Frame(self, bg="white")
        row.pack(pady=10)

        tk.Label(row, text="Time:", font=font, bg="white").pack(side=tk.LEFT, padx=10)
        self.time_label = tk.Label(row, text="00:00:00", font=font, bg="white")
        self.time_label.pack(side=tk.LEFT, padx=10)

        tk.Label(row, text="Level:", font=font, bg="white").pack(side=tk.LEFT, padx=10)
        levels = read_file()
        self.level_combo = ttk.Combobox(
            row, values=levels, state="readonly", width=6, font=font
        )
        if levels:
            self.level_combo.current(0)
        self.level_combo.pack(side=tk.LEFT, padx=10)

        tk.Label(row, text="Moves:", font=font, bg="white").pack(
            side=tk.LEFT, padx=10
        )
        self.move_count_label = tk.Label(row, text="0", font=font, bg="white")
        self.move_count_label.pack(side=tk.LEFT, padx=10)


class ControlPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")

        row = tk.Frame(self, bg="white")
        row.pack(pady=10)

        btn_cfg = dict(
            font=("Arial", 12),
            fg="white",
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            relief=tk.FLAT,
        )

        self.new_game_btn = tk.Button(row, text="New Game", bg="#FFB6C1", **btn_cfg)
        self.new_game_btn.pack(side=tk.LEFT, padx=5)

        self.ai_support_btn = tk.Button(row, text="AI Hint", bg="#ADD8E6", **btn_cfg)
        self.ai_support_btn.pack(side=tk.LEFT, padx=5)

        self.ai_solve_btn = tk.Button(row, text="AI Solve", bg="#98D8C8", **btn_cfg)
        self.ai_solve_btn.pack(side=tk.LEFT, padx=5)

        self.out_game_btn = tk.Button(row, text="Out Game", bg="#DDA0DD", **btn_cfg)
        self.out_game_btn.pack(side=tk.LEFT, padx=5)

        self.stop_ai_btn = tk.Button(row, text="Stop AI", bg="#F0E68C", **btn_cfg)
        self.stop_ai_btn.pack(side=tk.LEFT, padx=5)


class GameBoardPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white", bd=2, relief=tk.SUNKEN)
