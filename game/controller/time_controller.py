class TimeController:
    """Manages the game timer, updating the UI every second."""

    def __init__(self, control):
        self.control = control
        self._after_id = None
        self.elapsed_time = 0

    def start(self):
        self._tick()

    def _tick(self):
        self.elapsed_time += 1000
        hours = self.elapsed_time // 3600000
        minutes = (self.elapsed_time // 60000) % 60
        seconds = (self.elapsed_time // 1000) % 60
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.control.pz.info_panel.time_label.config(text=time_str)
        self._after_id = self.control.pz.after(1000, self._tick)

    def stop(self):
        if self._after_id is not None:
            self.control.pz.after_cancel(self._after_id)
            self._after_id = None

    def reset(self):
        self.stop()
        self.elapsed_time = 0
        self.control.pz.info_panel.time_label.config(text="00:00:00")
