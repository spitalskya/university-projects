from __future__ import annotations
from abc import ABC, abstractmethod


class ObserverInterface(ABC):
    """Interface which each observer needs to implement"""
    @abstractmethod
    def notify(self, new_state: str) -> None:
        pass
    
    @abstractmethod
    def get_message(self) -> str:
        pass
