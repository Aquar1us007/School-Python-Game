from math import floor

import sdl2
from sdl2 import SDL_RenderSetLogicalSize

class Window:
    def __init__(self, title: str, window_width: int, window_height: int, flags: sdl2.Uint32):
        self.width = window_width
        self.height = window_height

        self.window = sdl2.SDL_CreateWindow(
            title.encode("utf-8"), # Title behöver vara 1 - 4 bytes(utf-8) men Python använder Unicode där text är 1, 2 eller 4 bytes
            sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED,
            window_width, window_height,
            flags
        )
        if not self.window:
            raise RuntimeError(f"ERROR::SDL::Kunde inte skapa SDL fönstret: {SDL_GetError().decode()}")

    def resize_window(self, new_width: int, new_height: int):
        self.width = new_width
        self.height = new_height