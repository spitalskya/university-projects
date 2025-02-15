from __future__ import annotations
from interfaces.observer_interface import ObserverInterface


class Observer(ObserverInterface):
    """Instances of this class get the notifications about changes in Game 
    
    Mediated by GameObserver publisher class
    """
    
    _last_message: str
    
    def __init__(self) -> None:
        self._last_message = ""
        
    def notify(self, new_state: str) -> None:
        self._last_message = new_state

    def get_message(self) -> str:
        return self._last_message
