from ctypes import c_int
from math import floor
from enum import Enum

from sdl2 import SDL_Renderer
from sprite import BatchedSprite
from sprite import Sprite
from sprite import load_image
from window import Window

# Konstanter:
TILE_SIZE = 32
TILE_UV_SIZE = 32

RENDER_WIDTH = 640
RENDER_HEIGHT = 360

ASSET_FILE_PATH = "../assets/tiles.png"
CURSOR_TILE_PATH = "../assets/selected.png"

class TileType(Enum):
    WATER = 0
    GRASS = 1
    WOODS = 2
    WHEAT = 3
    STONE = 4
    FACTORY = 5

class Tile:
    def __init__(self, x: float, y: float, type: int):
        self.x = x
        self.y = y
        self.type = type

class TileMap:
    def __init__(self, renderer: SDL_Renderer, width: int, height: int):
        self.width = width
        self.height = height
        self.renderer = renderer
        self.tile_size = TILE_SIZE

        self.batched_sprite = BatchedSprite(0, 0, TILE_SIZE, TILE_SIZE)
        self.texture = load_image(self.renderer, ASSET_FILE_PATH)
        self.texture_uvs = {
            "water" : (0, 0, 32, 32),
            "grass" : (64, 0, 32, 32),
            "woods" : (96, 0, 32, 32),
            "wheat" : (128, 0, 32, 32),
            "stone" : (160, 0, 32, 32),
            "factory": (192, 0, 32, 32),
        }

        self.selected_sprite = Sprite(self.renderer, 0, 0, 32, 32, 0, 0, 32, 32, 2, 1, 0.750, CURSOR_TILE_PATH)

        self.tiles = [[0 for _ in range(height)] for _ in range(width)] # Skapar en 2D array av alla "tiles"
        for x in range(self.width):
            for y in range(self.height):
                self.tiles[x][y] = Tile(x * TILE_SIZE, y * TILE_SIZE, 0)

        self.camera_x = 0
        self.camera_y = 0
        self.mouse_x = c_int()
        self.mouse_y = c_int()
        self.grid_x = 0
        self.grid_y = 0
        self.window_width = 1920
        self.window_height = 1080

        self.global_animation_speed = 1.5 * 1000
        self.global_animation_frame = 0
        self.n_global_frames = 2
        self.n_global_rows = 1
        self.global_current_row = 0
        self.animation_timer = 0

    def get_window_size(self, width, height):
        self.window_width = float(width)
        self.window_height = float(height)

    def get_camera_position(self, x, y):
        self.camera_x = float(x)
        self.camera_y = float(y)

    def get_mouse_position(self, x, y):
        mouse_x = float(x.value)
        mouse_y = float(y.value)

        logical_x = mouse_x * (RENDER_WIDTH / self.window_width)
        logical_y = mouse_y * (RENDER_HEIGHT / self.window_height)

        logical_x += self.camera_x
        logical_y += self.camera_y

        self.grid_x = int(logical_x // TILE_SIZE)
        self.grid_y = int(logical_y // TILE_SIZE)
    
    def get_grid_positions(self):
        return self.grid_x, self.grid_y

    def set_tile(self, x: int, y: int, type: int):
        self.tiles[x][y].type = type

    def update(self, delta_time: float):
        self.selected_sprite.animate_sprite(delta_time)

        self.animation_timer += delta_time

        if self.animation_timer >= self.global_animation_speed:
            self.animation_timer = 0

            self.global_animation_frame += 1
            if self.global_animation_frame >= self.n_global_frames:
                self.global_animation_frame = 0
                self.global_current_row = self.global_current_row + 1
                if self.global_current_row >= self.n_global_rows:
                    self.global_current_row = 0

    def draw(self):
        start_tile_x = int(self.camera_x // TILE_SIZE)
        start_tile_y = int(self.camera_y // TILE_SIZE)

        tiles_across = (RENDER_WIDTH // TILE_SIZE) + 2
        tiles_down = (RENDER_HEIGHT // TILE_SIZE) + 2

        end_tile_x = min(self.width, start_tile_x + tiles_across)
        end_tile_y = min(self.height, start_tile_y + tiles_down)
        for y in range(max(0, start_tile_y), end_tile_y):
            for x in range(max(0, start_tile_x), end_tile_x):
                if x == self.grid_x and y == self.grid_y:
                    screen_x = (x * TILE_SIZE) - self.camera_x
                    screen_y = (y * TILE_SIZE) - self.camera_y
                    self.selected_sprite.move_sprite(screen_x, screen_y)
                tile = self.tiles[x][y]
                screen_x = tile.x - self.camera_x
                screen_y = tile.y - self.camera_y

                self.batched_sprite.x = screen_x
                self.batched_sprite.y = screen_y

                match tile.type:
                    case TileType.WATER.value:
                        uv_x, uv_y, uv_width, uv_height = self.texture_uvs["water"]
                        uv_x = TILE_SIZE * self.global_animation_frame
                        self.batched_sprite.draw_sprite(self.renderer, self.texture, uv_x, uv_y, uv_width, uv_height)
                    case TileType.GRASS.value:
                        uv_x, uv_y, uv_width, uv_height = self.texture_uvs["grass"]
                        self.batched_sprite.draw_sprite(self.renderer, self.texture, uv_x, uv_y, uv_width, uv_height)
                    case TileType.WOODS.value:
                        uv_x, uv_y, uv_width, uv_height = self.texture_uvs["woods"]
                        self.batched_sprite.draw_sprite(self.renderer, self.texture, uv_x, uv_y, uv_width, uv_height)
                    case TileType.WHEAT.value:
                        uv_x, uv_y, uv_width, uv_height = self.texture_uvs["wheat"]
                        self.batched_sprite.draw_sprite(self.renderer, self.texture, uv_x, uv_y, uv_width, uv_height)
                    case TileType.STONE.value:
                        uv_x, uv_y, uv_width, uv_height = self.texture_uvs["stone"]
                        self.batched_sprite.draw_sprite(self.renderer, self.texture, uv_x, uv_y, uv_width, uv_height)
                    case TileType.FACTORY.value:
                        uv_x, uv_y, uv_width, uv_height = self.texture_uvs["factory"]
                        self.batched_sprite.draw_sprite(self.renderer, self.texture, uv_x, uv_y, uv_width, uv_height)

                self.selected_sprite.draw_sprite()
