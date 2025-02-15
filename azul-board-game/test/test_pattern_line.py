from __future__ import annotations
import unittest
from typing import List
from interfaces.pattern_line_interfaces import PatternWallLineInterface
from interfaces.used_tiles_interfaces import UsedTilesGiveInterface
from azul.simple_types import Tile, Points, STARTING_PLAYER, RED, BLACK
from azul.pattern_line import PatternLine
from azul.floor import Floor


class FakeUsedTiles(UsedTilesGiveInterface):
    def give(self, tiles: List[Tile]) -> None:
        pass


class FakeWallLine(PatternWallLineInterface):
    tiles: List[Tile]
    
    def __init__(self) -> None:
        self.tiles = []
    
    def can_put_tile(self, tile: Tile) -> bool:
        return tile not in self.tiles
    
    def put_tile(self, tile: Tile) -> Points:
        self.tiles.append(tile)
        return Points(5)


class TestPatternLineWithFloor(unittest.TestCase):
    
    pattern_line: PatternLine
    floor: Floor
    used_tiles: UsedTilesGiveInterface
    wall_line: PatternWallLineInterface
    
    def setUp(self) -> None:
        self.used_tiles = FakeUsedTiles()
        self.wall_line = FakeWallLine()
        
        self.floor = Floor([Points(1), Points(2), Points(3)], self.used_tiles)
    
    def test_filled_pattern_line(self) -> None:
        self.pattern_line = PatternLine(3, self.floor, self.wall_line, self.used_tiles)

        self.assertEqual(self.pattern_line.state(), '_' * 3)
        
        self.pattern_line.put([RED, RED, STARTING_PLAYER])
        self.assertEqual(self.pattern_line.state(), '_RR')
        self.assertCountEqual(self.floor.state(), 'S')
        
        self.pattern_line.put([BLACK, BLACK])
        self.assertEqual(self.pattern_line.state(), '_RR')
        self.assertCountEqual(self.floor.state(), 'SLL')  

        self.pattern_line.put([RED, RED])
        self.assertEqual(self.pattern_line.state(), 'RRR')
        self.assertCountEqual(self.floor.state(), 'SLLR')
        
        points_pattern_line: Points = self.pattern_line.finish_round()
        points_floor: Points = self.floor.finish_round()
        self.assertEqual(points_pattern_line, Points(5))
        self.assertEqual(points_floor, Points(9))
        self.assertEqual(self.pattern_line.state(), '_' * 3)
        self.assertEqual(self.floor.state(), '')
    
    def test_unfilled_pattern_line(self) -> None:
        self.pattern_line = PatternLine(4, self.floor, self.wall_line, self.used_tiles)
        
        self.assertEqual(self.pattern_line.state(), '_' * 4)
        
        self.pattern_line.put([BLACK, STARTING_PLAYER, BLACK])
        self.assertEqual(self.pattern_line.state(), '__LL')
        self.assertCountEqual(self.floor.state(), 'S')
        
        self.pattern_line.put([RED])
        self.assertEqual(self.pattern_line.state(), '__LL')
        self.assertCountEqual(self.floor.state(), 'SR')  
        
        points_pattern_line: Points = self.pattern_line.finish_round()
        points_floor: Points = self.floor.finish_round()
        self.assertEqual(points_pattern_line, Points(0))
        self.assertEqual(points_floor, Points(3))
        self.assertEqual(self.pattern_line.state(), '__LL')
        self.assertEqual(self.floor.state(), '')

    def test_put_no_tiles(self) -> None:
        self.pattern_line = PatternLine(2, self.floor, self.wall_line, self.used_tiles)
        
        self.assertEqual(self.pattern_line.state(), '_' * 2)
        
        self.pattern_line.put([])
        self.assertEqual(self.pattern_line.state(), '_' * 2)
        self.assertCountEqual(self.floor.state(), '')
        
        self.pattern_line.put([STARTING_PLAYER])
        self.assertEqual(self.pattern_line.state(), '_' * 2)
        self.assertCountEqual(self.floor.state(), 'S')
        
        self.pattern_line.finish_round()
        self.assertEqual(self.pattern_line.state(), '_' * 2)
    
    def test_put_tile_which_is_on_wall_line(self) -> None:
        self.pattern_line = PatternLine(2, self.floor, self.wall_line, self.used_tiles)
        
        self.pattern_line.put([RED, RED])
        self.assertCountEqual(self.pattern_line.state(), 'RR')
        points: Points = self.pattern_line.finish_round()
        self.assertEqual(points, Points(5))
        self.assertCountEqual(self.pattern_line.state(), '_' * 2)
        
        self.pattern_line.put([RED])
        self.assertCountEqual(self.pattern_line.state(), '_' * 2)
        self.assertCountEqual(self.floor.state(), 'R')
        
        self.pattern_line.put([BLACK])
        self.assertCountEqual(self.pattern_line.state(), '_L')
        self.assertCountEqual(self.floor.state(), 'R')
