from __future__ import annotations
from typing import List, Dict
from interfaces.tile_source import TileSource
from interfaces.game_elements_interfaces import TableAreaInterface
from interfaces.factory_interfaces import FactoryBagInterface, FactoryTableCenterInterface
from azul.simple_types import Tile, BLACK, BLUE, GREEN, RED, YELLOW
from azul.table_center import TableCenter
from azul.factory import Factory

class TableArea(TableAreaInterface):
    
    _tile_sources: List[TileSource]
    _tile_idx_converter: Dict[int, Tile]

    def __init__(self, num_of_factories: int, bag: FactoryBagInterface) -> None:
        """Creates list of TileSources
        
        0 - TableCenter
        1...num_of_factories: Factory
        """
        
        self._tile_idx_converter = {0: BLACK, 1: BLUE, 2: GREEN, 3: RED, 4: YELLOW}

        table_center: FactoryTableCenterInterface = TableCenter()
        self._tile_sources = [table_center]
        self._tile_sources.extend(
            Factory(bag, table_center) for _ in range(num_of_factories)
        )

    def take(self, source_idx: int, idx: int) -> List[Tile]:
        """Calls take() on corresponding tile source"""
        
        tile_to_take: Tile = self._tile_idx_converter[idx]
        return self._tile_sources[source_idx].take(tile_to_take)
    
    def is_round_end(self) -> bool:
        """Checks if all tile sources are empty"""
        return all(tile_source.is_empty() for tile_source in self._tile_sources)

    def start_new_round(self) -> None:
        """Calls start_new_round() on all tile sources"""
        tile_source: TileSource
        for tile_source in self._tile_sources:
            tile_source.start_new_round()

    def state(self) -> str:
        result: str = ""
        tile_source: TileSource
        for i, tile_source in enumerate(self._tile_sources):
            if i == 0:
                result += f'Table center: |0: {tile_source.state()}|\nFactories: '
            else:
                result += f'|{i}: {tile_source.state()}| '
        return result

    def get_tile_sources(self) -> List[TileSource]:
        return self._tile_sources
