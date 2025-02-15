from __future__ import annotations
from typing import Dict, List, Tuple
import unittest
from test.fake_instance_factory import FakeInstanceFactory
from azul.game import Game
from azul.simple_types import Points

def dummy_display(_: str) -> None:
    pass

class TestGame(unittest.TestCase):
    
    game: Game
    
    def setUp(self) -> None:
        self.game = Game(FakeInstanceFactory())
        self.game.register_callback(dummy_display)
        
    def test_start_calls(self) -> None:
        self.assertFalse(self.game.start(0))
        self.assertFalse(self.game.start(1, 1))
        self.assertFalse(self.game.start(2, 1))
        self.assertFalse(self.game.start(2, 1, 1))
        self.assertFalse(self.game.start(3, 1, 2, 3, 4))
        self.assertFalse(self.game.start(3, 1, 2, 2))
        self.assertFalse(self.game.start(4))
        self.assertFalse(self.game.start(5, 1, 2, 3, 4, 5))
        self.assertTrue(self.game.start(3, 1, 2, 3))
        
    def test_take_calls(self) -> None:
        self.game.start(3, 10, 11, 12)
        
        self.assertFalse(self.game.take(0, 0, 0, 0))
        self.assertFalse(self.game.take(10, -1, 0, 0))
        self.assertFalse(self.game.take(10, 0, -1, 0))
        self.assertFalse(self.game.take(10, 0, 0, -1))
        self.assertFalse(self.game.take(10, 8, 0, 0))
        self.assertFalse(self.game.take(10, 0, 5, 0))
        self.assertFalse(self.game.take(10, 0, 0, 5))
        self.assertTrue(self.game.take(10, 0, 1, 0))
        self.assertTrue(self.game.take(11, 7, 4, 4))
        self.assertTrue(self.game.take(12, 1, 1, 1))
        self.assertTrue(self.game.take(10, 2, 2, 3))
    
    def test_number_of_factories(self) -> None:
        self.game.start(2, 10, 11)
        self.assertEqual(self.game.get_number_of_factories(), 5)
        self.setUp()
        self.game.start(3, 10, 11, 12)
        self.assertEqual(self.game.get_number_of_factories(), 7)
        self.setUp()
        self.game.start(4, 10, 11, 12, 13)
        self.assertEqual(self.game.get_number_of_factories(), 9)
        
    def test_evaluating_scores(self) -> None:
        
        player_points: Dict[int, Points] = {10: Points(1),
                                            11: Points(2),
                                            12: Points(3)}
        scoreboard: List[Tuple[int, Points]] = self.game.evaluate_scores(player_points)
        self.assertEqual(scoreboard, [(12, Points(3)), (11, Points(2)), (10, Points(1))])
        
        player_points = {10: Points(-1),
                         11: Points(2),
                         12: Points(2)}
        scoreboard = self.game.evaluate_scores(player_points)
        self.assertEqual(scoreboard, [(11, Points(2)), (12, Points(2)), (10, Points(-1))])
        
        player_points = {10: Points(2),
                         11: Points(2),
                         12: Points(2)}
        scoreboard = self.game.evaluate_scores(player_points)
        self.assertEqual(scoreboard, [(10, Points(2)), (11, Points(2)), (12, Points(2))])
        
        player_points = {10: Points(-3),
                         11: Points(-1),
                         12: Points(-2)}
        scoreboard = self.game.evaluate_scores(player_points)
        self.assertEqual(scoreboard, [(11, Points(-1)), (12, Points(-2)), (10, Points(-3))])
    
    def test_start_new_round_and_end_game_call(self) -> None:
        # fake board counts taken tiles as points
        # tile sources: [[STARTING_PLAYER, RED, GREEN], [BLACK, BLACK, GREEN]]
        self.game.start(3, 10, 11, 12)
        self.game.take(10, 0, 3, 0)     # took 1 Red, 1 Starting player tile
        self.game.take(11, 1, 0, 0)     # took 2 Black tiles
        self.game.take(12, 1, 2, 0)     # took 1 Green tile
        self.game.take(10, 0, 2, 1)     # took 1 Green tile
        
        # all tiles were taken, tile sources should be refilled with
        # [[STARTING_PLAYER, RED, GREEN], [BLACK, BLACK, GREEN]]
        self.assertTrue(self.game.take(10, 1, 0, 2))    # took 2 Black tiles
        self.assertTrue(self.game.take(11, 1, 2, 2))    # took 1 Green tile
        self.assertTrue(self.game.take(12, 0, 3, 2))    # took 1 Red, 1 Starting player tile
        self.assertTrue(self.game.take(10, 0, 2, 3))    # took 1 Green tile

        self.game.end_game()            # to check if end_game on boards were called
        self.assertEqual(self.game.get_board(10).points, Points(5))
        self.assertEqual(self.game.get_board(11).points, Points(3))
        self.assertEqual(self.game.get_board(12).points, Points(2))
    
    def test_small_game_with_starting_player_change(self) -> None:
        self.assertTrue(self.game.start(2, 10, 11))
        self.assertFalse(self.game.start(2, 10, 11))
        
        self.assertTrue(self.game.take(10, 1, 0, 2))
        state: str = "[]\n[]\n['L', 'L']\n[]\n[]"
        self.assertEqual(self.game.get_board(10).state(), state)
        self.assertFalse(self.game.take(10, 0, 3, 1))
        
        self.assertTrue(self.game.take(11, 0, 3, 0))
        state = "['R']\n[]\n[]\n[]\n[]"
        self.assertEqual(self.game.get_board(11).state(), state)
        
        self.assertTrue(self.game.take(10, 0, 2, 0))
        state = "['G']\n[]\n['L', 'L']\n[]\n[]"
        self.assertEqual(self.game.get_board(10).state(), state)
        
        self.assertTrue(self.game.take(11, 1, 2, 3))
        state = "['R']\n[]\n[]\n['G']\n[]"
        self.assertEqual(self.game.get_board(11).state(), state)
        
        # Round ended, starting player should be changed
        self.assertFalse(self.game.take(10, 0, 2, 0))
        self.assertTrue(self.game.take(11, 0, 2, 0))
    
    def test_if_game_ends(self) -> None:
        self.game.start(4, 10, 11, 12, 13)
        player_points = {10: Points(1),
                         11: Points(2),
                         12: Points(3),
                         13: Points(4)}
        scoreboard = self.game.evaluate_scores(player_points)
        self.game.determine_winner(scoreboard)
        
        # game should be ended, valid take call should result in False
        self.assertFalse(self.game.take(10, 0, 0, 0))
