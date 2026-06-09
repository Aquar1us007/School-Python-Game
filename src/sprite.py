from sdl2 import *
from sdl2.sdlimage import *

def load_image(renderer: SDL_Renderer, path: str) -> SDL_Texture:
    surface = IMG_Load(path.encode("utf-8"))
    if not surface:
        raise RuntimeError(f"ERROR::LOAD_IMAGE::Kunde inte ladda en bild: PATH: {path}")

    # Gör om bilden till en textur:
    texture = SDL_CreateTextureFromSurface(renderer, surface)
    SDL_FreeSurface(surface)
    if not texture:
        raise RuntimeError(f"ERROR::LOAD_IMAGE::Kunde inte skapa en texture {SDL_GetError().decode()}")

    return texture

class Sprite:
    def __init__(self, renderer: SDL_Renderer, x: float=0, y: float=0, width: int=32, height: int=32, uv_x: int=0, uv_y: int=0,  uv_width: int=32, uv_height: int=32, n_frames: int=1, n_rows: int=1, animation_speed: float=0.2, texture_path: str=""):
        self.renderer = renderer
        if self.renderer is None:
            raise RuntimeError("ERROR::SPRITE::Ett argument var ickegodkänt")

        # Position
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Textur:
        self.uv_x = uv_x
        self.uv_y = uv_y
        self.uv_width = uv_width
        self.uv_height = uv_height
        if uv_width == 0 and uv_height == 0:
            uv_width = width
            uv_height = height
        self.texture = load_image(self.renderer, texture_path)

        # Animation:
        self.s_rect = SDL_Rect(uv_x, uv_y, uv_width, uv_height)
        self.current_frame = 0
        self.current_row = 0
        self.n_frames = n_frames
        self.n_rows = n_rows
        self.animation_speed = animation_speed * 1000 # Konverterar till sekunder!
        self.animation_timer = 0

    def draw_sprite(self):
        d_rect = SDL_Rect(round(self.x), round(self.y), self.width, self.height)
        SDL_RenderCopy(self.renderer, self.texture, self.s_rect, d_rect)

    def move_sprite(self, new_x: int, new_y: int):
        self.x = new_x
        self.y = new_y

    def change_texture(self, path: str=""):
        self.texture = load_image(path)

    def animate_sprite(self, delta_time: float):
        self.animation_timer += delta_time

        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0

            self.current_frame += 1
            if self.current_frame >= self.n_frames:
                self.current_frame = 0
                self.current_row = self.current_row + 1
                if self.current_row >= self.n_rows:
                    self.current_row = 0

            self.uv_x = self.uv_width * self.current_frame
            self.uv_y = self.uv_height * self.current_row
            self.s_rect.x = self.uv_x
            self.s_rect.y = self.uv_y

    def destroy_sprite(self):
        if self.texture is not None:
            SDL_DestroyTexture(self.texture)

class BatchedSprite:
    def __init__(self, x: float, y: float, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw_sprite(self, renderer: SDL_Renderer, texture: SDL_Texture, uv_x: int, uv_y: int, uv_width: int, uv_height: int):
        d_rect = SDL_Rect(round(self.x), round(self.y), self.width, self.height)
        self.s_rect = SDL_Rect(uv_x, uv_y, uv_width, uv_height)
        SDL_RenderCopy(renderer, texture, self.s_rect, d_rect)