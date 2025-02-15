from __future__ import annotations
from typing import List, Optional
from interfaces.board_pattern_line_interface import BoardPatternLineInterface
from interfaces.pattern_line_interfaces import PatternLineFloorInterface, PatternWallLineInterface
from interfaces.used_tiles_interfaces import UsedTilesGiveInterface
from azul.simple_types import Points, Tile, STARTING_PLAYER, compress_tile_list

class PatternLine(BoardPatternLineInterface):
    
    _capacity: int
    _tiles: List[Tile]
    _current_type: Optional[Tile]
    _floor: PatternLineFloorInterface
    _wall_line: PatternWallLineInterface
    _used_tiles: UsedTilesGiveInterface
    
    def __init__(self, capacity: int, floor: PatternLineFloorInterface, 
                 wall_line: PatternWallLineInterface, used_tiles: UsedTilesGiveInterface) -> None:
        self._capacity = capacity
        self._tiles = []
        self._current_type = None
        self._floor = floor
        self._wall_line = wall_line
        self._used_tiles = used_tiles
    
    def put(self, tiles: List[Tile]) -> None:
        '''Puts extends its _tiles list by tiles, if they're the right type
        
        if tiles are not of the right type, they're dropped on the floor
        excess tiles and STARTING_PLAYER are also dropped
        '''
        if STARTING_PLAYER in tiles:
            tiles.remove(STARTING_PLAYER)
            self._floor.put([STARTING_PLAYER])

        if not tiles:
            return

        if not self.can_put_tiles(tiles):
            self._floor.put(tiles)
            return

        self.append_tiles(tiles)
    
    def append_tiles(self, tiles: List[Tile]) -> None:
        """Extends _tiles till capacity is reached or till tiles list is empty"""
        for tile in tiles.copy():
            if len(self._tiles) == self._capacity:
                self._floor.put(tiles)
                break
            
            self._tiles.append(tile)
            if self._current_type is None:
                self._current_type = tile
            
            tiles.remove(tile)
    
    def can_put_tiles(self, tiles: List[Tile]) -> bool:
        '''Checks whether the tiles match the current type
        
        if current type is None, checks, whether appropriate slot on WallLine is occupied
        expects tiles list to be list of one type of Tile
        '''
        
        if self._current_type is None and self._wall_line.can_put_tile(tiles[0]):
            return True

        return all(tile == self._current_type for tile in tiles)
    
    def finish_round(self) -> Points:
        """If whole pattern line is full, puts one of the tiles to corresponding WallLine
        
        remaining tiles are pushed to UsedTiles
        """
        if len(self._tiles) < self._capacity:
            return Points(0)
        
        tile_to_put: Tile = self._tiles.pop(0)
        tiles_to_give: List[Tile] = self._tiles
        self._used_tiles.give(tiles_to_give)
        self._tiles = []
        self._current_type = None
        
        return self._wall_line.put_tile(tile_to_put)
    
    def state(self) -> str:
        underscores: str = '_' * (self._capacity - len(self._tiles))
        return underscores + compress_tile_list(self._tiles)

    def get_wall_line(self) -> PatternWallLineInterface:
        return self._wall_line
    
    def get_capacity(self) -> int:
        return self._capacity

    def get_floor(self) -> PatternLineFloorInterface:
        return self._floor

    def get_tiles(self) -> List[Tile]:
        return self._tiles
    
    def get_current_type(self) -> Optional[Tile]:
        return self._current_type
