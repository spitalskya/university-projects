from __future__ import annotations
from typing import List
from abc import ABC, abstractmethod
from azul.simple_types import Tile


class TileSource(ABC):
    
    @abstractmethod
    def take(self, idx: Tile) -> List[Tile]:
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        pass

    @abstractmethod
    def state(self) -> str:
        pass
    
    @abstractmethod
    def start_new_round(self) -> None:
        pass
