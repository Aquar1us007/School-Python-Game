import math
from ctypes import byref, c_int

from sdl2 import *

class Camera:
    def __init__(self, x: float, y: float, camera_speed: float):
        self.x = x
        self.y = y
        self.camera_speed = camera_speed

        self.mouse_x = c_int()
        self.mouse_y = c_int()

        self.w = False
        self.a = False
        self.s = False
        self.d = False

    def handle_input(self, event: SDL_Event):
        SDL_GetMouseState(byref(self.mouse_x), byref(self.mouse_y))

        if event.type == SDL_KEYDOWN:
            key = event.key.keysym.sym
            if key == SDLK_w:
                self.w = True
            if key == SDLK_a:
                self.a = True
            if key == SDLK_s:
                self.s = True
            if key == SDLK_d:
                self.d = True

        if event.type == SDL_KEYUP:
            key = event.key.keysym.sym
            if key == SDLK_w:
                self.w = False
            if key == SDLK_a:
                self.a = False
            if key == SDLK_s:
                self.s = False
            if key == SDLK_d:
                self.d = False

    def update(self, delta_time: float):
        vel_x = 0
        vel_y = 0

        if self.w:
            vel_y -= 1
        if self.a:
            vel_x -= 1
        if self.s:
            vel_y += 1
        if self.d:
            vel_x += 1

        length = math.sqrt(vel_x**2 + vel_y**2)
        if length != 0:
            vel_x /= length
            vel_y /= length

        self.x += vel_x * self.camera_speed * delta_time
        self.y += vel_y * self.camera_speed * delta_time