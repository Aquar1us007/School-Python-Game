import random
import math

from tile import *
from set import *

class GameManager:
    def __init__(self, save_file_path: str):
        if save_file_path is None:
            raise RuntimeError("ERROR::GAME_MANAGER::Kunde inte hitta spar filen!")

        self.save_file_path = save_file_path
        self.save_data = {
            "score" : 0,
            "week" : 0,
            "food" : 0,
            "wood" : 0,
            "stone" : 0
        }
        self.read_save_file(self.save_file_path)

        # Placera en "tile":
        self.tile_map = None
        self.has_placed_tile = False
        self.place_tile_flag = False
        self.tile_type_to_place = 0

        self.lost = False
        self.highest_score = self.save_data["score"]

        self.game_data = {
            "score" : self.save_data["score"],
            "week" : self.save_data["week"],
            "food" : self.save_data["food"],
            "wood" : self.save_data["wood"],
            "stone" : self.save_data["stone"],
        }

        if self.game_data["week"] == 0:
            self.game_data["score"] = 0

    def read_save_file(self, save_file_path: str):
        self.loaded_tiles = []
        try:
            with open(save_file_path, "r") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue

                    key, value = line.split("=", 1)
                    if key == "score":
                        self.save_data["score"] = int(value)
                    elif key == "week":
                        self.save_data["week"] = int(value)
                    elif key == "resources":
                        for res in value.split(","):
                            if not res:
                                continue
                            res_key, res_val = res.split(":")
                            self.save_data[res_key] = int(res_val)
                    elif key == "tile":
                        x, y, t_type = value.split(",")
                        self.loaded_tiles.append((int(x), int(y), int(t_type)))

        except FileNotFoundError:
            raise RuntimeError("ERROR::SAVE_LOADING::Kunde inte hitta data från sparfilen")

    def write_save_file(self, save_file_path: str):
        try:
            score_to_save = max(self.highest_score, self.save_data.get("score", 0))
            with open(save_file_path, "w") as file:
                file.write(f"score={score_to_save}\n")
                file.write(f"week={self.game_data["week"]}\n")
                file.write(
                    f"resources=food:{self.game_data["food"]},"
                    f"wood:{self.game_data["wood"]},"
                    f"stone:{self.game_data["stone"]}\n"
                )

                if self.tile_map is not None:
                    for y in range(self.tile_map.height):
                        for x in range(self.tile_map.width):
                            t = self.tile_map.tiles[x][y]
                            if t.type != 0:
                                file.write(f"tile={x},{y},{t.type}\n")
    
        except Exception as e:
            raise RuntimeError(f"ERROR::SAVE_LOADING::Kunde inte spara filen: {e}")
    
    def pick_random_tile_type(self) -> int:
        type = random.randint(1, N_TILE_TYPES)
        return type

    def start(self, tile_map: TileMap, new_game: bool=False):
        self.tile_map = tile_map

        self.tile_map.set_tile(MAP_SIZE // 2, MAP_SIZE // 2, 1)

        if not new_game and self.lost != True:
            for x, y, t_type in getattr(self, "loaded_tiles", []):
                tile_map.set_tile(x, y, t_type)

            for key in self.game_data:
                if key == "score" or key == "week":
                    continue

                if self.game_data["week"] == 0:
                    self.game_data[key] = N_STARTING_RESOURCES

            self.has_placed_tile = True
        else:
            self.lost = False
            self.game_data = {
            "score" : 0,
            "week" : 0,
            "food" : N_STARTING_RESOURCES,
            "wood" : N_STARTING_RESOURCES,
            "stone" : N_STARTING_RESOURCES
            }

            for y in range(tile_map.height):
                for x in range(tile_map.width):
                    tile_map.set_tile(x, y, 0)
            
            tile_map.set_tile(MAP_SIZE // 2, MAP_SIZE // 2, 1)

    def place_tile(self, tile_map: TileMap, x: int, y: int, type: int):
        if self.place_tile_flag and self.has_placed_tile != True:
            if tile_map.tiles[x][y].type != 0:
                return
            
            allow_tile_placement = False
            neighbor_offsets = [
                (0, -1),
                (0, 1),
                (-1, 0),
                (1, 0)
            ]

            for dx, dy in neighbor_offsets:
                t_x = x + dx
                t_y = y + dy
                if 0 <= t_x < tile_map.width and 0 <= t_y < tile_map.height:
                    if tile_map.tiles[t_x][t_y].type != 0:
                        allow_tile_placement = True
                        break
                    
            if allow_tile_placement:
                tile_map.set_tile(x, y, type)
                self.has_placed_tile = True
    
    def next_week(self, tile_map: TileMap):
        if self.has_placed_tile:
            self.check_tiles(tile_map)

            # Dålig "Tile":
            has_placed_bad_tile = False
            bad_tile_attempts = 0
            if random.randint(1, 6) == 5 and self.game_data["week"] > 3:
                while has_placed_bad_tile != True and bad_tile_attempts != tile_map.width * tile_map.height:
                    x = random.randint(0, tile_map.width - 1)
                    y = random.randint(0, tile_map.height - 1)
                    if tile_map.tiles[x][y].type != 0:
                        continue

                    allow_tile_placement = False
                    neighbor_offsets = [
                        (0, -1),
                        (0, 1),
                        (-1, 0),
                        (1, 0)
                    ]

                    for dx, dy in neighbor_offsets:
                        t_x = x + dx
                        t_y = y + dy
                        if 0 <= t_x < tile_map.width and 0 <= t_y < tile_map.height:
                            if tile_map.tiles[t_x][t_y].type != 0:
                                allow_tile_placement = True
                                break
                    
                    if allow_tile_placement:
                        tile_map.tiles[x][y].type = 5
                    
                    if tile_map.tiles[x][y].type == 5:
                        has_placed_bad_tile = True
                        break
                    
                    bad_tile_attempts += 1

            # Flytta till nästa vecka:
            if self.game_data["week"] >= TAX_START_WEEK:
                tax = int(3 + TAX_AMOUNT * math.log1p(self.game_data["week"] - TAX_START_WEEK))
                self.game_data["food"] -= tax
                self.game_data["wood"] -= tax
                self.game_data["stone"] -= tax
            self.game_data["week"] += 1
            self.game_data["score"] += 1

            self.game_over()

            self.tile_type_to_place = self.pick_random_tile_type()
            self.has_placed_tile = False

            if self.lost == True:
                return

    # Kollar alla utsatta tiles för poäng: s
    def check_tiles(self, tile_map: TileMap):
        neighbor_offsets = [
            (0, -1),
            (0, 1),
            (-1, 0),
            (1, 0)
        ]

        factory_neighbor_offsets = [
            (-1, 0),
            (-1, 1),
            (0, 1),
            (1, 1),
            (1, 0),
            (1, -1),
            (0, -1),
            (-1, -1)
        ]

        counted_pairs = set()
        blocked_tiles = set()

        for y in range(tile_map.height):
            for x in range(tile_map.width):
                if tile_map.tiles[x][y].type == 5:
                    for dx, dy in factory_neighbor_offsets:
                        t_x = x + dx
                        t_y = y + dy
                        if 0 <= t_x < tile_map.width and 0 <= t_y < tile_map.height:
                            blocked_tiles.add((t_x, t_y))

        for y in range(tile_map.height):
            for x in range(tile_map.width):
                if tile_map.tiles[x][y].type == 0:
                    continue

                if (x, y) in blocked_tiles:
                    continue

                current_tile_type = tile_map.tiles[x][y].type

                match current_tile_type:
                    case 2:
                        self.game_data["wood"] += 1
                    case 3:
                        self.game_data["food"] += 1
                    case 4:
                        self.game_data["stone"] += 1

                for dx, dy in neighbor_offsets:
                    t_x = x + dx
                    t_y = y + dy
                    if 0 <= t_x < tile_map.width and 0 <= t_y < tile_map.height:
                        if current_tile_type == tile_map.tiles[t_x][t_y].type and (t_x, t_y) not in blocked_tiles:
                            pair = tuple(sorted([(x, y), (t_x, t_y)]))
                            if pair not in counted_pairs:
                                counted_pairs.add(pair)
                                match current_tile_type:
                                    case 2:
                                        self.game_data["wood"] += 1
                                    case 3:
                                        self.game_data["food"] += 1
                                    case 4:
                                        self.game_data["stone"] += 1

    def game_over(self):
        for key in self.game_data:
            if key == "score" or key == "week":
                continue
            
            if self.game_data[key] < 0:
                if self.game_data["score"] > self.highest_score:
                    self.highest_score = self.game_data["score"]
                self.lost = True