from __future__ import annotations
import unittest
from typing import List, Optional
from azul.game_finished import GameFinished
from azul.simple_types import NORMAL, GAME_FINISHED, Tile, BLACK, BLUE, GREEN, RED, YELLOW


class TestGameFinished(unittest.TestCase):
    def setUp(self) -> None:
        self.game_finished: GameFinished = GameFinished()
    
    def test_should_continue(self) -> None:
        wall: List[List[Optional[Tile]]] = [[BLUE, None, None, BLACK, GREEN],
                                            [None, None, None, None, None],
                                            [BLACK, GREEN, BLUE, YELLOW, None],
                                            [RED, BLACK, None, BLUE, YELLOW],
                                            [None, RED, None, GREEN, None]]
        self.assertEqual(self.game_finished.game_finished(wall), NORMAL)
    
    def test_should_continue2(self) -> None:
        wall: List[List[Optional[Tile]]] = [[None] * 5] * 5
        self.assertEqual(self.game_finished.game_finished(wall), NORMAL)
    
    def test_should_finish(self) -> None:
        wall: List[List[Optional[Tile]]] = [[None, YELLOW, RED, BLACK, GREEN],
                                            [None, None, None, None, None],
                                            [BLACK, GREEN, BLUE, YELLOW, None],
                                            [RED, BLACK, GREEN, BLUE, YELLOW],
                                            [YELLOW, None, None, None, BLUE]]
        self.assertEqual(self.game_finished.game_finished(wall), GAME_FINISHED)

    def test_should_finish2(self) -> None:
        wall: List[List[Optional[Tile]]] = [[BLUE, YELLOW, RED, BLACK, GREEN],
                                            [GREEN, BLUE, YELLOW, RED, BLACK],
                                            [BLACK, GREEN, BLUE, YELLOW, RED],
                                            [RED, BLACK, GREEN, BLUE, YELLOW],
                                            [YELLOW, RED, BLACK, GREEN, BLUE]]
        self.assertEqual(self.game_finished.game_finished(wall), GAME_FINISHED)
