from __future__ import annotations
from typing import List
from interfaces.factory_interfaces import FactoryTableCenterInterface
from azul.simple_types import Tile, compress_tile_list, STARTING_PLAYER


class TableCenter(FactoryTableCenterInterface):
    
    _tiles: List[Tile]
    
    def __init__(self) -> None:
        self._tiles = []

    def take(self, idx: Tile) -> List[Tile]:
        """Returns all tiles of corresponding type + STARTING_PLAYER tile if it is in _tiles"""
        tiles_to_give = [i for i in self._tiles if i == idx]
        while idx in self._tiles:
            self._tiles.remove(idx)
        
        if STARTING_PLAYER in self._tiles:
            tiles_to_give.append(STARTING_PLAYER)
            self._tiles.remove(STARTING_PLAYER)
        
        return tiles_to_give

    def is_empty(self) -> bool:
        return not self._tiles

    def state(self) -> str:
        return compress_tile_list(sorted(self._tiles, key=str))
    
    def start_new_round(self) -> None:
        """Creates new STARTING_PLAYER tile"""
        self._tiles.append(STARTING_PLAYER)

    def add(self, tiles: List[Tile])-> None:
        self._tiles.extend(tiles)
