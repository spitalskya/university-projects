# Crosswords - constraint satisfaction problem solver

This project implements a solution for solving a crossword puzzle using a constraint satisfaction problem (CSP) approach. The main algorithm used for solving the puzzle is backtracking, where we attempt to fill the puzzle by selecting words sequentially and exploring possible solutions. If a valid solution is found, the process ends; otherwise, we backtrack and try other options.

## Heuristics Implemented:

To improve the performance of the backtracking algorithm, several heuristics were added:

- **Minimum Remaining Values (MRV)**: The algorithm selects the sequence with the fewest valid words to fill, reducing branching at higher levels of the search tree.
- **Degree Heuristic**: It prioritizes sequences that overlap with the most other sequences, reducing the search space in future steps.
- **Least Constraining Value (LCV)**: This heuristic chooses the word that minimizes the restrictions placed on the remaining sequences.

## Optimization:

The efficiency of the algorithm was improved with:

- **Forward-checking**: After each word assignment, the domains of overlapping sequences are updated to only include words that can still be validly placed.
- **Maintaining Arc Consistency (MAC)**: The algorithm uses the AC-3 algorithm to ensure that every pair of overlapping sequences is consistent with each other, reducing the chances of dead ends.
- **Word Database**: A pre-processed word dictionary was created to speed up the search, allowing constant time access to words matching specific constraints.

Heuristic combinations were tested, with the degree heuristic and MAC algorithm proving to be the most effective overall. The Least Constraining Value heuristic was computationally expensive and not used effectively in larger puzzles.

Overall, the solution demonstrates the utility of heuristics in improving the efficiency of CSP solvers, especially for larger and more complex problems.

A more detailed description is available in the [report](report.pdf).  
