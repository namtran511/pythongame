import os
import tkinter as tk

from game.sound_manager.sound_effect import SoundEffect
from game.sound_manager.options_menu import OptionsMenu

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MainMenu(tk.Toplevel):
    """Main menu window with Play, Options, and Exit buttons."""

    def __init__(self, master):
        super().__init__(master)
        self.master_root = master

        self.title("Puzzle Game")
        self.geometry("530x700")
        self.resizable(False, False)
        self.configure(bg="#F0F0F0")

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 530) // 2
        y = (self.winfo_screenheight() - 700) // 2
        self.geometry(f"+{x}+{y}")

        # Background music
        self.sound = SoundEffect()
        sound_path = os.path.join(BASE_DIR, "res", "SoundEffect", "soundgame.wav")
        if self.sound.set_file(sound_path):
            self.sound.play()
            self.sound.loop()

        # Title area
        title_frame = tk.Frame(self, bg="#F0F0F0", width=430, height=400)
        title_frame.pack(pady=(50, 20))
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame,
            text="PUZZLE\nGAME",
            font=("MV Boli", 52, "bold"),
            fg="#FF69B4",
            bg="#F0F0F0",
        ).pack(expand=True)

        # Buttons
        btn_frame = tk.Frame(self, bg="#F0F0F0")
        btn_frame.pack()

        btn_cfg = dict(
            font=("Arial", 16, "bold"),
            fg="white",
            width=12,
            height=2,
            bd=0,
            cursor="hand2",
            relief=tk.FLAT,
        )

        tk.Button(
            btn_frame,
            text="PLAY GAME",
            bg="#31A9B8",
            activebackground="#2899A8",
            command=self._play_game,
            **btn_cfg,
        ).pack(pady=5)

        tk.Button(
            btn_frame,
            text="OPTIONS",
            bg="#6495ED",
            activebackground="#5485DD",
            command=self._show_options,
            **btn_cfg,
        ).pack(pady=5)

        tk.Button(
            btn_frame,
            text="EXIT",
            bg="#B83131",
            activebackground="#A82121",
            command=self._exit_game,
            **btn_cfg,
        ).pack(pady=5)

        self.protocol("WM_DELETE_WINDOW", self._exit_game)

    def _play_game(self):
        self.withdraw()
        from game.view.puzzle_window import PuzzleWindow

        PuzzleWindow(self.master_root, self)

    def _show_options(self):
        OptionsMenu(self, self.sound)

    def _exit_game(self):
        self.sound.stop_sound()
        self.sound.close()
        self.master_root.destroy()
