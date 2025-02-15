from __future__ import annotations
import unittest
from typing import List
from azul.used_tiles import UsedTiles
from azul.simple_types import Tile, STARTING_PLAYER, RED, BLUE, YELLOW, GREEN, BLACK 


class TestUsedTiles(unittest.TestCase):

    def setUp(self) -> None:
        self.used_tiles: UsedTiles = UsedTiles()
    
    def test_give(self) -> None:
        tiles_to_give: List[Tile] = [RED]
        self.used_tiles.give(tiles_to_give)
        self.assertEqual(self.used_tiles.get_tiles(), [RED])
        tiles_to_give = [BLUE]
        self.used_tiles.give(tiles_to_give)
        self.assertCountEqual(self.used_tiles.get_tiles(), [RED, BLUE])
        tiles_to_give = [STARTING_PLAYER, BLACK, RED]
        self.used_tiles.give(tiles_to_give)
        self.assertEqual(self.used_tiles.get_tiles(), [RED, BLUE, BLACK, RED])
    
    def test_take_all(self) -> None:
        tiles_to_give: List[Tile] = [YELLOW, GREEN, BLACK, STARTING_PLAYER]
        self.assertCountEqual(self.used_tiles.get_tiles(), [])
        self.used_tiles.give(tiles_to_give)
        tiles_to_take: List[Tile] = self.used_tiles.take_all()
        self.assertCountEqual(tiles_to_take, [YELLOW, GREEN, BLACK])
        self.assertCountEqual(self.used_tiles.get_tiles(), [])
