from __future__ import annotations
import unittest
from test.deterministic_instance_factory import DeterministicInstanceFactory
from azul.game import Game
from azul.simple_types import Points


class IntegrationTestGame(unittest.TestCase):
    
    game: Game
    
    def setUp(self) -> None:
        self.game = Game(DeterministicInstanceFactory())
    
    def test_game_session(self) -> None:    # pylint: disable=too-many-statements
        self.assertTrue(self.game.start(2, 10, 11))

        # first round
        self.assertTrue(self.game.take(10, 1, 0, 1))    # filled second PL
        self.assertTrue(self.game.take(11, 2, 2, 1))    # filled second PL
        self.assertTrue(self.game.take(10, 3, 4, 3))
        self.assertTrue(self.game.take(11, 4, 1, 3))
        self.assertTrue(self.game.take(10, 5, 4, 3))    # filled fourth PL
        self.assertTrue(self.game.take(11, 0, 3, 4))    # 11 is starting player - 1 tile falls
        self.assertTrue(self.game.take(10, 0, 1, 0))    # 1 tile falls, filled first PL
        self.assertTrue(self.game.take(11, 0, 0, 0))    # 1 tile falls, filled first PL
        self.assertTrue(self.game.take(10, 0, 0, 2))    # no tiles take
        self.assertTrue(self.game.take(11, 0, 2, 2))
        # round ended
        
        self.assertEqual(self.game.get_board(10).points, Points(3 - 1))
        self.assertEqual(self.game.get_board(11).points, Points(2 - 2))
        
        # second round
        self.assertTrue(self.game.take(11, 1, 1, 3))    # filled fourth PL
        self.assertTrue(self.game.take(10, 0, 0, 1))    # can't put black tiles there
                                                        # 10 is starting player, 3 tiles fall
        self.assertTrue(self.game.take(11, 2, 3, 4))    # filled fifth PL, 1 tile falls
        self.assertTrue(self.game.take(10, 3, 0, 0))    # filled first PL, 1 tile falls
        self.assertTrue(self.game.take(11, 4, 2, 2))    # filled third PL, 1 tile falls
        self.assertTrue(self.game.take(10, 5, 3, 1))    # filled second PL
        self.assertTrue(self.game.take(11, 0, 1, 1))    # filled second PL
        self.assertTrue(self.game.take(10, 0, 4, 4))
        self.assertTrue(self.game.take(11, 0, 2, 0))    # filled first PL, 1 tile falls    
        # round ended
         
        self.assertEqual(self.game.get_board(10).points, Points(2 + 5 - 6))
        self.assertEqual(self.game.get_board(11).points, Points(0 + 8 - 4))
        
        # third round
        self.assertTrue(self.game.take(10, 1, 0, 2))
        self.assertTrue(self.game.take(11, 2, 2, 3))
        self.assertTrue(self.game.take(10, 3, 0, 2))    # filled third PL, 1 tile falls
        self.assertTrue(self.game.take(11, 4, 2, 3))    # filled fourth PL
        self.assertTrue(self.game.take(10, 0, 4, 4))    # filled fifth PL, 2 tiles fall
                                                        # 10 is starting player
        self.assertTrue(self.game.take(11, 5, 3, 0))    # filled first PL, 1 tile falls
        self.assertTrue(self.game.take(10, 0, 1, 3))    # filled fourth PL
        self.assertTrue(self.game.take(11, 0, 4, 1))    # filled second PL
        self.assertTrue(self.game.take(10, 0, 3, 0))    # filled first PL, 1 tile falls
        # round ended
        
        self.assertEqual(self.game.get_board(10).points, Points(1 + 6 - 6))
        self.assertEqual(self.game.get_board(11).points, Points(4 + 10 - 1))
        
        # fourth round
        self.assertTrue(self.game.take(10, 3, 4, 2))
        self.assertTrue(self.game.take(11, 2, 2, 4))
        self.assertTrue(self.game.take(10, 5, 4, 2))    # filled third PL, 1 tile falls
        self.assertTrue(self.game.take(11, 4, 2, 4))
        self.assertTrue(self.game.take(10, 0, 3, 3))    # filled fourth PL, 1 tile falls
                                                        # 10 is starting player
        self.assertTrue(self.game.take(11, 0, 1, 0))    # filled first PL, 1 tile falls
        self.assertTrue(self.game.take(10, 1, 1, 1))    # filled second PL
        self.assertTrue(self.game.take(11, 0, 0, 3))    # filled fourth PL
        # round ended
        
        self.assertEqual(self.game.get_board(10).points, Points(1 + 8 - 2))
        self.assertEqual(self.game.get_board(11).points, Points(13 + 9 - 1))

        # fifth round
        self.assertTrue(self.game.take(10, 3, 4, 0))    # filled first PL, 1 tile falls
        self.assertTrue(self.game.take(11, 2, 2, 4))    # filled fifth PL, 1 tile falls
        self.assertTrue(self.game.take(10, 4, 2, 1))    # filled second PL
        self.assertTrue(self.game.take(11, 5, 4, 0))    # filled first PL, 1 tile falls
        self.assertTrue(self.game.take(10, 0, 3, 2))    # filled third PL, 2 tiles fall
                                                        # 10 is starting player
        self.assertTrue(self.game.take(11, 1, 1, 2))
        self.assertTrue(self.game.take(10, 0, 0, 3))    # filled fourth PL
        self.assertTrue(self.game.take(11, 0, 1, 2))    # filled third PL, 1 tile falls
        # round and game ended
        
        self.assertEqual(self.game.get_board(10).points, Points(7 + 20 - 4 + 7))
        self.assertEqual(self.game.get_board(11).points, Points(21 + 18 - 4 + 19))

        # takes are not possible after game has ended
        self.assertFalse(self.game.take(10, 1, 0, 0))
