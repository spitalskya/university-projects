from __future__ import annotations
from typing import Callable
from abc import ABC, abstractmethod


class GameInterface(ABC):
    
    @abstractmethod
    def register_callback(self, callback: Callable[[str], None]) -> None:
        pass
    
    @abstractmethod
    def start(self, num_of_players: int, *ids: int) -> bool:
        pass
    
    @abstractmethod
    def take(self, player_id: int, source_idx: int, idx: int, destination_idx: int) -> bool:
        """Method for communicating between players and the game
        
        returns whether the move was successful
            whether was player on turn and whether all Idxs were valid
        
        playerId - identification of the player
        sourceIdx - from what TileSource he takes a Tile/Tiles
        tileIdx - which type of Tile he takes
        destinationIdx - on which PatternLine he places the Tile/Tiles
        """
