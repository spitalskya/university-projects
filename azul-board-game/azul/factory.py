from __future__ import annotations
from typing import List
from interfaces.factory_interfaces import FactoryBagInterface, FactoryTableCenterInterface
from interfaces.tile_source import TileSource
from azul.simple_types import Tile, compress_tile_list


class Factory(TileSource):
    
    _tiles: List[Tile]
    _bag: FactoryBagInterface
    _table_center: FactoryTableCenterInterface
    
    def __init__(self, bag: FactoryBagInterface, table_center: FactoryTableCenterInterface) -> None:
        self._tiles = []
        self._bag = bag
        self._table_center = table_center

    def take(self, idx: Tile) -> List[Tile]:
        """Returns all tiles of give type, the rest are added to Table Center"""
        tiles_to_take: List[Tile] = [i for i in self._tiles if i == idx]
        while idx in self._tiles:
            self._tiles.remove(idx)
        self._table_center.add(self._tiles)
        self._tiles.clear()
        return tiles_to_take

    def is_empty(self) -> bool:
        return not bool(self._tiles)

    def state(self) -> str:
        return compress_tile_list(sorted(self._tiles, key=str))    
    
    def start_new_round(self) -> None:
        """Takes 4 new tile from bag"""
        self._tiles.extend(self._bag.take(4))
