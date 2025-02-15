from __future__ import annotations
from typing import List, Dict, Tuple, Optional, Callable
from interfaces.game_interface import GameInterface
from interfaces.instance_factory_interface import InstanceFactoryInterface
from interfaces.combined_interfaces import BagInterface, UsedTilesInterface
from interfaces.round_results_interfaces import (FinalPointsCalculationInterface,
                                                 GameFinishedInterface)
from interfaces.game_elements_interfaces import (BoardInterface, TableAreaInterface,
                                                 GameObserverInterface)
from azul.instance_factory import InstanceFactory
from azul.simple_types import (FinishRoundResult, GAME_FINISHED, 
                               Tile, STARTING_PLAYER,
                               Points)


class Game(GameInterface):
    
    _factory: InstanceFactoryInterface
    _game_started: bool
    _callback: Optional[Callable[[str], None]]
    _ended: bool
    
    _players: list[int]
    _number_of_players: int
    _player_on_turn: int
    _player_to_start_next_round: Optional[int]
        
    _game_observer: GameObserverInterface
    _table_area: TableAreaInterface
    _boards: Dict[int, BoardInterface]
    _final_points_calculation: FinalPointsCalculationInterface
    _game_finished: GameFinishedInterface
    _bag: BagInterface
    _used_tiles: UsedTilesInterface
        
    def __init__(self, instance_factory: Optional[InstanceFactoryInterface] = None) -> None:
        """Sets fields which are needed when start command is called"""
        self._callback = None
        if instance_factory:
            self._factory = instance_factory
        else:
            self._factory = InstanceFactory()
        self._ended = False
        self._game_started = False
        self._players = []
        self._player_to_start_next_round = None
    
    def register_callback(self, callback: Callable[[str], None]) -> None:
        """Registers callback function to Communication layer to display state of the game"""
        self._callback = callback
    
    def start(self, num_of_players: int, *ids: int) -> bool:
        """ Starts the game
        
        checks, whether the start command wasn't already called
        checks, whether the number of players are between 2 to 4 and all ids are unique ints
        if all checks pass, calls create_game() to setup the whole game
        """
        if self._ended: 
            self.notify("Game has ended")
            return False
        
        if num_of_players < 2 or num_of_players > 4 or self._game_started:
            return False
        if len(ids) != num_of_players:
            return False
        player_id: int
        for player_id in ids:
            if not isinstance(player_id, int):
                return False
            if ids.count(player_id) > 1:
                return False
        
        for i in range(num_of_players):
            self._players.append(ids[i])
        self._number_of_players = len(self._players)
        self._player_on_turn = 0
        self._game_started = True
        self.create_game()
        self.notify('Game started')
        self._table_area.start_new_round()
        self.notify(self.state())
        return True
        
    def create_game(self) -> None:
        """Sets up all necessary structures
        
        firstly, through InstanceFactory, sets up all instances which needs to be passed to inits
        secondly, creates TableArea and dictionary of player IDs and their boards
        """
        self._game_observer = self._factory.get_game_observer()
        self._used_tiles = self._factory.get_used_tiles()
        self._bag = self._factory.get_bag(self._used_tiles)
        self._final_points_calculation = self._factory.get_final_points_calculation()
        self._game_finished = self._factory.get_game_finished()
        
        
        self._table_area = self._factory.get_table_area(self.get_number_of_factories(), self._bag)
        self._boards = {}
        for player in self._players:
            self._boards[player] = self._factory.get_board(self._game_finished, 
                                                           self._final_points_calculation, 
                                                           self._used_tiles)
        
    def take(self, player_id: int, source_idx: int, idx: int, destination_idx: int) -> bool:
        """Method for communicating between players and the game
        
        returns whether the move was successful
            whether was player on turn and whether all Idxs were valid
        
        changes starting_player, if STARTING_PLAYER tile was taken
        
        playerId - identification of the player
        sourceIdx - from what TileSource he takes a Tile/Tiles
        idx - which type of Tile he takes
        destinationIdx - on which PatternLine he places the Tile/Tiles
        """
        if self._ended: 
            self.notify("Game has ended")
            return False
        
        if not (player_id == self._players[self._player_on_turn] and 
            0 <= source_idx <= self.get_number_of_factories() and
            0 <= idx <= 4 and
            0 <= destination_idx <= 4):
            return False
        

        tiles_taken: List[Tile] = self._table_area.take(source_idx, idx)
        if STARTING_PLAYER in tiles_taken:
            self._player_to_start_next_round = player_id
            
        self._boards[player_id].put(destination_idx, tiles_taken)
        
        if self._table_area.is_round_end():
            self.notify('Starting new round')
            self.start_new_round()
            self.notify(self.state())
            return True

        self._player_on_turn = (self._player_on_turn + 1) % self._number_of_players
        self.notify(self.state())
        return True
    
    def start_new_round(self) -> None:
        """ Starts new round
        
        firstly, calls finish_round() on all boards and checks, whether game should end
        if not calls start_new_round() on TableArea, which resets the Factories and TableCenter
            changes starting player to the one who drew STARTING_PLAYER tile 
            keeps the order of play
        if yes, calls end_game()
        """
        board: BoardInterface
        results: List[FinishRoundResult] = []
        for board in self._boards.values():
            results.append(board.finish_round())
        if GAME_FINISHED in results:
            self.end_game()
            return
        
        while self._player_to_start_next_round != self._players[0]:
            self._players = self._players[1:] + [self._players.pop(0)]
        self._player_to_start_next_round = None
        self._player_on_turn = 0
        
        self._table_area.start_new_round()

    def end_game(self) -> None:
        """Ends the game
        
        calls end_game() on all boards and gets Points from them
        """
        player_id: int
        board: BoardInterface
        player_points: Dict[int, Points] = {}
        for player_id, board in self._boards.items():
            board.end_game()
            player_points[player_id] = board.points
            
        scoreboard: List[Tuple[int, Points]] = self.evaluate_scores(player_points)
        self.determine_winner(scoreboard)
        
    def evaluate_scores(self, player_points: Dict[int, Points]) -> List[Tuple[int, Points]]:
        """From dictionary of player_id: Points obtained evaluates ranking"""
        return sorted(player_points.items(), key=lambda item: item[1], reverse=True)

    def determine_winner(self, scoreboard: List[Tuple[int, Points]]) -> None:
        """Handles who is the winner from scoreboard"""
        curent_rank: int = 1
        result: list[str] = []
        result.append('▼' * 10)
        result.append('FINAL SCOREBOARD:')
        previous_score: Points = scoreboard[0][1]
        player_id: int
        score: Points
        for player_id, score in scoreboard:
            if score < previous_score:
                curent_rank += 1
            previous_score = score
            result.append(f'{curent_rank}. place: {player_id} with {score} points')
        result.append('▲' * 10)
        self.notify('\n'.join(result))
        self._ended = True
    
    def state(self) -> str:
        """Returns state of the game as a string"""
        result: list[str] = []
        result.append('▼' * 10)
        result.append(f'Player to take: {self._players[self._player_on_turn]}')
        result.append('Take command structure: take [player ID] [tile source] ' \
            '[tile code] [pattern line]')
        result.append('')
        result.append('Tile codes: |0: L| |1: B| |2: G| |3: R| |4: Y|')
        result.append('')
        result.append(f'{self._table_area.state()}') 
        result.append('')       
        result.append(self.get_state_of_boards())
        result.append('')
        result.append(f'Bag: {self._bag.state()}')
        result.append(f'Used tiles: {self._used_tiles.state()}')
        result.append('▲' * 10)
        return '\n'.join(result)
    
    def get_state_of_boards(self) -> str:
        board_states: list[list[str]] = []
        player_id: int
        board: BoardInterface
        for player_id, board in sorted(self._boards.items()):
            current_state: list[str] = []
            current_state.append('-' * 15)
            current_state.append(f'Board of {player_id}')
            current_state.extend(board.state().split('\n'))
            current_state.append('-' * 15)
            board_states.append(current_state)
        
        result: list[str] = []
        just: int = 15
        for i in range(len(board_states[0])):
            row: str = ""
            board_state: list[str]
            for board_state in board_states:
                row += '|' + board_state[i].ljust(just) + '|' + '\t'
            result.append(row)
        
        return '\n'.join(result)
    
    def notify(self, new_state: str) -> None:
        """Notifies players and game observers with passed state"""
        if self._callback: 
            self._callback(new_state)
        self._game_observer.notify_everybody(new_state)

    def get_number_of_factories(self) -> int:
        """From number of players determines how many factories should be created"""
        num_of_factories: dict[int, int] = {2: 5, 3: 7, 4: 9}
        return num_of_factories[self._number_of_players]
    
    def get_board(self, player_id: int) -> BoardInterface:
        """Returns board of player_id player"""
        return self._boards[player_id]
