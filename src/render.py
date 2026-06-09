import math
import time

import sdl2
from sdl2 import *
from sdl2.sdlimage import *
from sdl2.sdlttf import *

from window import Window
from sprite import Sprite
from sprite import BatchedSprite
from sprite import load_image
from game_manager import GameManager

from tile import TileMap

GAP_BETWEEN_TEXT = 20

class Renderer:
    def __init__(self, RESOLUTION_WIDTH: int=640, RESOLUTION_HEIGHT: int=360, window: SDL_Window=None):
        if window is None:
            raise RuntimeError("ERROR::RENDER::Ett argument var ickegodkänt")

        self.RESOLUTION_WIDTH = RESOLUTION_WIDTH
        self.RESOLUTION_HEIGHT = RESOLUTION_HEIGHT
        self.sdl_window = window
        self.renderer = SDL_CreateRenderer(self.sdl_window, -1, SDL_RENDERER_PRESENTVSYNC | SDL_RENDERER_ACCELERATED)
        if self.renderer is None:
            raise RuntimeError(f"ERROR::RENDER::Kunde inte skapa SDL rendern: {SDL_GetError().decode()}")

        SDL_RenderSetLogicalSize(self.renderer, 640, 360)
        SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, b"nearest")

        # Text:
        self.color = SDL_Color(255, 255, 255)
        self.large_font = sdlttf.TTF_OpenFont(b"../assets/arcade.ttf", 32)
        self.font = sdlttf.TTF_OpenFont(b"../assets/arcade.ttf", 18)
        self.smaller_font = sdlttf.TTF_OpenFont(b"../assets/arcade.ttf", 12)

        self.cloud_sprite = Sprite(self.renderer, 0, 0, RESOLUTION_WIDTH, RESOLUTION_HEIGHT, 0, 0, 320, 160, 1, 1, 0.2, "../assets/cloud.png")
    
    def render_clear(self):
        SDL_RenderClear(self.renderer, 0, 0, 0, 255)

    def render_set_color(self, r: int=0, g: int=0, b: int=0, a: int=255):
        SDL_SetRenderDrawColor(self.renderer, r, g, b, a)
    
    def render_start_gui(self, game_manager: GameManager):
        t = time.time()
        pulse = (math.sin(t) + 1) / 2
        r = int(50 + 100 * pulse)
        g = int(80 + 120 * pulse)
        b = int(150 + 100 * pulse)

        self.render_set_color(r, g, b, 255)
        SDL_RenderClear(self.renderer)

        self.cloud_sprite.draw_sprite()

        score_str = f"HIGH   SCORE   {game_manager.highest_score}"
        score_bytes = score_str.encode()
        score_text_surface = sdlttf.TTF_RenderText_Solid(self.large_font, score_bytes, self.color)
        score_texture = SDL_CreateTextureFromSurface(self.renderer, score_text_surface)
        score_rect = SDL_Rect((self.RESOLUTION_WIDTH - score_text_surface.contents.w) // 2, (self.RESOLUTION_HEIGHT // 2) - score_text_surface.contents.h - 60, score_text_surface.contents.w, score_text_surface.contents.h)
        score_rect_background = SDL_Rect((self.RESOLUTION_WIDTH - score_text_surface.contents.w) // 2 - 5, (self.RESOLUTION_HEIGHT // 2) - score_text_surface.contents.h - 60 - 5, score_text_surface.contents.w + 10, score_text_surface.contents.h + 10)
        self.render_set_color(255, 0, 0, 255)
        SDL_RenderFillRect(self.renderer, score_rect_background)
        self.render_set_color()
        SDL_RenderCopy(self.renderer, score_texture, None, score_rect)

        play_str = f"Tryck   1   for   att   spela"
        play_bytes = play_str.encode()
        play_text_surface = sdlttf.TTF_RenderText_Solid(self.font, play_bytes, self.color)
        play_texture = SDL_CreateTextureFromSurface(self.renderer, play_text_surface)
        play_rect = SDL_Rect((self.RESOLUTION_WIDTH - play_text_surface.contents.w) // 2, (self.RESOLUTION_HEIGHT - play_text_surface.contents.h) // 2, play_text_surface.contents.w, play_text_surface.contents.h)
        SDL_RenderCopy(self.renderer, play_texture, None, play_rect)

        res_str = f"Tryck   2   for   att   andra   upplossningen"
        res_bytes = res_str.encode()
        res_text_surface = sdlttf.TTF_RenderText_Solid(self.font, res_bytes, self.color)
        res_texture = SDL_CreateTextureFromSurface(self.renderer, res_text_surface)
        res_rect = SDL_Rect((self.RESOLUTION_WIDTH - res_text_surface.contents.w) // 2, (self.RESOLUTION_HEIGHT - res_text_surface.contents.h) // 2 + play_text_surface.contents.h + 10, res_text_surface.contents.w, res_text_surface.contents.h)
        SDL_RenderCopy(self.renderer, res_texture, None, res_rect)

        self.render_present()

    def render(self, sprites: dict, tile_map: TileMap, game_manager: GameManager):
        # Rensar skärmen:
        SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 255)
        SDL_RenderClear(self.renderer)
        # Render koden:
        tile_map.draw()

        # GUI:
        score_str = f"Poang   {game_manager.game_data["score"]}"
        score_bytes = score_str.encode()
        score_text_surface = sdlttf.TTF_RenderText_Solid(self.font, score_bytes, self.color)
        score_texture = SDL_CreateTextureFromSurface(self.renderer, score_text_surface)
        score_rect = SDL_Rect((self.RESOLUTION_WIDTH - score_text_surface.contents.w) // 2, 10, score_text_surface.contents.w, score_text_surface.contents.h)
        SDL_RenderCopy(self.renderer, score_texture, None, score_rect)

        week_str = f"Vecka   {game_manager.game_data["week"]}"
        week_bytes = week_str.encode()
        week_text_surface = sdlttf.TTF_RenderText_Solid(self.font, week_bytes, self.color)
        week_texture = SDL_CreateTextureFromSurface(self.renderer, week_text_surface)
        week_rect = SDL_Rect((self.RESOLUTION_WIDTH - week_text_surface.contents.w) // 8, 10, week_text_surface.contents.w, week_text_surface.contents.h)
        SDL_RenderCopy(self.renderer, week_texture, None, week_rect)

        food_str = f"Mat   {game_manager.game_data["food"]}"
        food_bytes = food_str.encode()
        food_text_surface = sdlttf.TTF_RenderText_Solid(self.smaller_font, food_bytes, self.color)
        food_texture = SDL_CreateTextureFromSurface(self.renderer, food_text_surface)
        food_rect = SDL_Rect(score_rect.x + score_text_surface.contents.w + GAP_BETWEEN_TEXT, score_rect.y + 5, food_text_surface.contents.w, food_text_surface.contents.h)
        SDL_RenderCopy(self.renderer, food_texture, None, food_rect)

        wood_str = f"Tra   {game_manager.game_data["wood"]}"
        wood_bytes = wood_str.encode()
        wood_text_surface = sdlttf.TTF_RenderText_Solid(self.smaller_font, wood_bytes, self.color)
        wood_texture = SDL_CreateTextureFromSurface(self.renderer, wood_text_surface)
        wood_rect = SDL_Rect(food_rect.x + food_text_surface.contents.w + GAP_BETWEEN_TEXT, score_rect.y + 5, wood_text_surface.contents.w, wood_text_surface.contents.h)
        SDL_RenderCopy(self.renderer, wood_texture, None, wood_rect)

        stone_str = f"Sten   {game_manager.game_data["stone"]}"
        stone_bytes = stone_str.encode()
        stone_text_surface = sdlttf.TTF_RenderText_Solid(self.smaller_font, stone_bytes, self.color)
        stone_texture = SDL_CreateTextureFromSurface(self.renderer, stone_text_surface)
        stone_rect = SDL_Rect(wood_rect.x + wood_text_surface.contents.w + GAP_BETWEEN_TEXT, score_rect.y + 5, stone_text_surface.contents.w, stone_text_surface.contents.h)
        SDL_RenderCopy(self.renderer, stone_texture, None, stone_rect)

        # Nästa tile:
        tile_to_place_str = "Next  round"
        match game_manager.tile_type_to_place:
            case 1:
                tile_to_place_str = f"Ruta   att   placera   grass"
            case 2:
                tile_to_place_str = f"Ruta   att   placera   skog"
            case 3:
                tile_to_place_str = f"Ruta   att   placera   vete"
            case 4:
                tile_to_place_str = f"Ruta   att   placera   sten"
        
        tile_to_place_bytes = tile_to_place_str.encode()
        tile_to_place_surface = sdlttf.TTF_RenderText_Solid(self.font, tile_to_place_bytes, self.color)
        tile_to_place_texture = SDL_CreateTextureFromSurface(self.renderer, tile_to_place_surface)
        tile_to_place_rect = SDL_Rect((self.RESOLUTION_WIDTH - tile_to_place_surface.contents.w) // 8, 340, tile_to_place_surface.contents.w, tile_to_place_surface.contents.h)
        SDL_RenderCopy(self.renderer, tile_to_place_texture, None, tile_to_place_rect)
        
        # Presenterar fönstret:
        self.render_present()

    def render_present(self):
        SDL_RenderPresent(self.renderer)