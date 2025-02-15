from __future__ import annotations
import unittest
from typing import List
from azul.simple_types import Tile, RED, GREEN, YELLOW, BLACK, STARTING_PLAYER
from azul.table_area import TableArea
from azul.factory import Factory
from azul.table_center import TableCenter
from interfaces.factory_interfaces import FactoryBagInterface
from interfaces.tile_source import TileSource


class FakeBag(FactoryBagInterface):
    def take(self, count: int) -> List[Tile]:
        return [RED, RED, YELLOW, BLACK]


class IntegrationTestTableArea(unittest.TestCase):
    
    table_area: TableArea
    tile_sources: List[TileSource]
    bag: FactoryBagInterface
    
    def setUp(self) -> None:
        self.bag = FakeBag()
        self.table_area = TableArea(5, self.bag)
        self.tile_sources = self.table_area.get_tile_sources()
    
    def test_proper_construction(self) -> None:
        self.assertEqual(len(self.tile_sources), 6)
        tile_source: TileSource
        for tile_source in self.tile_sources:
            self.assertIsInstance(tile_source, TileSource) 
        self.assertIsInstance(self.tile_sources[0], TableCenter) 
        for tile_source in self.tile_sources[1:]:
            self.assertIsInstance(tile_source, Factory) 
            
    def test_start_new_round(self) -> None:
        tile_source: TileSource
        for tile_source in self.tile_sources:
            self.assertTrue(tile_source.is_empty())
        
        self.table_area.start_new_round()
        for tile_source in self.tile_sources:
            self.assertFalse(tile_source.is_empty())
        
        self.assertCountEqual(self.tile_sources[0].state(), 'S')
        for tile_source in self.tile_sources[1:]:
            self.assertCountEqual(tile_source.state(), 'RRLY')
    
    def test_round_end(self) -> None:
        self.assertTrue(self.table_area.is_round_end())
        self.table_area.start_new_round()
        self.assertFalse(self.table_area.is_round_end())
    
    def test_whole_round(self) -> None:
        self.table_area.start_new_round()
        
        self.assertCountEqual(self.tile_sources[0].state(), 'S')
        
        tiles_to_take: List[Tile] = [RED, RED, GREEN, BLACK, YELLOW]
        tile_source: TileSource
        for i, tile_source in enumerate(self.tile_sources[1:]):
            self.assertFalse(tile_source.is_empty())
            
            tiles_taken: List[Tile] = tile_source.take(tiles_to_take[i])
            self.assertTrue(all(tile == tiles_to_take[i] for tile in tiles_taken))
            self.assertCountEqual(tile_source.state(), '')
            
            self.assertTrue(tile_source.is_empty())
        
        self.assertCountEqual(self.tile_sources[0].state(), 'S' + 'R' * 6 
                              + 'G' * 0 + 'L' * 4 + 'Y' * 4)

        self.assertCountEqual(self.tile_sources[0].take(RED), [RED] * 6 + [STARTING_PLAYER])
        tile_to_take: Tile
        for tile_to_take in [GREEN, BLACK, YELLOW]:
            tiles_taken = self.tile_sources[0].take(tile_to_take)
            self.assertTrue(all(tile == tile_to_take for tile in tiles_taken))
        self.assertTrue(self.tile_sources[0].is_empty())
        self.assertCountEqual(self.tile_sources[0].state(), '')
        
        self.assertTrue(self.table_area.is_round_end())
        
        # new round
        self.assertTrue(all(tile_source.is_empty() for tile_source in self.tile_sources))
        self.table_area.start_new_round()
        self.assertFalse(any(tile_source.is_empty() for tile_source in self.tile_sources))
        self.assertCountEqual(self.tile_sources[0].state(), 'S')
        for tile_source in self.tile_sources[1:]:
            self.assertCountEqual(tile_source.state(), 'RRLY')         
