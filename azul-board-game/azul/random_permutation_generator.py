from __future__ import annotations
from random import shuffle
from interfaces.permutation_generator_interface import PermutationGeneratorInterface


class RandomPermutationGenerator(PermutationGeneratorInterface):
    """Permutation generator for Bag, to isolate random element"""
    def get_permutation(self, length: int) -> list[int]:
        permutation = list(range(length))
        shuffle(permutation)
        return permutation
