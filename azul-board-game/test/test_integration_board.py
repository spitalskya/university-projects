from __future__ import annotations
import unittest
from typing import List
from azul.board import Board
from azul.floor import Floor
from azul.pattern_line import PatternLine
from azul.wall_line import WallLine
from azul.simple_types import (FinishRoundResult, Points, Tile, NORMAL, GAME_FINISHED,
                               BLACK, BLUE, GREEN, RED, YELLOW, STARTING_PLAYER)
from interfaces.used_tiles_interfaces import UsedTilesGiveInterface
from interfaces.round_results_interfaces import (FinalPointsCalculationInterface,
                                                 GameFinishedInterface)


class FakeGameFinished(GameFinishedInterface):
    def game_finished(self, wall: List[List[Tile | None]]) -> FinishRoundResult:
        for line in wall:
            if None not in line:
                return GAME_FINISHED
        return NORMAL

class FakeFinalPointsCalculation(FinalPointsCalculationInterface):
    def get_points(self, wall: List[List[Tile | None]]) -> Points:    
        return Points(50)

class FakeUsedTiles(UsedTilesGiveInterface):
    def give(self, tiles: List[Tile]) -> None:
        pass


class IntegrationTestBoard(unittest.TestCase):
    
    board: Board
    pattern_lines: List[PatternLine]
    wall_lines: List[WallLine]
    floor: Floor
    
    def setUp(self) -> None:
        self.board = Board(FakeGameFinished(), FakeFinalPointsCalculation(), FakeUsedTiles())
        self.pattern_lines = self.board.get_pattern_lines()
        self.wall_lines = self.board.get_wall_lines()
        self.floor = self.board.get_floor()
            
    def test_proper_construction(self) -> None:
        self.assertEqual(len(self.pattern_lines), 5)
        self.assertEqual(len(self.wall_lines), 5)
        self.assertEqual(self.board.points, Points(0))
        
        pattern_line: PatternLine
        for i, pattern_line in enumerate(self.pattern_lines):
            self.assertEqual(pattern_line.get_wall_line(), self.wall_lines[i])
            self.assertEqual(pattern_line.get_floor(), self.floor)
            
            self.assertEqual(pattern_line.get_capacity(), i + 1)
            self.assertCountEqual(pattern_line.get_tiles(), [])
            self.assertCountEqual(pattern_line.state(), '_' * (i + 1))
            self.assertIsNone(pattern_line.get_current_type())
        
        tiles: List[Tile] = [BLACK, BLUE, GREEN, RED, YELLOW]
        wall_line: WallLine
        for i, wall_line in enumerate(self.wall_lines):
            if i == 0:
                self.assertIsNone(wall_line.get_line_up())
            else:
                self.assertIsInstance(wall_line.get_line_up(), WallLine)
            
            if i == 4:
                self.assertIsNone(wall_line.get_line_down())
            else:
                self.assertIsInstance(wall_line.get_line_down(), WallLine)
            
            self.assertCountEqual(wall_line.get_tiles(), [None] * 5)
            self.assertCountEqual(wall_line.state(), 'bglry')
            self.assertTrue(all(wall_line.can_put_tile(tile) for tile in tiles))
    
        self.assertCountEqual(self.floor.state(), '')
    
    def test_board_put(self) -> None:
        destination_idx: int = 2
        pattern_line: PatternLine = self.pattern_lines[destination_idx]
        tiles_to_put: List[Tile] = [RED, RED]
        
        self.assertCountEqual(pattern_line.get_tiles(), [])
        self.board.put(destination_idx, tiles_to_put)
        self.assertCountEqual(pattern_line.get_tiles(), [RED, RED])
        
        tiles_to_put = [BLACK]
        self.board.put(destination_idx, tiles_to_put)
        self.assertCountEqual(pattern_line.get_tiles(), [RED, RED])
        self.assertCountEqual(self.floor.get_tiles(), [BLACK])
        
        tiles_to_put = [RED, STARTING_PLAYER, RED]
        self.board.put(destination_idx, tiles_to_put)
        self.assertCountEqual(pattern_line.get_tiles(), [RED, RED, RED])
        self.assertCountEqual(self.floor.get_tiles(), [STARTING_PLAYER, BLACK, RED])
    
    def test_put_with_occupied_wall_line(self) -> None:
        destination_idx: int = 1
        pattern_line: PatternLine = self.pattern_lines[destination_idx]
        self.wall_lines[destination_idx].put_tile(BLACK)
        
        tiles_to_put: List[Tile] = [BLACK]
        pattern_line.put(tiles_to_put)
        self.assertCountEqual(pattern_line.get_tiles(), [])
        self.assertCountEqual(self.floor.get_tiles(), [BLACK])
        
        tiles_to_put = [RED]
        pattern_line.put(tiles_to_put)
        self.assertCountEqual(pattern_line.get_tiles(), [RED])
    
    def test_game_session(self) -> None:
        pattern_line: PatternLine
        for pattern_line in self.pattern_lines:
            self.assertEqual(pattern_line.finish_round(), Points(0))
        
        self.assertEqual(self.board.points, Points(0))
        
        self.board.put(0, [RED])
        self.board.put(1, [YELLOW] * 2)
        self.board.put(2, [BLUE] * 3 + [STARTING_PLAYER])
        self.board.put(3, [BLUE] * 2)
        self.board.put(4, [BLACK] * 6)
        
        self.assertEqual(self.board.finish_round(), NORMAL)
        self.assertEqual(self.board.points, Points(7 - 2))
        
        self.board.put(0, [RED])        # should fall on floor
        self.board.put(2, [YELLOW] * 3)
        self.board.put(3, [BLUE] * 2)
        
        self.assertEqual(self.board.finish_round(), NORMAL)
        self.assertEqual(self.board.points, Points(5 + 4 - 1))
        
        for tile in [BLUE, YELLOW, BLACK]:
            self.board.put(0, [tile])
            self.assertEqual(self.board.finish_round(), NORMAL)
        
        self.board.put(0, [GREEN])
        self.board.put(3, [GREEN] * 4)
        self.assertEqual(self.board.finish_round(), GAME_FINISHED)
        self.assertEqual(self.board.points, Points(8 + 20))
        
        self.board.end_game()
        self.assertEqual(self.board.points, Points(28 + 50))
