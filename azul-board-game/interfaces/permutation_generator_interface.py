from __future__ import annotations
from abc import ABC, abstractmethod


class PermutationGeneratorInterface(ABC):
    
    @abstractmethod
    def get_permutation(self, length: int) -> list[int]:
        pass
