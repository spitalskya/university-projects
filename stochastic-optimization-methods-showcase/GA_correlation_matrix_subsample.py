from typing import Callable
from itertools import combinations
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_olivetti_faces


def create_olivetti_correlation_matrix() -> None:
    """Creates and saves correlation matrix from olivetti_X dataset
    """
    print("\nCalculating olivetti sample correlation matrix")
    data = fetch_olivetti_faces(shuffle=True)
    X = data.images.reshape((data.images.shape[0], -1))  # Flatten 64x64 images to 1D
    cor_matrix: np.ndarray = np.corrcoef(X.T)
    np.savetxt("olivetti_cor_matrix.csv", cor_matrix, delimiter=",", fmt="%.8f")
    print("Finished\n")


def GA_correlation(cor_matrix: np.ndarray, m: int, max_gens: int = 1_000, population_size = 16, 
                   tournament_size: int = 4, crossover_k: int = 1,
                   p_mut: float = 1/10, max_mutation_value: int = 5,
                   show_progress: bool = True, show_result: bool = True
                   ) -> tuple[np.ndarray, float]:
    """Genetic algorithm that chooses `m` distinct variables with lowest sample covariance in `cor_matrix`

    Args:
        cor_matrix (np.ndarray): sample covariance matrix
        m (int): how many variables to choose
        max_gens (int, optional): maximum number of generations for the GA. Defaults to 1_000
        population_size (int, optional): how many chromosomes are stored in each generation. Defaults to 16.
        tournament_size (int, optional): size of the tournament for choosing parent pair. Defaults to 4.
        crossover_k (int, optional): at how many points do parent chromosomes cross-over to make a child. Defaults to 1.
        p_mut (float, optional): probability of mutating a child gene. Defaults to 1/10.
        max_mutation_value (int, optional): maximum possible absolute change of a gene in mutation. Defaults to 5.
        show_progress (bool, optional): whether to visualize progress of best chromosomes throughout generations. Defaults to True.
        show_result (bool, optional): whether to visualize progression of average fitness and best chromosome at the end. Defaults to True.

    Returns:
        tuple[np.ndarray, float]: pair, where first value is the optimal solution found by GA, second value is its fitness
    """

    def objective_function(x: np.ndarray, R: np.ndarray) -> float:
        """Calculates objective function for minimization problem
        Objective function is the maximum absolute value in sample correlation matrix
        of subsample of variables, outside the diagonal of the matrix
        

        Args:
            x (np.ndarray): indexes of the variables in the subsample
            R (np.ndarray): sample correlation matrix with diagonal set to 0

        Returns:
            float: value of the objective function
        """
        # we do not want to choose two same variables
        # objective function of such `x` is therefore maximum possible value
        if len(set(x)) != len(x):   
            return 1
        
        # if all chosen variables are different, calculate the maximum absolute value
        # in corresponding rows and columns of the sample correlation matrix
        return np.max(np.abs(R[np.ix_(x, x)]))

    
    def generate_initial_solution_with_fitness() -> tuple[np.ndarray, float]:
        """Generates initial solution of length m and calculates its fitness
        Initial solution is random subsample of variables without repetition

        Returns:
            tuple[np.ndarray, float]: pair of generated initial solution with its fitness
        """
        # generate random subsample of variables
        x: np.ndarray = np.random.randint(low=0, high=M, size=m)
        
        # while there are repeating variables, generate new subsample
        while len(set(x)) != len(x):
            x: np.ndarray = np.random.randint(low=0, high=M, size=m)
            
        # return the initial solution with its fitness
        return x, objective_function(x, R)
    
    
    def tournament_selection(tournament_size: int) -> np.ndarray:
        """Select the parent by tournament selection
        Selects randomly `tournament_size` chromosomes from the population.
        Returns the one with best fitness as parent

        Args:
            tournament_size (int): size of the random sample from population

        Returns:
            np.ndarray: chromosome with best fitness
        """
        
        # choose a random sample from chromosomes of size `tournament_size`
        tournament: list[tuple[np.ndarray, float]] = random.sample(chromosomes, k=tournament_size)
        
        # return the chromosome with best fitness
        return min(tournament, key=lambda x: x[1])[0]
    
    
    def k_crossover(parent_1: np.ndarray, parent_2: np.ndarray, k: int = 1) -> tuple[np.ndarray, np.ndarray]:
        """Generates two complementary children from parents `parent_1` and `parent_2` by crossover at `k` points

        Args:
            parent_1 (np.ndarray): first parent chromosome
            parent_2 (np.ndarray): second parent chromosome
            k (int, optional): number of crossing over points. Defaults to 1

        Returns:
            tuple[np.ndarray, np.ndarray]: two children chromosomes
        """
        
        # copy parents into children chromosomes
        # later, subsequences will be replaced by corresponding subsequence from other parent
        child_1: np.ndarray = parent_1.copy()
        child_2: np.ndarray = parent_2.copy()
        
        # generate k crossover points
        # add 0 to the beginning and m to the end so that indexes for subsequences are easily fetched 
        crossover_points: list[int] = [0] + sorted(random.sample(range(1, m), k=k)) + [m]
        
        # add subsequences from the other parent into the children
        for i in range(0, k + 1, 2):
            subsequence: slice = slice(crossover_points[i], crossover_points[i + 1])
            child_1[subsequence] = parent_2[subsequence]
            child_2[subsequence] = parent_1[subsequence]
        
        # return the generated children
        return child_1, child_2
    
    
    def mutate(child: np.ndarray) -> np.ndarray:
        """Mutates the child chromosomes
        Adds to each gene in chromosome a realization of U(-`max_mutation_value`, `max_mutation_value`)
        with probability `p_mut`

        Args:
            child (np.ndarray): child chromosome to be mutated

        Returns:
            np.ndarray: mutated child chromosome
        """
        # copy child chromosome for mutation
        child_mutated: np.ndarray = child.copy()
        
        # clipping function - if gene of mutated chromosome would fall outside [0, M)
        # replace it with the closest boundary
        clip: Callable[[float], float] = lambda x: min(M - 1, max(0, x))
        
        # iterate through each gene, mutate it with probability `p_mut`
        for i, x_i in enumerate(child_mutated):
            if random.random() < 1 - p_mut:
                continue
            
            # generate mutation shift and add it to the gene
            shift: int = random.randint(-max_mutation_value, max_mutation_value)
            child_mutated[i] = clip(x_i + shift)
        
        # return the mutated child
        return child_mutated
    
    
    def plot_chromosome(chromosome: np.ndarray, size: int, ax: plt.Axes, alpha: float = 1) -> None:
        """Plots the provided solution into `size`*`size` pixel grid

        Args:
            chromosome (np.ndarray): chromosome (solution) to be plotted
            size (int): dimension of the square grid plot
            ax (plt.Axes): figure to plot it into
            alpha (float): transparency level. Defaults to 1.
        """
        # generate matrix where 1 means that the corresponding pixel was chosen, 0 otherwise
        data = np.array([[1 if i*size + j in chromosome else 0 for j in range(size)] for i in range(size)] )
        ax.imshow(data, interpolation='nearest', cmap="Greys", alpha=alpha)
    
    # extract M
    M: int = cor_matrix.shape[0]   
    
    # chcek if m is smaller than M (we need to choose subsample)
    assert m < M, "m needs to be smaller than M"
    
    # check if tournament size was set smaller than population size
    assert tournament_size < population_size, "tournament_size needs to be smaller than population_size"
    
    # visualization in pixel grid only if number of variables is a square number
    if int(M ** 0.5) ** 2 != M:
        show_progress = False
         
    # set the diagonal values of sample correlation matrix to zeros 
    # so that during calculating objective function we do not have to worry about i != j
    R: np.ndarray = cor_matrix.copy()
    np.fill_diagonal(R, 0)
    
    # generate initial chromosomes - first value of the pair is chromosome, second is its fitness
    chromosomes: list[tuple[np.ndarray, float]] = [
        generate_initial_solution_with_fitness() for _ in range(population_size)
        ]

    # find the best chromosome with minimal fitness
    best_chromosome, best_fitness = min(chromosomes, key=lambda x: x[1])
    
    # list to store average fitness in each generation for visualization purposes
    fitnesses: list[float] = []
    
    # figure for solution progress
    if show_progress:
        fig, axs = plt.subplots(2, 5, figsize=(16, 8))
        axs = axs.ravel()
    
    # loop through generations
    for g in range(max_gens):
        # add average fitness of the generation to the `fitnesses` list
        fitnesses.append(sum([p[1] for p in chromosomes]) / len(chromosomes))
    
        # visualize best chromosome (so far) 10 times during the run
        # plot is shown at the end
        if show_progress and g % int(max_gens / 10) == 0:   
            ax: plt.Axes = axs[g // int(max_gens / 10)]
            for chromosome in chromosomes:
                plot_chromosome(chromosome[0], int(M ** 0.5), ax, alpha=0.25)
            ax.set_title(f"Chromosomes in {g}-th generation,\naverage fitness={fitnesses[-1]:.3f}")
            ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    
        # create children chromosomes
        children = []
        for _ in range(population_size // 2):      # each pairing creates two children
            # generate two children my crossing over parent chromosomes `crossover_k` times
            # parents are chosen by tournament of `tournament_size` random individuals
            child_1, child_2 = k_crossover(
                parent_1=tournament_selection(tournament_size), 
                parent_2=tournament_selection(tournament_size),
                k=crossover_k
                )
            
            # mutate both children chromosomes
            child_1_mut, child_2_mut = mutate(child_1), mutate(child_2)
            
            # add them to the children list with their fitnesses
            children.extend([
                (child_1_mut, objective_function(child_1_mut, R)),
                (child_2_mut, objective_function(child_2_mut, R)),
            ])
        
        # add children to the population of chromosomes
        chromosomes.extend(children)
        
        # sort the population by their fitness, keep only the first half
        chromosomes = sorted(chromosomes, key=lambda x: x[1])[:population_size]
        
        # if the better fitness was found, update the current solution
        if chromosomes[0][1] < best_fitness:
            best_chromosome, best_fitness = chromosomes[0]
    
    # visualization
    if show_progress:
        fig.suptitle("Progress of best chromosomes and average fitness in generations", fontsize=16)
        plt.tight_layout()
        plt.show()
    if show_result:
        if int(M ** 0.5) ** 2 != M:     # only show average fitness throughout generations, no pixel grid
            ax = plt.gca()
            ax.plot(fitnesses)
            ax.set_title("Average fitness in generations")
            ax.set_xlabel("generation")
            ax.set_ylabel("fitness")
            plt.show()
        else:                           # show fitness progression and pixel grid
            _, axs = plt.subplots(1, 2, figsize=(10, 6))
            
            axs[0].plot(fitnesses)
            axs[0].set_title("Average fitness in generations")
            axs[0].set_xlabel("generation")
            axs[0].set_ylabel("average fitness")
            
            plot_chromosome(best_chromosome, size=int(M ** 0.5), ax=axs[1])
            axs[1].set_title(f"Optimal solution found\noptimal fitness = {best_fitness:.3f}")
            axs[1].tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
            
            plt.tight_layout()
            plt.show()
    
    # return best solution found with its fitness
    return sorted(best_chromosome), best_fitness


def test_GA_compared_to_brute_force() -> None:
    """Compares brute force and GA algorithm on subsampling for smallest maximum absolute correlation
    """
    def brute_force(R: np.ndarray, m: int) -> float:
        """Finds the best subsample of length `m` with smallest maximum absolute correlation with brute force

        Args:
            R (np.ndarray): sample correlation matrix
            m (int): size of subsample

        Returns:
            float: smallest maximum absolute correlation for subsample of size `m`
        """
        M: int = R.shape[0]
        R_without_diagonal: np.ndarray = R.copy()
        np.fill_diagonal(R_without_diagonal, 0)
        
        results: list[float] = []
        for subsample in combinations(range(M), m):
            results.append(np.max(np.abs(R_without_diagonal[np.ix_(subsample, subsample)])))
        return min(results)
        
    
    small_R: np.ndarray = np.random.random(size=(4, 4)) * 2 - 1
    medium_R: np.ndarray = np.random.random(size=(8, 8)) * 2 - 1
    big_R: np.ndarray = np.random.random(size=(16, 16)) * 2 - 1
    very_big_R: np.ndarray = np.random.random(size=(40, 40)) * 2 - 1
    
    for m, R, mut_value in zip([2, 4, 6, 4], [small_R, medium_R, big_R, very_big_R], [1, 3, 5, 7]):
        np.fill_diagonal(R, 1)
        print(f"M={R.shape[0]}, m={m} -> brute_force={brute_force(R, m):.3f}, " +
              f"GA={GA_correlation(R, m, max_mutation_value=mut_value, show_progress=False, show_result=False)[1]:.3f}")


def main() -> None:
    # compare brute force and GA on small random correlation matrices
    #test_GA_compared_to_brute_force()
    
    # create olivetti sample correlation matrix
    create_olivetti_correlation_matrix()
    
    # test and visualize GA on olivetti sample correlation matrix
    cor_matrix: np.ndarray = pd.read_csv("olivetti_cor_matrix.csv", header=None).to_numpy()
    sol: tuple[np.ndarray, float] = GA_correlation(
        cor_matrix, m=40, max_gens=1000,            # should handle m=100 quite quickly
        max_mutation_value=10, crossover_k=5, tournament_size=4
        )
    print(f"Solution: {sol[0]}")
    print(f"Fitness: {sol[1]}")
    

if __name__ == "__main__":
    main()
