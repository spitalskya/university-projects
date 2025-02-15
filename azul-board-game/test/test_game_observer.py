from __future__ import annotations
import unittest
from typing import List
from interfaces.observer_interface import ObserverInterface
from azul.game_observer import GameObserver
from azul.observer import Observer


class TestGameObserver(unittest.TestCase):
    """Sociable test for GameObserver(publisher) and Observer(subscriber) classes"""
    
    def setUp(self) -> None:
        self.game_observer: GameObserver = GameObserver()
    
    def test_register_and_cancel(self) -> None:
        observers: List[ObserverInterface] = [Observer() for _ in range(5)]
        
        self.assertCountEqual(self.game_observer.get_observers(), [])
        
        observer: ObserverInterface
        for observer in observers:
            self.game_observer.register_observer(observer)
            self.assertIn(observer, self.game_observer.get_observers())

        not_registered_observer: ObserverInterface = Observer()
        self.game_observer.cancel_observer(not_registered_observer)
        self.assertCountEqual(self.game_observer.get_observers(), observers)
        
        for observer in observers:
            self.game_observer.cancel_observer(observer)
            self.assertNotIn(observer, self.game_observer.get_observers())
        
        self.assertCountEqual(self.game_observer.get_observers(), [])

    def test_notify_all(self) -> None:
        to_register: List[ObserverInterface] = [Observer() for _ in range(5)]
        
        observer: ObserverInterface
        for observer in to_register:
            self.game_observer.register_observer(observer)
        
        for observer in self.game_observer.get_observers():
            self.assertEqual(observer.get_message(), "")
        
        new_state: str = "State 1"
        self.game_observer.notify_everybody(new_state)
        for observer in self.game_observer.get_observers():
            self.assertEqual(observer.get_message(), new_state)
            
        new_state = "State 2"
        self.game_observer.notify_everybody(new_state)
        for observer in self.game_observer.get_observers():
            self.assertEqual(observer.get_message(), new_state)
