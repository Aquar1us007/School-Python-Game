import sdl2
from sdl2 import *

from camera import Camera
from tile import TileMap
from game_manager import *

class Update():
    def __init__(self):
        self.last_time = 0
        self.current_time = SDL_GetPerformanceCounter()
        self.delta_time = 0
        self.time_since_start = 0

    def update(self, sprites: dict, camera_obj: Camera, tile_map_obj: TileMap, game_manager: GameManager):
        self.last_time = self.current_time
        self.current_time = SDL_GetPerformanceCounter()
        self.delta_time = ((self.current_time - self.last_time) * 1000) / SDL_GetPerformanceFrequency()
        self.time_since_start += self.delta_time / 1000

        camera_obj.update(self.delta_time)
        grid_pos = tile_map_obj.get_grid_positions()
        game_manager.place_tile(tile_map_obj, grid_pos[0], grid_pos[1], game_manager.tile_type_to_place)
        tile_map_obj.get_mouse_position(camera_obj.mouse_x, camera_obj.mouse_y)
        tile_map_obj.get_camera_position(camera_obj.x, camera_obj.y)
        tile_map_obj.update(self.delta_time)