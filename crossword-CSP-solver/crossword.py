import copy
import random
import sys
import time
from typing import Literal

################################# USEFUL TYPES ################################

Position = tuple[int, int, int, str]        # (start_row, start_col, length, direction)
Grid = list[list[str]]

# WordsDatabase[length][position][letter] -> indexes of all words of length `length` that have `letter` at `position`
WordsDatabase = dict[int, dict[int, dict[str, set[int]]]]   

############################### CLASS DEFINITION ##############################

class CrossWord():
    
    # grid of the crossword
    grid: Grid
    
    # (start_row, start_col, length, direction)
    positions: list[Position]   
    
    # domain for each position, indexes to `words` list
    position_domain: dict[Position, set[int]]   
    
    # domains of which positions are affected by change in certain position
    positions_affected: dict[Position, set[Position]] = {}  
    
    # overlap squares of two positions
    overlap: dict[Position, dict[Position, tuple[int, int]]] = {}   
        
    # dict of possible directions {name: (delta_row, delta_col)}
    directions: dict[str, tuple[int, int]] = {"down": (1, 0), "right": (0, 1)}

    def __init__(self, grid: Grid) -> None:
        self.grid: list[list[str]] = grid
        self.positions: list[tuple[int, int, int, str]] = self.get_positions(grid)
        self.set_positions_affected()


    def get_positions(self, grid: Grid) -> list[Position]:
        # Computes list of all possible positions for words.
        # Each position is a touple: (start_row, start_col, length, direction),
        # and length must be at least 2, i.e. positions for a single letter
        # (length==1) are omitted.
        # Note: Currently only for "down" and "right" directions.
        def check_line(line):
            res = []
            start_i, was_space = 0, False
            for i in range(len(line)):
                if line[i] == '#' and was_space:
                    was_space = False
                    if i - start_i > 1:
                        res.append((start_i, i - start_i))
                elif line[i] == ' ' and not was_space:
                    start_i = i
                    was_space = True
            return res

        poss = []
        for r in range(len(grid)):
            row = grid[r]
            poss = poss + [(r, p[0], p[1], "right") for p in check_line(row)]
        for c in range(len(grid[0])):
            column = [row[c] for row in grid]
            poss = poss + [(p[0], c, p[1], "down") for p in check_line(column)]
        
        return poss


    def set_positions_affected(self) -> None:
        """Computes values for `self.positions_affected` and `self.overlap`
        """
        # dictionary of squares corresponding to each position
        relevant_squares: dict[Position, set[tuple[int, int]]] = {}
        for pos in self.positions:
            relevant_squares[pos] = set()
            r, c, length, direction_str = pos
            dr, dc = self.directions[direction_str]
            for _ in range(length):
                relevant_squares[pos].add((r, c))
                r += dr
                c += dc
                
        # compute which positions' domains are affected by the change in `pos`
        # also, compute overlap square of `pos` and `other_pos`
        for pos in self.positions:
            self.positions_affected[pos] = set()
            self.overlap[pos] = {}
            for other_pos in self.positions:
                # same positions
                if pos == other_pos: 
                    continue
                
                # if there is a shared square corresponding to both position, update fields
                if relevant_squares[pos] & relevant_squares[other_pos]:
                    self.positions_affected[pos].add(other_pos)
                    self.overlap[pos][other_pos] = (relevant_squares[pos] & relevant_squares[other_pos]).pop()


    def __str__(self) -> str:
        """Returns formatted string of current crossword grid

        Returns:
            str: formatted string
        """
        return '\n'.join([''.join(row) for row in self.grid])

    
    def text_at_pos(self, position: Position) -> str:
        # Returns text currently written in specified position.
        dr, dc = self.directions[position[3]]
        r, c = position[0], position[1]
        return ''.join([self.grid[r + i * dr][c + i * dc] for i in range(position[2])])


    def write_word(self, position: Position, word: str) -> None:
        # Writes word to specified position and direction.
        # Note: this method does not check whether the word can be placed into
        # specified position.
        dr, dc = self.directions[position[3]]
        r, c = position[0], position[1]
        for i in range(position[2]):
            self.grid[r + i * dr][c + i * dc] = word[i]     
           
            
    def can_write_word(self, position: Position, word: str) -> bool:
        """Check whether the word can be placed into specified position,
        i.e. position is empty, or all letters within the position are same
        as those in the word.

        Args:
            position (Position): position to write into
            word (str): word to check if it can be written into provided `position`

        Returns:
            bool: whether the `word` can be written into provided `position`
        """
        # check if passed position is valid
        if position not in self.positions:
            return False
        
        dr, dc = self.directions[position[3]]
        r, c = position[0], position[1]
        length: int = position[2]
        
        # check if length of the word is the same as the length of the position
        if len(word) != length:
            return False
        
        # check whether squares corresponding to given position are all empty
        # or contain the same letter as `word` at that index
        for i in range(length):
            ch: str = self.grid[r][c]
            if not(ch == ' ' or ch == word[i]):
                return False
            r += dr
            c += dc
            
        return True
    
    
    def update_domains(self, assigned_position: Position,
                       words_db: WordsDatabase, words: list[str],
                       maintain_arc_consistency: bool = True,
                       show_AC_remaining_queue: bool = False) -> bool:   
        """Updates domains based on the new word written in `assigned_position`.
        
        Firstly, removes all words from domains of position that overlap with assigned position
        and now can't be written there.
        Secondly, if desired, maintain arc consistency.

        Args:
            assigned_position (Position): position recently filled with word
            words_db (WordsDatabase): database of words for easy searching through viable words
            words (list[str]): list of all words
            maintain_arc_consistency (bool, optional): whether to call arc consistency algorithm at the end. 
                Defaults to True.
            show_remaining_queue (bool, optional): whether to print progress of AC algorithm. 
                Defaults to False.

        Returns:
            bool: whether the updated crossword is solvable (all domains must have size >= 1)
        """
        # update domains of each position affected by adding a new word
        for affected_position in self.positions_affected[assigned_position]:      
            # get overlapping square of two positions in the grid
            overlap: tuple[int, int] = self.overlap[assigned_position][affected_position]
            
            # get the character written into the overlapping square
            changed_char: str = self.grid[overlap[0]][overlap[1]]
            
            # calculate the position of the overlapping square in the affected position
            idx_of_changed_char: int = overlap[0] - affected_position[0] if affected_position[3] == "down" else overlap[1] - affected_position[1]
            
            # get the new domain of the position
            # remove all words from it that do not have fetched letter at corresponding index
            new_domain: set[int] = words_db[affected_position[2]][idx_of_changed_char][changed_char] & self.position_domain[affected_position]
            
            # if new domain is empty, crossword is not solvable
            if not new_domain:
                return False
            
            # update the new domain
            self.position_domain[affected_position] = new_domain.copy()
            
        # call arc consistency algorithm with all arcs with nodes that may have changed their domain
        if maintain_arc_consistency:
            arcs: set[tuple[Position, Position]] = {(affected, assigned_position) for affected in self.positions_affected[assigned_position]}
            
            # return whether after maintaining AC is the crossword solvable
            return self.arc_consistency(arcs, words_db, words, show_AC_remaining_queue)
        
        # crossword is solvable
        return True           
    
    
    def arc_consistency(self, arcs: set[tuple[Position, Position]], 
                        words_db: WordsDatabase, words: list[str],
                        show_remaining_queue: bool = False) -> bool:
        """Algorithm that maintains arc consistency in the domains.

        Args:
            arcs (set[tuple[Position, Position]]): initial queue of the algorithm
            words_db (WordsDatabase): database of words for easy searching through viable words
            words (list[str]): list of all words
            show_remaining_queue (bool, optional): whether to print progress of AC algorithm. 
                Defaults to False.

        Returns:
            bool: whether the updated crossword is solvable (all domains must have size >= 1)
        """
        while arcs:
            # print if told to do so
            if show_remaining_queue:  
                print(f"Length of AC queue: {len(arcs)}, sum of domains' sizes: {sum([len(domain) for domain in self.position_domain.values()])}")
                
            p2, p1 = arcs.pop()
            new_p1_domain: set[str] = self.position_domain[p1].copy()
            
            # remove each word in domain of p1 for which there is no word in domain of p2
            # with the same letter at the overlapping square of the two positions
            for w1 in self.position_domain[p1]:
                overlap: tuple[int, int] = self.overlap[p1][p2]
                char1_idx: int = overlap[0] - p1[0] if p1[3] == "down" else overlap[1] - p1[1]
                char2_idx: int = overlap[0] - p2[0] if p2[3] == "down" else overlap[1] - p2[1]
                
                if not words_db[p2[2]][char2_idx][words[w1][char1_idx]] & self.position_domain[p2]:
                    new_p1_domain -= {w1}    
            
            length_new_p1_domain: int = len(new_p1_domain)
            
            # if no values were updated, don't add arcs from p1
            if length_new_p1_domain == len(self.position_domain[p1]):
                continue
            
            # if the new domain is empty, crossword is not solvable
            if length_new_p1_domain == 0:
                return False
            
            # if domain of p1 was updated, add its arcs to the queue
            self.position_domain[p1] = new_p1_domain.copy()
            arcs |= {(p3, p1) for p1 in self.positions for p3 in self.positions_affected[p1] if p3 != p2}
            
        # crossword is arc consistent and solvable
        return True
    
    
    def number_of_eliminated_words(self, assigned_position: Position, word: str,
                                   words_db: WordsDatabase, words: list[str],
                                   maintain_arc_consistency: bool) -> int:
        """Method used for least-constraining-value heuristic. Calculates how many
        words from all domains are eliminated after assigning word into `assigned_position`

        Args:
            assigned_position (Position): position recently filled with word
            word (str): word to be written in `assigned_position`
            words_db (WordsDatabase): database of words for easy searching through viable words
            words (list[str]): list of all words
            maintain_arc_consistency (bool): whether to consider values removed by AC algorithm

        Returns:
            int: how many words from all domains are eliminated after assigning word into `assigned_position`

        """
        # backup the current crossword state
        grid_before: Grid = copy.deepcopy(self.grid)
        domains_before: dict[Position, set[int]] = copy.deepcopy(self.position_domain)
        
        # reference values
        domain_size_before: int = sum([len(domain) for domain in self.position_domain.values()])
        
        # update domains
        self.write_word(assigned_position, word)
        res: bool = self.update_domains(assigned_position, words_db, words, maintain_arc_consistency)
        
        # if crossword is not solvable after assigning word into `assigned_position`, 
        # all values from domains were eliminated
        if not res:
            return domain_size_before
        
        # calculate the reduction in sum of sizes of domains
        result: int = domain_size_before - sum([len(domain) for domain in self.position_domain.values()])
        
        # restore the previous crossword state
        self.grid = copy.deepcopy(grid_before)
        self.position_domain = copy.deepcopy(domains_before)
        
        # return the number of eliminated words
        return result            
    
        
############################### SERVICE METHODS ###############################

def load_words(path) -> list[str]:
    # Loads all words from file
    return open(path, 'r').read().splitlines()


def load_grids(path: str) -> list[Grid]:
    # Loads empty grids from file
    raw = open(path, 'r').read().split("\n\n")
    per_rows = [grid.rstrip().split('\n') for grid in raw]
    per_char = [[list(row) for row in grid] for grid in per_rows]
    return per_char


def split_words_by_length(words: list[int]) -> dict[int, set[int]]:
    """Splits words into sets containing words with same length

    Args:
        words (list[int]): words to split

    Returns:
        dict[int, set[int]]: map from length to sets of words with given length
    """
    words_by_length: dict[int, set[str]] = {}
    for i, word in enumerate(words):
        length: int = len(word)
        if length not in words_by_length:
            words_by_length[length] = set()
        words_by_length[length].add(i)
    return words_by_length


def create_word_database(words: list[str]) -> WordsDatabase:
    """Creates "database" of words that allows easy and fast search for words that have
    certain letter at certain position.

    Args:
        words (list[str]): words to store in the "database"

    Returns:
        WordsDatabase: database of the words
            WordsDatabase[length][position][letter] -> indexes to `words` of all words of length `length` 
            that have `letter` at `position`
    """
    database: WordsDatabase = {}
    alphabet: list[str] = [chr(i) for i in range(ord('a'), ord('z') + 1)] + ['\'']
    for i, word in enumerate(words):
        length: int = len(word)
        
        # create dictionary for each position in the word with given length inside of which 
        # create dictionary with keys as characters from the alphabet
        if length not in database:
            database[length] = {i: {
                ch: set() for ch in alphabet
            } for i in range(length)}
        
        for j, ch in enumerate(word):
            database[length][j][ch].add(i)
        
    return database       


################################### SOLVING ###################################

def solve(cw: CrossWord, words: list[str], 
          show_progress: bool = False, show_remaining_AC_queue: bool = False, 
          maintain_arc_consistency: bool = True,
          unassigned_variable_heuristic: Literal["degree", "MRV", ""] = "degree",
          use_LCV: bool = False, LCV_size: int | None = None) -> bool:
    """Solves provided crossword with backtracking.

    Args:
        cw (CrossWord): crossword to be solved
        words (list[str]): words that can be used
        show_progress (bool, optional): whether to state of the filled crossword after each added word. 
            Defaults to True.
        show_remaining_AC_queue (bool, optional): whether to print progress of AC algorithm. 
            Defaults to False.
        maintain_arc_consistency (bool, optional): whether to maintain arc consistency in each step. 
            Defaults to True.
        unassigned_variable_heuristic (str, optional): heuristic to choose unassigned variable. 
            None used if "" is passed.
            Defaults to "degree".
        use_LCV (bool, optional): whether to use least-constraining-value heuristic to choose value to assign. 
            Defaults to False.
        LCV_size (int | None, optional): sample of how many values from domain to check during LCV run (performance purposes). 
            Defaults to None -> all values.
            
    Returns:
        bool: True if the crossword was solved, False if it can't be solved with provided words
    """      
    def solve_backtrack(cw: CrossWord) -> bool:
        """Backtracking function used to solve the crossword. 

        Args:
            cw (CrossWord): crossword to be solved

        Returns:
            bool: True if the crossword was solved, False if it can't be solved after previous word assignments
        """        
        # print progress if asked to do so
        if show_progress:
            print(cw)
            print("Sum of sizes of all domains:", sum([len(domain) for domain in cw.position_domain.values()]))

        # if the whole crossword is filled, return True
        if ' ' not in [ch for row in cw.grid for ch in row]:
            return True
        
        # get all unassigned positions
        unassigned_positions = [pos for pos in cw.positions if " " in cw.text_at_pos(pos)]
        
        # choose unassigned variable by passed heuristic
        MRV_heuristic = lambda p: len(cw.position_domain[p])
        degree_heuristic = lambda p: len(cw.positions_affected[p] - (set(cw.positions) - set(unassigned_positions)))
        
        if unassigned_variable_heuristic == "degree":
            unassigned_position = max(unassigned_positions, key=degree_heuristic)
        elif unassigned_variable_heuristic == "MRV":
            unassigned_position = min(unassigned_positions, key=MRV_heuristic)       
        else:
            unassigned_position = unassigned_positions[0]
            
        # backup state of the grid before the word assignment
        domains_before: dict[Position, set[int]] = copy.deepcopy(cw.position_domain)
        grid_before: Grid = copy.deepcopy(cw.grid)
        
        # get the domain of the chosen unassigned position to loop through
        domain: list[int] = list(cw.position_domain[unassigned_position])
        
        # if LCV heuristic should be used, calculate which word "eliminates" the smallest number of words in other domains
        if use_LCV:
            lcv: list[tuple[str, int]] = []
            
            # if LCV size is not set or is larger than available domain, set it do domain length
            # loop through words in domain
            for word_idx in random.sample(domain, k=min(LCV_size, len(domain) if LCV_size is not None else len(domain))):
                word = words[word_idx]
                
                # if the word can be written (probably redundant check), calculate how many words it eliminates
                if cw.can_write_word(unassigned_position, word):                   
                    lcv.append((
                        word_idx, 
                        cw.number_of_eliminated_words(unassigned_position, word, words_db, words, maintain_arc_consistency)
                        ))
            
            # order the domain from least to most-constraining-variables
            domain = [word_idx for word_idx, eliminated_words in sorted(lcv, key=lambda x: x[1])]
        
        # loop through the domain
        for word_idx in domain:     
            # if the word can be written (probably redundant check)
            if cw.can_write_word(unassigned_position, words[word_idx]):
                # write the word
                cw.write_word(unassigned_position, words[word_idx])
                
                # update domains
                # if crossword is not solvable, revert it to the previous state
                if not cw.update_domains(unassigned_position, words_db, words, maintain_arc_consistency, show_remaining_AC_queue):
                    cw.position_domain = copy.deepcopy(domains_before)
                    cw.grid = copy.deepcopy(grid_before)
                    continue
                
                # backtrack deeper
                if solve_backtrack(cw):
                    return True
                
                # if backtrack returned that the crossword is not solvable with currently filled word, remove it
                cw.position_domain = copy.deepcopy(domains_before)
                cw.grid = copy.deepcopy(grid_before)       
        
        # if no word returned solved crossword, crossword is not solvable in current state
        return False

    # separate words by length, assign these sets as domains of positions in crossword
    words_by_length: dict[int, set[int]] = split_words_by_length(words)
    cw.position_domain = {
        pos: words_by_length[pos[2]].copy() for pos in cw.positions
    }
    
    # create the database of words for easy searching through viable words meeting certain conditions
    words_db: WordsDatabase = create_word_database(words)  
    
    # print sum of sizes of all domains
    if show_progress:
        print("Sum of sizes of all domains:", sum([len(domain) for domain in cw.position_domain.values()]))
    
    # call arc consistency algorithm if asked to do so
    if maintain_arc_consistency:        
        cw.arc_consistency({(pos, affected) for pos in cw.positions for affected in cw.positions_affected[pos]},
                        words_db, words, show_remaining_AC_queue)
 
    # return the result of backtrack
    return solve_backtrack(cw)  

    
    
################################ MAIN PROGRAM #################################
def solve_one_crossword(words: list[str], grid: Grid, show_progress: bool = True,
                        maintain_arc_consistency: bool = True,
                        unassigned_variable_heuristic: Literal["degree", "MRV", ""] = "degree",
                        use_LCV: bool = False, LCV_size: int | None = None) -> None:
    """Solves one crossword with given grid, print the solution.

    Args:
        words (list[str]): words that can be used in solution
        grid (Grid): grid to be filled
        show_progress (bool, optional): whether to state of the filled crossword after each added word. 
            Defaults to True.
        maintain_arc_consistency (bool, optional): whether to maintain arc consistency in each step. 
            Defaults to True.
        unassigned_variable_heuristic (str, optional): heuristic to choose unassigned variable. 
            None used if "" is passed.
            Defaults to "degree".
        use_LCV (bool, optional): whether to use least-constraining-value heuristic to choose value to assign. 
            Defaults to False.
        LCV_size (int | None, optional): sample of how many values from domain to check during LCV run (performance purposes). 
            Defaults to None -> all values.
    """
    cw: CrossWord = CrossWord(grid)
    res: bool = solve(cw, words, show_progress, False, 
                      maintain_arc_consistency, unassigned_variable_heuristic, 
                      use_LCV, LCV_size)
    if res:
        print('=' * 40 + "\nCrossword was solved successfully")
        print(cw)
    else:
        if use_LCV and LCV_size is not None:        # using only sample for each LCV run
            print('=' * 40 + "\nSolution wasn't found")
        else:
            print('=' * 40 + "\nCrossword can't be solved with words from the given dictionary")


def solve_all_crosswords(words: list[str], grids: list[Grid], solutions_file: str | None = "solutions.txt", 
                         show_progress: bool = True,
                         maintain_arc_consistency: bool = True,
                         unassigned_variable_heuristic: Literal["degree", "MRV", ""] = "degree",
                         use_LCV: bool = False, LCV_size: int | None = None) -> None:
    """Times the solution of all 10 crosswords, stores results (solution and times) into a file.
    If no file is provided, prints to terminal.
    
    Beware, last crossword (empty 6x6) takes about 7 hours on Intel® Core™ i3-1115G4 processor
    (it has no solution, so it takes a while to test everything).
    Other crosswords together take about 20-25 minutes together to be solved on the processor above.

    Args:
        words (list[str]): words that can be used in solution
        grid (Grid): grid to be filled
        solutions_file (str | None, optional): file to store solutions in, if None, print to terminal. 
            Defaults to "solutions.txt".
        show_progress (bool, optional): whether to state of the filled crossword after each added word. 
            Defaults to True.
        maintain_arc_consistency (bool, optional): whether to maintain arc consistency in each step. 
            Defaults to True.
        unassigned_variable_heuristic (str, optional): heuristic to choose unassigned variable. 
            None used if "" is passed.
            Defaults to "degree".
        use_LCV (bool, optional): whether to use least-constraining-value heuristic to choose value to assign. 
            Defaults to False.
        LCV_size (int | None, optional): sample of how many values from domain to check during LCV run (performance purposes). 
            Defaults to None -> all values.
    """
    if len(grids) != 10:
        print("Please, provide all 10 grids")
    
    # order in which to evaluate crosswords
    order: list[int] = [0, 1, 2, 3, 4, 5, 7, 8, 6, 9] 
    # points for each crossword
    points: list[float] = [0.5, 1, 1.5, 1.5, 1.5, 2, 2, 2, 2, 2]
    points_so_far: float = 0
    
    # create file for solutions
    if solutions_file is not None:    
        with open(solutions_file, 'w') as file:
            pass
    
    # time the whole run
    start_of_run: float = time.time()
    for i in order:        
        # time the solving process
        start: float = time.time()
        print(f"solving crossword no. {str(i + 1)} ====")
        
        # solve the i-th crossword
        cw = CrossWord(grids[i])
        solve(cw, words, show_progress, False, 
              maintain_arc_consistency, unassigned_variable_heuristic, 
              use_LCV, LCV_size)
        
        # print/store results
        points_so_far += points[i]
        output_str: str = (
            "==== Crossword No." + str(i + 1) + " ====\n"
            + str(cw)
            + f"\nelapsed time crossword: {(time.time() - start)/60 :.5f}\n"
            + f"elapsed time total: {(time.time() - start_of_run)/60 :.5f}\n"
            + f"\nGiven all the solved crosswords are correct, you have so far {points_so_far}"
                " points!\n"
            + "=" * 24
        )
        
        if solutions_file is not None:
            with open(solutions_file, 'a') as file:
                sys.stdout = file
                print(output_str)
                sys.stdout = sys.__stdout__
        else:
            print(output_str)


if __name__ == "__main__":
    # load data
    words: list[str] = load_words("words.txt")    
    grids: list[Grid] = load_grids("krizovky.txt")
    # shuffle the words -> without this, even with sets as domain structures, 
    # some crosswords were consistently getting stuck, shuffling tries to reduce this problem
    random.shuffle(words)
    
    solve_one_crossword(words, grids[6], show_progress=True,
                        maintain_arc_consistency=True,
                        unassigned_variable_heuristic="degree",
                        use_LCV=False)
    
    """solve_all_crosswords(words, grids, solutions_file="solutions_new.txt", 
                        show_progress=True, 
                        maintain_arc_consistency=True,
                        unassigned_variable_heuristic="degree",
                        use_LCV=False)"""
