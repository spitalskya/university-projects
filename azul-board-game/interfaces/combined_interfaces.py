"""Combined interfaces 

At the start of the game, Game needs to create concrete instances to pass
to constructors of certain classes. However, sometimes they except those
instances to implement different interfaces. The interfaces here combine
all the necessary ones (where needed), so that the Game can pass concrete
instances with correct type to constructors. Concrete classes which need
this structure then implement these combined interfaces.
"""


from abc import ABC, abstractmethod
from interfaces.factory_interfaces import FactoryBagInterface
from interfaces.used_tiles_interfaces import UsedTilesGiveInterface, UsedTilesTakeAllInterface


class BagInterface(FactoryBagInterface, ABC):
    """communication between Bag and Game
    
    Bag needs to be passed to Factroy constructor
    as implementation of FactoryBagInterfaces,
    but it does not need to know about state() method
    """
    @abstractmethod
    def state(self) -> str:
        pass

class UsedTilesInterface(UsedTilesGiveInterface, UsedTilesTakeAllInterface, ABC):
    """combines UsedTilesGive for PatternLine and Floor and UsedTilesTakeAll for Bag
    adds communication between Game and Bag
    """
    @abstractmethod
    def state(self) -> str:
        pass
