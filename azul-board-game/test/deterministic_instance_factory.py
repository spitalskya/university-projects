from __future__ import annotations
from typing import List
from azul.simple_types import Tile, BLACK, BLUE, GREEN, RED, YELLOW
from azul.bag import Bag
from azul.instance_factory import InstanceFactory
from interfaces.combined_interfaces import BagInterface
from interfaces.used_tiles_interfaces import UsedTilesTakeAllInterface
from interfaces.permutation_generator_interface import PermutationGeneratorInterface


class TrivialPermutationGenerator(PermutationGeneratorInterface):
    def get_permutation(self, length: int) -> list[int]:
        return list(range(length))

class DeterministicInstanceFactory(InstanceFactory):
    """Class that behaves exactly like InstanceFactory, but creates deterministic Bag"""
    
    def get_bag(self, used_tiles: UsedTilesTakeAllInterface) -> BagInterface:
        tiles: List[Tile] =  [BLACK, BLACK, BLUE, BLUE, GREEN, GREEN, 
                              RED, RED, YELLOW, YELLOW] * 10
        return Bag(tiles, used_tiles, TrivialPermutationGenerator())
