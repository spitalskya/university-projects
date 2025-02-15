from __future__ import annotations
from typing import List
from abc import ABC, abstractmethod
from azul.simple_types import Tile


class UsedTilesGiveInterface:
    def give(self, tiles: List[Tile]) -> None:
        pass

class UsedTilesTakeAllInterface(ABC):
    @abstractmethod
    def take_all(self) -> List[Tile]:
        pass
