from __future__ import annotations
import unittest
from typing import List, Optional
from interfaces.wall_line_interface import WallLineAdjacentLineInterface
from azul.wall_line import WallLine
from azul.simple_types import Tile, Points, BLACK, BLUE, GREEN, RED, YELLOW


class FakeWallLine(WallLineAdjacentLineInterface):
    
    _tiles: List[Optional[Tile]]
    _line_up: Optional[WallLineAdjacentLineInterface]
    _line_down: Optional[WallLineAdjacentLineInterface]
    
    def __init__(self) -> None:
        self._tiles = [None] * 5
        self._line_up = None
        self._line_down = None
    
    def get_tile_in_column(self, column: int) -> Optional[Tile]:
        return self._tiles[column]
    
    def get_line_up(self) -> Optional[WallLineAdjacentLineInterface]:
        return self._line_up
    
    def get_line_down(self) -> Optional[WallLineAdjacentLineInterface]:
        return self._line_down
    
    def put_tiles(self, tiles: List[Optional[Tile]]) -> None:
        self._tiles = tiles
    
    def put_line_up(self, line_up: Optional[WallLineAdjacentLineInterface]) -> None:
        self._line_up = line_up
        
    def put_line_down(self, line_down: Optional[WallLineAdjacentLineInterface]) -> None:
        self._line_down = line_down


class TestWallLine(unittest.TestCase):
    
    def setUp(self) -> None:
        """Creates list of fake WallLines to simulate board state"""
        self.wall_lines: List[FakeWallLine] = [FakeWallLine() for _ in range(5)]
        
        tiles: List[List[Optional[Tile]]] = [[BLUE, None, None, BLACK, None],
                                             [GREEN, BLUE, None, RED, BLACK],
                                             [None, GREEN, BLUE, YELLOW, RED],
                                             [None, BLACK, None, BLUE, None],
                                             [None, None, None, GREEN, None]]
        wall_line: FakeWallLine
        for i, wall_line in enumerate(self.wall_lines):
            wall_line.put_line_up(None if i == 0 else self.wall_lines[i - 1])
            wall_line.put_line_down(None if i == len(self.wall_lines) - 1
                                    else self.wall_lines[i + 1])
            wall_line.put_tiles(tiles[i])
        
    def test_middle_wall_line(self) -> None:
        index: int = 2
        wall_line = WallLine([BLACK, GREEN, BLUE, YELLOW, RED])
        wall_line.put_line_up(self.wall_lines[index - 1])
        wall_line.put_line_down(self.wall_lines[index + 1])
        
        tile: Tile = BLACK
        self.assertEqual(wall_line.can_put_tile(tile), True)
        points = wall_line.put_tile(tile)
        self.assertEqual(wall_line.state(), "Lgbyr")
        self.assertEqual(str(points), "3")
        
        tile = GREEN
        self.assertEqual(wall_line.can_put_tile(tile), True)
        points = wall_line.put_tile(tile)
        self.assertEqual(wall_line.state(), "LGbyr")
        self.assertEqual(str(points), "5")
        
        tile = GREEN
        self.assertEqual(wall_line.can_put_tile(tile), False)
        self.assertCountEqual(wall_line.state(), "LGbyr")
        self.assertCountEqual(wall_line.get_tiles(), [BLACK, GREEN] + [None] * 3)
        
        tile = YELLOW
        self.assertEqual(wall_line.can_put_tile(tile), True)
        points = wall_line.put_tile(tile)
        self.assertCountEqual(wall_line.state(), "LGbYr")
        self.assertEqual(str(points), "5")

        
    def test_first_wall_line(self) -> None:
        index: int = 0
        wall_line = WallLine([BLUE, YELLOW, RED, BLACK, GREEN])
        wall_line.put_line_up(None)
        wall_line.put_line_down(self.wall_lines[index + 1])
        
        tile: Tile = BLACK
        self.assertEqual(wall_line.can_put_tile(tile), True)
        points: Points = wall_line.put_tile(tile)
        self.assertEqual(wall_line.state(), "byrLg")
        self.assertEqual(str(points), "5")
        
        tile = GREEN
        self.assertEqual(wall_line.can_put_tile(tile), True)
        points = wall_line.put_tile(tile)
        self.assertEqual(wall_line.state(), "byrLG")
        self.assertEqual(str(points), "5")
        
        tile = BLACK
        self.assertEqual(wall_line.can_put_tile(tile), False)
        self.assertCountEqual(wall_line.get_tiles(), [BLACK, GREEN] + [None] * 3)
        
    def test_last_wall_line(self) -> None:
        index: int = 4
        wall_line = WallLine([YELLOW, RED, BLACK, GREEN, BLUE])
        wall_line.put_line_up(self.wall_lines[index - 1])
        wall_line.put_line_down(None)
        
        
        tile: Tile = BLUE
        self.assertEqual(wall_line.can_put_tile(tile), True)
        points: Points = wall_line.put_tile(tile)
        self.assertEqual(wall_line.state(), "yrlgB")
        self.assertEqual(str(points), "1")
        
        tile = YELLOW
        self.assertEqual(wall_line.can_put_tile(tile), True)
        points = wall_line.put_tile(tile)
        self.assertEqual(wall_line.state(), "YrlgB")
        self.assertEqual(str(points), "1")

        tile = GREEN
        self.assertEqual(wall_line.can_put_tile(tile), True)
        points = wall_line.put_tile(tile)
        self.assertEqual(wall_line.state(), "YrlGB")
        self.assertEqual(str(points), "7")

        tile = RED
        self.assertEqual(wall_line.can_put_tile(tile), True)
        points = wall_line.put_tile(tile)
        tile = BLACK
        self.assertEqual(wall_line.can_put_tile(tile), True)
        points = wall_line.put_tile(tile)
        self.assertCountEqual(wall_line.state(), "BGLRY")
