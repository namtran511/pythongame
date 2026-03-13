import tkinter as tk
import random

from game.model.point2d import Point2D
from game.fileserver.w_file import write_file


class PuzzleBoardManager:
    """Creates and manages the puzzle tile grid."""

    def __init__(self, control):
        self.control = control

    def add_board(self):
        """Build the tile grid based on the selected level."""
        level = self.control.pz.info_panel.level_combo.get()
        parts = level.split("x")
        self.control.SIZE = int(parts[0])
        size = self.control.SIZE

        board = self.control.pz.game_board_panel
        for widget in board.winfo_children():
            widget.destroy()

        self.control.matrix = [[None] * size for _ in range(size)]

        for i in range(size):
            board.grid_rowconfigure(i, weight=1)
            board.grid_columnconfigure(i, weight=1)

        font_size = max(12, 28 - (size - 3) * 4)

        for i in range(size):
            for j in range(size):
                value = i * size + j + 1

                if i == size - 1 and j == size - 1:
                    text = ""
                    bg_color = "white"
                else:
                    text = str(value)
                    bg_color = self._get_color_for_value(value, size)

                btn = tk.Button(
                    board,
                    text=text,
                    font=("MV Boli", font_size, "bold"),
                    fg="white",
                    bg=bg_color,
                    activebackground=bg_color,
                    relief=tk.RAISED,
                    bd=2,
                    cursor="hand2",
                )
                btn.grid(row=i, column=j, sticky="nsew", padx=2, pady=2)
                btn.config(command=lambda b=btn: self._on_tile_click(b))
                self.control.matrix[i][j] = btn

    def _on_tile_click(self, btn):
        ctrl = self.control
        if ctrl.is_start_game and ctrl.is_start_game_flag != 0:
            if ctrl.check_move(btn):
                ctrl.move_button(btn)
                if ctrl.check_win():
                    ctrl.time_controller.stop()
                    self._show_win_dialog()
                    ctrl.is_start_game = False
                    write_file(
                        ctrl.pz.info_panel.time_label.cget("text"),
                        ctrl.pz.info_panel.move_count_label.cget("text"),
                    )

    def _show_win_dialog(self):
        dialog = tk.Toplevel(self.control.pz)
        dialog.title("You Won!")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        dialog.configure(bg="#FFE6E6")

        dialog.update_idletasks()
        px = self.control.pz.winfo_x()
        py = self.control.pz.winfo_y()
        pw = self.control.pz.winfo_width()
        ph = self.control.pz.winfo_height()
        dialog.geometry(f"+{px + (pw - 300) // 2}+{py + (ph - 200) // 2}")

        tk.Label(
            dialog,
            text="Congratulations!\nYou Won!",
            font=("Arial", 16, "bold"),
            fg="#FF69B4",
            bg="#FFE6E6",
        ).pack(expand=True)

        def on_continue():
            dialog.destroy()
            self.control.is_start_game = True

        tk.Button(
            dialog,
            text="Continue",
            font=("Arial", 14),
            bg="#90EE90",
            fg="blue",
            command=on_continue,
        ).pack(pady=20)

        dialog.grab_set()
        dialog.focus_set()

    @staticmethod
    def _get_color_for_value(value: int, size: int) -> str:
        """Gradient from pink → yellow → light blue based on tile value."""
        ratio = value / (size * size - 1)

        if ratio < 0.5:
            t = ratio * 2
            r = int(255)
            g = int(182 + (223 - 182) * t)
            b = int(193 + (100 - 193) * t)
        else:
            t = (ratio - 0.5) * 2
            r = int(255 + (173 - 255) * t)
            g = int(223 + (216 - 223) * t)
            b = int(100 + (230 - 100) * t)

        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        return f"#{r:02x}{g:02x}{b:02x}"

    def get_empty_pos(self):
        for i in range(self.control.SIZE):
            for j in range(self.control.SIZE):
                if self.control.matrix[i][j].cget("text") == "":
                    return Point2D(i, j)
        return None

    def mix_button(self):
        """Shuffle tiles by performing 500 random valid moves."""
        for _ in range(500):
            p = self.get_empty_pos()
            choice = random.randint(0, 3)

            if choice == 0 and p.x > 0:
                self._swap(p, p.x - 1, p.y)
            elif choice == 1 and p.y < self.control.SIZE - 1:
                self._swap(p, p.x, p.y + 1)
            elif choice == 2 and p.x < self.control.SIZE - 1:
                self._swap(p, p.x + 1, p.y)
            elif choice == 3 and p.y > 0:
                self._swap(p, p.x, p.y - 1)

    def _swap(self, p: Point2D, x: int, y: int):
        m = self.control.matrix
        temp_text = m[p.x][p.y].cget("text")
        temp_bg = m[p.x][p.y].cget("bg")
        m[p.x][p.y].config(text=m[x][y].cget("text"), bg=m[x][y].cget("bg"))
        m[x][y].config(text=temp_text, bg=temp_bg)
