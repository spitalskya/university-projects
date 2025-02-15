from __future__ import annotations
from typing import List, Dict
from collections import Counter
from azul.simple_types import Tile
from interfaces.used_tiles_interfaces import UsedTilesTakeAllInterface
from interfaces.combined_interfaces import BagInterface
from interfaces.permutation_generator_interface import PermutationGeneratorInterface


class Bag(BagInterface):
    
    _tiles: List[Tile]
    _used_tiles: UsedTilesTakeAllInterface
    _permutation_generator: PermutationGeneratorInterface   # class that gives random permutation
    
    def __init__(self, tiles: List[Tile], used_tiles: UsedTilesTakeAllInterface, 
                 permutation_generator: PermutationGeneratorInterface) -> None:
        self._tiles = tiles
        self._used_tiles = used_tiles
        self._permutation_generator = permutation_generator
    
    def take(self, count: int) -> List[Tile]:
        """Returns count number of random tiles
        
        if bag does not have enough tiles, it takes_all() from used tiles
        """
        while count > len(self._tiles):
            self.take_all_from_used_tiles()
        
        tiles_to_give: List[Tile] = self.get_random_tiles(count)
        
        tile: Tile
        for tile in tiles_to_give:
            self._tiles.remove(tile)
        
        return tiles_to_give
    
    def get_random_tiles(self, count: int) -> List[Tile]:
        """Gets random permuation of indexes of self._tiles, then returns _tiles by those indexes"""
        permutation: list[int] = self._permutation_generator.get_permutation(len(self._tiles))
        tiles_to_give: List[Tile] = [self._tiles[permutation[i]] for i in range(count)]
        return tiles_to_give

    def take_all_from_used_tiles(self) -> None:
        self._tiles.extend(self._used_tiles.take_all())
    
    def state(self) -> str:
        counted_tiles: Dict[Tile, int] = dict(Counter(self._tiles))
        result: list[str] = []
        tile_type: Tile
        for tile_type in sorted(counted_tiles, key=str):
            result.append(f'|{str(tile_type)}: {counted_tiles[tile_type]}|')
        return ' '.join(result)

    def get_tiles(self) -> List[Tile]:
        return self._tiles
