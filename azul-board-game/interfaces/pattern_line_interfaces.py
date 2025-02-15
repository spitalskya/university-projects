from __future__ import annotations
from typing import List
from abc import ABC, abstractmethod
from azul.simple_types import Tile, Points


class PatternLineFloorInterface(ABC):
    
    @abstractmethod
    def put(self, tiles: List[Tile]) -> None:
        pass

class PatternWallLineInterface(ABC):
    
    @abstractmethod
    def can_put_tile(self, tile: Tile) -> bool:
        pass
    
    @abstractmethod
    def put_tile(self, tile: Tile) -> Points:
        pass
