from __future__ import annotations
from typing import List
from abc import ABC, abstractmethod
from azul.simple_types import Tile, Points


class BoardPatternLineInterface(ABC):
    
    @abstractmethod
    def put(self, tiles: List[Tile]) -> None:
        pass
    
    @abstractmethod
    def finish_round(self) -> Points:
        pass
    
    @abstractmethod
    def state(self) -> str:
        pass
