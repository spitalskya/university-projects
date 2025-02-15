"""Interfaces between Game and classes which Game
utilizes substantially
"""


from __future__ import annotations
from typing import List
from abc import ABC, abstractmethod
from interfaces.observer_interface import ObserverInterface
from azul.simple_types import Tile, Points, FinishRoundResult


class TableAreaInterface(ABC):
    """communication between TableArea and Game"""
    
    @abstractmethod
    def take(self, source_idx: int, idx: int) -> List[Tile]:
        pass
    
    @abstractmethod
    def is_round_end(self) -> bool:
        pass
    
    @abstractmethod
    def start_new_round(self) -> None:
        pass
    
    @abstractmethod
    def state(self) -> str:
        pass

class BoardInterface(ABC):
    """communication between Board and Game"""

    points: Points
    
    @abstractmethod
    def put(self, destination_idx: int, tiles: List[Tile]) -> None:
        pass
    
    @abstractmethod
    def finish_round(self) -> FinishRoundResult:
        pass

    @abstractmethod
    def end_game(self) -> None:
        pass
    
    @abstractmethod
    def state(self) -> str:
        pass

class GameObserverInterface(ABC):
    """Interface for observers of the game"""
    @abstractmethod
    def notify_everybody(self, state: str) -> None:
        pass
    
    @abstractmethod
    def register_observer(self, observer: ObserverInterface) -> None:
        pass
    
    @abstractmethod
    def cancel_observer(self, observer: ObserverInterface) -> None:
        pass
