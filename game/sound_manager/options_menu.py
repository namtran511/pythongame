import tkinter as tk


class OptionsMenu(tk.Toplevel):
    """Sound options dialog with play/stop music buttons."""

    def __init__(self, parent, sound):
        super().__init__(parent)
        self.sound = sound

        self.title("Options Menu")
        self.geometry("350x220")
        self.resizable(False, False)
        self.configure(bg="#E6F0FF")

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 350) // 2
        y = (self.winfo_screenheight() - 220) // 2
        self.geometry(f"+{x}+{y}")

        frame = tk.Frame(self, bg="#E6F0FF")
        frame.pack(expand=True)

        tk.Button(
            frame,
            text="Play Music",
            font=("Arial", 14, "bold"),
            bg="#66CCFF",
            fg="white",
            width=20,
            height=2,
            bd=0,
            command=self._play_music,
        ).pack(pady=10)

        tk.Button(
            frame,
            text="Stop Music",
            font=("Arial", 14, "bold"),
            bg="#FF6666",
            fg="white",
            width=20,
            height=2,
            bd=0,
            command=self._stop_music,
        ).pack(pady=10)

    def _play_music(self):
        self.sound.play()
        self.sound.loop()

    def _stop_music(self):
        self.sound.stop_sound()
