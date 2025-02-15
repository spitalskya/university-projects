from __future__ import annotations
from typing import Optional
from abc import ABC, abstractmethod
from azul.simple_types import Tile


class WallLineAdjacentLineInterface(ABC):
    """Communication between WallLine and its WallLine-neighbours"""
    
    @abstractmethod
    def get_tile_in_column(self, column: int) -> Optional[Tile]:
        pass
    
    @abstractmethod
    def get_line_up(self) -> Optional[WallLineAdjacentLineInterface]:
        pass
    
    @abstractmethod
    def get_line_down(self) -> Optional[WallLineAdjacentLineInterface]:
        pass
