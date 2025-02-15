from __future__ import annotations
from typing import List, Optional
from abc import ABC, abstractmethod
from azul.simple_types import Tile, Points, FinishRoundResult

class FinalPointsCalculationInterface(ABC):
    
    @abstractmethod
    def get_points(self, wall: List[List[Optional[Tile]]]) -> Points:
        pass

class GameFinishedInterface(ABC):
    @abstractmethod
    def game_finished(self, wall: List[List[Optional[Tile]]]) -> FinishRoundResult:
        pass
