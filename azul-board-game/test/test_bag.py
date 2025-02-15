from __future__ import annotations
import unittest
from typing import List
from interfaces.permutation_generator_interface import PermutationGeneratorInterface
from interfaces.used_tiles_interfaces import UsedTilesTakeAllInterface
from azul.bag import Bag
from azul.simple_types import Tile, YELLOW, RED, GREEN


class FakePermutationGenerator(PermutationGeneratorInterface):
    
    def get_permutation(self, length: int) -> list[int]:
        return list(range(length))


class FakeUsedTiles(UsedTilesTakeAllInterface):
    
    def take_all(self) -> List[Tile]:
        return [YELLOW, RED, GREEN, RED]

class TestBag(unittest.TestCase):
    
    bag: Bag
    used_tiles: UsedTilesTakeAllInterface
    permutation_generator: PermutationGeneratorInterface
    
    def setUp(self) -> None:
        self.used_tiles = FakeUsedTiles()
        self.permutation_generator = FakePermutationGenerator()
    
    def test_bag(self) -> None:
        self.bag = Bag([RED, YELLOW, YELLOW, GREEN, RED, RED], 
                       self.used_tiles, self.permutation_generator)
        
        self.assertCountEqual(self.bag.get_tiles(), [GREEN, YELLOW, YELLOW, RED, RED, RED])
        self.assertCountEqual(self.bag.take(3), [RED, YELLOW, YELLOW])
        self.assertCountEqual(self.bag.get_tiles(), [GREEN, RED, RED])
        self.assertCountEqual(self.bag.take(4), [GREEN, RED, RED, YELLOW])
        self.assertCountEqual(self.bag.get_tiles(), [GREEN, RED, RED])
        self.assertCountEqual(self.bag.take(0), [])
        self.assertCountEqual(self.bag.get_tiles(), [RED, GREEN, RED])
        self.assertCountEqual(self.bag.take(3), [RED, GREEN, RED])
        self.assertCountEqual(self.bag.get_tiles(), [])
    
    def test_multiple_take_all_calls(self) -> None:
        self.bag = Bag([RED, YELLOW, YELLOW, GREEN, RED, RED], 
                       self.used_tiles, self.permutation_generator)

        self.assertCountEqual(self.bag.take(4), [RED, YELLOW, YELLOW, GREEN])
        self.assertCountEqual(self.bag.take(7), [RED, RED, YELLOW, RED, GREEN, RED, YELLOW])
        self.assertCountEqual(self.bag.get_tiles(), [RED, GREEN, RED])
        
    def test_initially_empty_bag(self) -> None:
        self.bag = Bag([], self.used_tiles, self.permutation_generator)
        
        self.assertCountEqual(self.bag.get_tiles(), [])
        self.assertCountEqual(self.bag.take(3), [YELLOW, RED, GREEN])
        self.assertCountEqual(self.bag.get_tiles(), [RED])
        self.assertCountEqual(self.bag.take(2), [RED, YELLOW])
        self.assertCountEqual(self.bag.get_tiles(), [RED, RED, GREEN])
    
    def test_take_zero_from_bag(self) -> None:
        self.bag = Bag([], self.used_tiles, self.permutation_generator)
        
        self.assertCountEqual(self.bag.get_tiles(), [])
        self.assertCountEqual(self.bag.take(0), [])
        self.assertCountEqual(self.bag.get_tiles(), [])
        
