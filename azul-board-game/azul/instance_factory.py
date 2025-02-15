from __future__ import annotations
from typing import List
from interfaces.game_elements_interfaces import (BoardInterface, TableAreaInterface,
                                                 GameObserverInterface)
from interfaces.instance_factory_interface import InstanceFactoryInterface
from interfaces.used_tiles_interfaces import UsedTilesTakeAllInterface
from interfaces.combined_interfaces import BagInterface, UsedTilesInterface
from interfaces.round_results_interfaces import (FinalPointsCalculationInterface, 
                                                 GameFinishedInterface)
from azul.board import Board
from azul.table_area import TableArea
from azul.game_observer import GameObserver
from azul.used_tiles import UsedTiles
from azul.game_finished import GameFinished
from azul.bag import Bag
from azul.random_permutation_generator import RandomPermutationGenerator
from azul.final_points_calculation import (FinalPointsCalculation, WallPointsCalculation,
                                           HorizontalRowPointsCalculation, 
                                           VerticalColumnPointsCalculation, ColorPointsCalculation)
from azul.simple_types import Tile, BLACK, BLUE, GREEN, RED, YELLOW


class InstanceFactory(InstanceFactoryInterface):
    """Structure to construct instances for Game class"""
    
    def get_board(self, game_finished: GameFinishedInterface, 
                  final_points: FinalPointsCalculationInterface,
                  used_tiles: UsedTilesInterface) -> BoardInterface:
        return Board(game_finished, final_points, used_tiles)
    
    def get_table_area(self, number_of_factories: int, 
                       bag: BagInterface) -> TableAreaInterface:
        return TableArea(number_of_factories, bag)

    def get_bag(self, used_tiles: UsedTilesTakeAllInterface) -> BagInterface:
        """Creates Bag with 20 tiles of each type
        
        needs reference on UsedTiles and creates RandomPermutationGenerator
        """
        tiles: List[Tile] =  [BLACK, BLUE, GREEN, RED, YELLOW] * 20
        return Bag(tiles, used_tiles, RandomPermutationGenerator())
    
    def get_game_observer(self) -> GameObserverInterface:
        return GameObserver()
    
    def get_final_points_calculation(self) -> FinalPointsCalculationInterface:
        horizontal = HorizontalRowPointsCalculation()
        vertical = VerticalColumnPointsCalculation()
        color = ColorPointsCalculation()

        wall_points_calculation = WallPointsCalculation()
        wall_points_calculation.add_component(horizontal, vertical, color)
        
        final_points_calculation = FinalPointsCalculation()
        final_points_calculation.add_component(wall_points_calculation)
        
        return final_points_calculation
    
    def get_game_finished(self) -> GameFinishedInterface:
        return GameFinished()
    
    def get_used_tiles(self) -> UsedTilesInterface:
        return UsedTiles()
