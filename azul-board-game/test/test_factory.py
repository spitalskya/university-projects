from __future__ import annotations
import unittest
from typing import List
from interfaces.factory_interfaces import FactoryBagInterface, FactoryTableCenterInterface
from azul.simple_types import Tile, RED, YELLOW, BLACK, GREEN, compress_tile_list
from azul.factory import Factory

class FakeTableCenter(FactoryTableCenterInterface):
    tiles: List[Tile]
    
    def __init__(self) -> None:
        self.tiles = []
    
    def is_empty(self) -> bool:
        return False
    
    def start_new_round(self) -> None:
        pass
    
    def state(self) -> str:
        return compress_tile_list(self.tiles)
    
    def take(self, idx: Tile) -> List[Tile]:
        return []
    
    def add(self, tiles: List[Tile]) -> None:
        self.tiles.extend(tiles)


class FakeBag(FactoryBagInterface):
    
    def take(self, count: int) -> List[Tile]:
        tiles: List[Tile] = [BLACK, YELLOW, BLACK, RED]
        return tiles[:count]


class TestFactory(unittest.TestCase):
    
    factory: Factory
    bag: FactoryBagInterface
    table_center: FactoryTableCenterInterface
    
    def setUp(self) -> None:
        self.bag = FakeBag()
        self.table_center = FakeTableCenter()
        self.factory = Factory(self.bag, self.table_center)
    
    def test_factory(self) -> None:        
        self.assertCountEqual(self.factory.state(), '')
        self.assertTrue(self.factory.is_empty())
        
        self.factory.start_new_round()
        self.assertCountEqual(self.factory.state(), "LLYR")
        self.assertFalse(self.factory.is_empty())
        
        self.assertCountEqual(self.factory.take(BLACK), [BLACK, BLACK])
        self.assertCountEqual(self.factory.state(), '')
        self.assertCountEqual(self.table_center.state(), 'YR')
        self.assertTrue(self.factory.is_empty())
        
    def test_factory_take_one(self) -> None:
        self.assertCountEqual(self.factory.state(), '')
        self.assertTrue(self.factory.is_empty())
        
        self.factory.start_new_round()
        self.assertCountEqual(self.factory.state(), "LLYR")
        self.assertFalse(self.factory.is_empty())
        
        self.assertCountEqual(self.factory.take(RED), [RED])
        self.assertCountEqual(self.factory.state(), '')
        self.assertCountEqual(self.table_center.state(), 'YLL')
        self.assertTrue(self.factory.is_empty())
    
    def test_factory_take_zero(self) -> None:
        self.assertCountEqual(self.factory.state(), '')
        self.assertTrue(self.factory.is_empty())
        
        self.factory.start_new_round()
        self.assertCountEqual(self.factory.state(), "LLYR")
        self.assertFalse(self.factory.is_empty())
        
        self.assertCountEqual(self.factory.take(GREEN), [])
        self.assertCountEqual(self.factory.state(), '')
        self.assertCountEqual(self.table_center.state(), 'YRLL')
        self.assertTrue(self.factory.is_empty())
