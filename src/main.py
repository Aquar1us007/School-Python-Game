import sdl2
from sdl2 import * # Importerar allt från SDL2
from sdl2.sdlimage import *
from sdl2.sdlttf import *
import sdl2.sdlmixer as mixer

from window import Window
from render import Renderer
from update import Update
from sprite import Sprite
from game_manager import GameManager
from tile import TileMap
from camera import Camera
from set import *

# Fönstrets inställningar:
WINDOW_TITLE = "Spel"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_FLAGS = SDL_WINDOW_RESIZABLE

# Intern upplösning:
DEFAULT_RESOLUTION = (640, 320)
LOW_RESOLUTION = (320, 180)

class MusicPlayer:
    def __init__(self, path: str):
        if mixer.Mix_OpenAudio(44100, mixer.MIX_DEFAULT_FORMAT, 2, 2048) < 0:
            raise RuntimeError(f"ERROR::MUSIC::Kunde inte start SDL mixer")
    
        self.path = path
        self.music = None
        mixer.Mix_VolumeMusic(64)

    def play_music(self):
        self.music = mixer.Mix_LoadMUS(self.path.encode("utf-8"))
        if not self.music:
            raise RuntimeError(f"ERROR::MUSIC::Kunde inte skapa en låt")

        mixer.Mix_PlayMusic(self.music, -1)

        return self.music

    def stop_music(self):
        mixer.Mix_HaltMusic()
        mixer.Mix_CloseAudio()

class App:
    def __init__(self, title: str, window_width: int, window_height: int, flags: sdl2.Uint32):
        self.resolution_width, self.resolution_height = DEFAULT_RESOLUTION

        self.window_obj = Window(title, window_width, window_height, flags)
        self.render_obj = Renderer(self.resolution_width, self.resolution_height, self.window_obj.window)
        self.update_obj = Update()
        self.running = True

        self.game_manager_obj = GameManager(SAVE_FILE_PATH)
        self.tile_map_obj = TileMap(self.render_obj.renderer, MAP_SIZE, MAP_SIZE)
        self.tile_map_obj.get_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.camera_obj = Camera(((MAP_SIZE * self.tile_map_obj.tile_size) // 2) - 9 * self.tile_map_obj.tile_size - self.tile_map_obj.tile_size // 2, ((MAP_SIZE * self.tile_map_obj.tile_size) // 2) - 5 * self.tile_map_obj.tile_size + self.tile_map_obj.tile_size // 4, 1.0)

        self.state = "start"

        self.music_obj = MusicPlayer("../assets/music.mp3")
        self.music_obj.play_music()

    def handle_input(self) -> bool:
        event = SDL_Event()
        while SDL_PollEvent(event) != 0:
            
            # ==== Start ====
            
            if self.state == "start":
                if event.type == SDL_QUIT:
                    return False
                if event.window.event == SDL_WINDOWEVENT_RESIZED:
                    self.window_obj.resize_window(event.window.data1, event.window.data2)
                    self.tile_map_obj.get_window_size(event.window.data1, event.window.data2)
                if event.type == SDL_KEYDOWN:
                    if event.key.keysym.sym == SDLK_1:
                        self.state = "game"
                    if event.key.keysym.sym == SDLK_2:
                        if self.resolution_width == DEFAULT_RESOLUTION[0] and self.resolution_height == DEFAULT_RESOLUTION[1]:
                            self.resolution_width, self.resolution_height = LOW_RESOLUTION
                        else:
                            self.resolution_width, self.resolution_height = DEFAULT_RESOLUTION
            
            # ==== Spel ====

            if self.state == "game":
                self.camera_obj.handle_input(event)
                if event.type == SDL_QUIT:
                    return False
                if event.type == SDL_WINDOWEVENT:
                    if event.window.event == SDL_WINDOWEVENT_RESIZED:
                        self.window_obj.resize_window(event.window.data1, event.window.data2)
                        self.tile_map_obj.get_window_size(event.window.data1, event.window.data2)
                if event.type == SDL_KEYDOWN:
                    if event.key.keysym.sym == SDLK_ESCAPE:
                        self.state = "start"
                    if event.key.keysym.sym == SDLK_SPACE:
                        self.game_manager_obj.next_week(self.tile_map_obj)
                    if event.key.keysym.sym == SDLK_r:
                        self.game_manager_obj.place_tile_flag = True
                if event.type == SDL_KEYUP:
                    if event.key.keysym.sym == SDLK_r:
                        self.game_manager_obj.place_tile_flag = False
        return True

    def start(self):
        self.sprites = {}
        self.game_manager_obj.start(self.tile_map_obj, self.game_manager_obj.lost)

    def run(self):
        while self.running:
            if self.state == "start":
                self.running = self.handle_input()
                self.render_obj.render_start_gui(self.game_manager_obj)

            if self.state == "game":
                self.running = self.handle_input()
                self.update_obj.update(self.sprites, self.camera_obj, self.tile_map_obj, self.game_manager_obj)
                self.render_obj.render(self.sprites, self.tile_map_obj, self.game_manager_obj)
                if self.game_manager_obj.lost == True:
                    self.start()
                    self.state = "start"
    
    def close(self):
        # Skriver sparfilen innan vi stänger av SDL:
        self.music_obj.stop_music()
        self.game_manager_obj.write_save_file(SAVE_FILE_PATH)

        if self.window_obj.window is None:
            SDL_DestroyWindow(self.window_obj.window)
        IMG_Quit() # Avslutar SDL IMG
        if SDL_WasInit(SDL_INIT_EVERYTHING) != 0: # Avslutar SDL och ger minnet till systemet så vi slipper krascher mm...
            SDL_Quit()

def main() -> int:
    if SDL_Init(SDL_INIT_EVERYTHING) != 0:
        print(f"ERROR::SDL::Kunde inte starta SDL2: {SDL_GetError().decode()}") # SDL_GetError() skriver problemet i bytes och inte i text därför används .decode()
        return 1
    if IMG_Init(IMG_INIT_PNG) == 0:
        print(f"ERROR::SDL_IMAGE::Kunde inte starta SDL image för .PNG bilder")
        return 1
    if TTF_Init() != 0:
        print("ERROR::SDL_TTF::Kunde inte starta SDL TTF")

    app = None
    try:
        app = App(WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_FLAGS)
        app.start()
        app.run()
    except Exception as exception:
        print(f"{exception}")
    finally:
        if app is not None:
            app.close()

    return 0

if __name__ == "__main__":
    main()
