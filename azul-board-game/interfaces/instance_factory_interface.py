from __future__ import annotations
from abc import ABC, abstractmethod
from interfaces.game_elements_interfaces import (BoardInterface, TableAreaInterface,
                                                 GameObserverInterface)
from interfaces.combined_interfaces import UsedTilesInterface, BagInterface
from interfaces.round_results_interfaces import (FinalPointsCalculationInterface,
                                                 GameFinishedInterface)
from interfaces.used_tiles_interfaces import UsedTilesTakeAllInterface

class InstanceFactoryInterface(ABC):
    
    @abstractmethod
    def get_board(self, game_finished: GameFinishedInterface, 
                  final_points: FinalPointsCalculationInterface,
                  used_tiles: UsedTilesInterface) -> BoardInterface:
        pass
    
    @abstractmethod
    def get_table_area(self, number_of_factories:int, 
                       bag: BagInterface) -> TableAreaInterface:
        pass
    
    
    @abstractmethod
    def get_bag(self, used_tiles: UsedTilesTakeAllInterface) -> BagInterface:
        pass
    
    @abstractmethod
    def get_game_observer(self) -> GameObserverInterface:
        pass
    
    @abstractmethod
    def get_final_points_calculation(self) -> FinalPointsCalculationInterface:
        pass
    
    @abstractmethod
    def get_game_finished(self) -> GameFinishedInterface:
        pass
    
    @abstractmethod
    def get_used_tiles(self) -> UsedTilesInterface:
        pass
