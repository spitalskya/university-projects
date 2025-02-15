from __future__ import annotations
from typing import List


class Points:
    _value: int

    def __init__(self, value: int):
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    @staticmethod
    def sum(points_list: List[Points]) -> Points:
        return Points(sum((x.value for x in points_list)))
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Points):
            return NotImplemented
        return self._value == other.value
    
    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Points):
            return NotImplemented
        return self._value < other.value
    
    def __str__(self) -> str:
        return str(self._value)


class Tile:
    _representation: str

    def __init__(self, representation: str):
        self._representation = representation

    def __str__(self) -> str:
        return self._representation


class FinishRoundResult:
    """0 represents that game did not end, 1 represents that game ended"""
    _value: int

    def __init__(self, value: int):
        self._value = value
        
    @property
    def value(self) -> int:
        return self._value
    
    def __str__(self) -> str:
        return "normal" if self._value == 0 else "gameFinished"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FinishRoundResult):
            return NotImplemented
        return self._value == other.value


STARTING_PLAYER: Tile = Tile("S")
RED: Tile = Tile("R")
BLUE: Tile = Tile("B")
YELLOW: Tile = Tile("Y")
GREEN: Tile = Tile("G")
BLACK: Tile = Tile("L")

NORMAL: FinishRoundResult = FinishRoundResult(0)
GAME_FINISHED: FinishRoundResult = FinishRoundResult(1)

def compress_tile_list(tiles: List[Tile]) -> str:
    return "".join([str(x) for x in tiles])
