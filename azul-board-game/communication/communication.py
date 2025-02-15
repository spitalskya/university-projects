from interfaces.game_interface import GameInterface
from azul.game import Game

class InputError(Exception):
    
    def __str__(self) -> str:
        return "wrong input values"

class Communication:
    """Layer that handles communication between terminal and the game
    
    Registers callback function to game to display state on terminal
    Checks initial validness of inputs
    """
    _game: GameInterface
    
    def __init__(self) -> None:
        """Initializes game, registers callback function for displaying on the terminal"""
        self._game = Game()
        self._game.register_callback(self.display)
        self.session()
    
    def session(self) -> None:
        """Takes terminal input arguments in loop, calls specific handlers"""
        
        self.display('Game initialized')
        while True:
            command: str
            parameters: list[str]
            try:
                command, *parameters = input().split()
                parameters_converted: list[int] = list(map(int, parameters))
                
                if command == 'start':
                    self.handle_start(*parameters_converted)
                elif command == 'take':
                    self.handle_take(*parameters_converted)
                elif command == 'end':
                    return
                else:
                    self.display('Command not recognized, use "end" if you want to end the game')
                    
            except ValueError:
                self.display('Valid commands are "start", "take" and "end"')
    
    def handle_start(self, *parameters: int) -> None:
        """Calls start() in Game and checks validness of input"""
        
        try:
            number_of_players: int = parameters[0]
            ids: list[int] = list(parameters[1:])
            if not self._game.start(number_of_players, *ids):
                raise InputError
        except InputError as e:
            self.display(f'Invalid start command: {str(e)}')
        except IndexError:
            self.display('Invalid start command: insufficient arguments')
    
    def handle_take(self, *parameters: int) -> None:
        """Calls take() in Game and checks validness of input"""
        
        try:
            player_id: int = parameters[0]
            source_idx: int = parameters[1]
            idx: int = parameters[2]
            destination_idx: int = parameters[3]
            if not self._game.take(player_id, source_idx, idx, destination_idx):
                raise InputError
        except InputError as e:
            self.display(f'Invalid take command: {str(e)}')
        except IndexError:
            self.display('Invalid start command: insufficient arguments')
    
    def display(self, state: str) -> None:
        """Displays state string on terminal"""
        print(state)

if __name__ == "__main__":
    Communication()
