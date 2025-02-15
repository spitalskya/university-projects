from __future__ import annotations
import unittest
from typing import List, Optional
from azul.simple_types import Tile, RED, BLUE, YELLOW, GREEN, BLACK
from azul.final_points_calculation import FinalPointsCalculation, WallPointsCalculation, \
    HorizontalRowPointsCalculation, VerticalColumnPointsCalculation, ColorPointsCalculation


class TestFinalPointsCalculation(unittest.TestCase):

    def setUp(self) -> None:
        self.horizontal = HorizontalRowPointsCalculation()
        self.vertical = VerticalColumnPointsCalculation()
        self.color = ColorPointsCalculation()

        wall_points_calculation = WallPointsCalculation()
        wall_points_calculation.add_component(self.horizontal, self.vertical, self.color)
        
        self.final_points_calculation = FinalPointsCalculation()
        self.final_points_calculation.add_component(wall_points_calculation)

    def test_get_points(self) -> None:
        test_wall: List[List[Optional[Tile]]] = [
            [None,  YELLOW, RED,    None,   None],
            [None,  BLUE,   YELLOW, RED,    None],
            [None,  GREEN,  BLUE,   None,   RED],
            [RED,   BLACK,  GREEN,  BLUE,   YELLOW],
            [None,  RED,    BLACK,  GREEN,  None]
        ]

        horizontal_row_points = self.horizontal.get_points(test_wall)
        self.assertEqual(horizontal_row_points.value, 2)

        vertical_column_points = self.vertical.get_points(test_wall)
        self.assertEqual(vertical_column_points.value, 14)

        color_points = self.color.get_points(test_wall)
        self.assertEqual(color_points.value, 10)

        points = self.final_points_calculation.get_points(test_wall)
        self.assertEqual(points.value, 26)
    
    def test_get_points2(self) -> None:
        test_wall: List[List[Optional[Tile]]] = [
            [BLUE,  YELLOW, RED,    BLACK,   GREEN],
            [GREEN,  BLUE,   YELLOW, RED,    BLACK],
            [BLACK,  GREEN,  BLUE,   YELLOW,   RED],
            [RED,   None,  None,  BLUE,   None],
            [YELLOW,  None,    None,  None,  None]
        ]

        points = self.final_points_calculation.get_points(test_wall)
        self.assertEqual(points.value, 13)
    
    def test_get_points3(self) -> None:
        test_wall: List[List[Optional[Tile]]] = [
            [BLUE,  YELLOW, RED, BLACK,   GREEN],
            [GREEN,  BLUE,   YELLOW, RED,    BLACK],
            [BLACK,  GREEN,  None,   YELLOW,   RED],
            [None,   BLACK,  GREEN,  None,   None],
            [None,  None,    None,  None,  None]
        ]

        points = self.final_points_calculation.get_points(test_wall)
        self.assertEqual(points.value, 4)
