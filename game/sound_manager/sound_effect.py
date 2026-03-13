import os

try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except (ImportError, Exception):
    PYGAME_AVAILABLE = False


class SoundEffect:
    def __init__(self):
        self._sound = None
        self._channel = None
        self._current_file = None

    def set_file(self, sound_file: str) -> bool:
        if not PYGAME_AVAILABLE:
            return False
        if self._current_file == sound_file and self._sound is not None:
            return True
        try:
            if not os.path.exists(sound_file):
                print(f"Sound file not found: {sound_file}")
                return False
            self._sound = pygame.mixer.Sound(sound_file)
            self._current_file = sound_file
            return True
        except Exception as e:
            print(f"Error loading sound: {e}")
            return False

    def play(self):
        if self._sound and PYGAME_AVAILABLE:
            self._channel = self._sound.play()

    def loop(self):
        if self._sound and PYGAME_AVAILABLE:
            self._channel = self._sound.play(loops=-1)

    def stop_sound(self):
        if self._channel and PYGAME_AVAILABLE:
            self._channel.stop()

    def close(self):
        self._sound = None
        self._channel = None
        self._current_file = None
