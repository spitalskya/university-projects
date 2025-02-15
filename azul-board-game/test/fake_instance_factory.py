from __future__ import annotations
from typing import List, Optional, Dict
from interfaces.game_elements_interfaces import (BoardInterface, TableAreaInterface,
                                                 GameObserverInterface)
from interfaces.instance_factory_interface import InstanceFactoryInterface
from interfaces.combined_interfaces import UsedTilesInterface, BagInterface
from interfaces.round_results_interfaces import (FinalPointsCalculationInterface,
                                                 GameFinishedInterface)
from interfaces.observer_interface import ObserverInterface
from interfaces.used_tiles_interfaces import UsedTilesTakeAllInterface
from azul.simple_types import (Points, Tile, FinishRoundResult, NORMAL, 
                               BLUE, YELLOW, RED, BLACK, GREEN, STARTING_PLAYER)


class FakeInstanceFactory(InstanceFactoryInterface):
    
    def get_board(self, game_finished: GameFinishedInterface, 
                  final_points: FinalPointsCalculationInterface,
                  used_tiles: UsedTilesInterface) -> BoardInterface:
        return FakeBoard()
    
    def get_table_area(self, number_of_factories:int, 
                       bag: BagInterface) -> TableAreaInterface:
        return FakeTableArea()
    
    
    def get_bag(self, used_tiles: UsedTilesTakeAllInterface) -> BagInterface:
        return FakeBag()
    
    def get_game_observer(self) -> GameObserverInterface:
        return FakeGameObserver()
    
    def get_final_points_calculation(self) -> FinalPointsCalculationInterface:
        return FakeFinalPointsCalculation()
    
    def get_game_finished(self) -> GameFinishedInterface:
        return FakeGameFinished()
    
    def get_used_tiles(self) -> UsedTilesInterface:
        return FakeUsedTiles()


class FakeBoard(BoardInterface):
    lines: List[List[Tile]]
    points: Points
    
    def __init__(self) -> None:
        self.lines = [[] for _ in range(5)]
        self.points = Points(0)
    
    def put(self, destination_idx: int, tiles: List[Tile]) -> None:
        if STARTING_PLAYER in tiles:
            tiles.remove(STARTING_PLAYER)
        self.lines[destination_idx].extend(tiles)
    
    def finish_round(self) -> FinishRoundResult:
        return NORMAL

    def end_game(self) -> None:
        """Counts all put tiles on lines and that sets as points"""
        count: int = 0
        line: List[Tile]
        for line in self.lines:
            count += len(line)
            line.clear()
        self.points = Points(count)
    
    def state(self) -> str:
        result: List[str] = []
        line: List[Tile]
        for line in self.lines:
            result.append(str(list(map(str, line))))
        return '\n'.join(result)

class FakeTableArea(TableAreaInterface):
    tile_sources: List[List[Tile]]
    tile_idx_converter: Dict[int, Tile]
    
    def __init__(self) -> None:
        self.tile_sources = [[STARTING_PLAYER, RED, GREEN],
                             [BLACK, BLACK, GREEN]]
        self.tile_idx_converter = {0: BLACK, 1: BLUE, 2: GREEN, 3: RED, 4: YELLOW}
    
    def take(self, source_idx: int, idx: int) -> List[Tile]:
        """TableArea with only two Tile sources, no moving between them"""
        # from which tile source to take
        tile_source: List[Tile] = self.tile_sources[0 if source_idx == 0 else 1]
        
        tiles_to_take: List[Tile] = []
        if STARTING_PLAYER in tile_source:
            tiles_to_take.append(STARTING_PLAYER)
            tile_source.remove(STARTING_PLAYER)
        
        tile_idx: Tile = self.tile_idx_converter[idx]
        tile: Tile
        for tile in tile_source:
            if tile == tile_idx:
                tiles_to_take.append(tile)
        while tile_idx in tile_source:
            tile_source.remove(tile_idx)
        return tiles_to_take
    
    def is_round_end(self) -> bool:
        tile_source: List[Tile]
        for tile_source in self.tile_sources:
            if tile_source:
                return False   
        return True
    
    def start_new_round(self) -> None:
        self.tile_sources = [[STARTING_PLAYER, RED, GREEN],
                             [BLACK, BLACK, GREEN]]
    
    def state(self) -> str:
        return str(self.tile_sources)

class FakeBag(BagInterface):
    def take(self, count: int) -> List[Tile]:
        return []
    
    def state(self) -> str:
        return ''

class FakeUsedTiles(UsedTilesInterface):
    def give(self, tiles: List[Tile]) -> None:
        pass
    
    def take_all(self) -> List[Tile]:
        return []
    
    def state(self) -> str:
        return ''
    
class FakeGameFinished(GameFinishedInterface):
    def game_finished(self, wall: List[List[Tile | None]]) -> FinishRoundResult:
        return NORMAL

class FakeFinalPointsCalculation(FinalPointsCalculationInterface):
    def get_points(self, wall: List[List[Optional[Tile]]]) -> Points:
        return Points(0)

class FakeGameObserver(GameObserverInterface):
    
    def notify_everybody(self, state: str) -> None:
        pass
    
    def register_observer(self, observer: ObserverInterface) -> None:
        pass
    
    def cancel_observer(self, observer: ObserverInterface) -> None:
        pass
