from __future__ import annotations
from typing import List, Dict
from collections import Counter
from azul.simple_types import Tile, STARTING_PLAYER
from interfaces.combined_interfaces import UsedTilesInterface

class UsedTiles(UsedTilesInterface):
    """Stores used tiles from Floor and PatternLine to by taken by Bag"""
    
    _tiles: List[Tile]

    def __init__(self) -> None:
        self._tiles = []

    def give(self, tiles: List[Tile]) -> None:
        """Takes list of tiles, removes STARTING_PLAYER and extends _tiles with the rest"""
        if STARTING_PLAYER in tiles:
            tiles.remove(STARTING_PLAYER)
        self._tiles.extend(tiles)

    def take_all(self) -> List[Tile]:
        """Returns whole _tiles list and clears it"""
        new_copy: List[Tile] = self._tiles.copy()
        self._tiles.clear()
        return new_copy
        
    def state(self) -> str:
        counted_tiles: Dict[Tile, int] = dict(Counter(self._tiles))
        result: list[str] = []
        tile_type: Tile
        for tile_type in sorted(counted_tiles, key=str):
            result.append(f'|{str(tile_type)}: {counted_tiles[tile_type]}|')
        return ' '.join(result)
    
    def get_tiles(self) -> List[Tile]:
        return self._tiles
