from __future__ import annotations
from typing import List
from abc import ABC, abstractmethod
from azul.simple_types import Tile
from interfaces.tile_source import TileSource

class FactoryBagInterface(ABC):
    
    @abstractmethod
    def take(self, count: int) -> List[Tile]:
        pass

class FactoryTableCenterInterface(TileSource, ABC):
    
    @abstractmethod
    def add(self, tiles: List[Tile]) -> None:
        pass
