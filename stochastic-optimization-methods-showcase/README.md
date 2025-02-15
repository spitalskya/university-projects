# Stochastic optimization methods showcase

## 1. PSO Steiner Tree Optimization

This program implements a Particle Swarm Optimization (PSO) algorithm to solve the Euclidean Steiner Tree problem. Given a set of terminal points, the algorithm finds the optimal placement of additional vertices to minimize the total edge weight of the Steiner Tree.

### Functions

- `PSO_Steiner_tree(...)`: solves the Euclidean Steiner Tree problem using PSO.
- `binary_search_PSO_Steiner_tree(...)`: attempts to find the optimal number of vertices to be added using a binary search approach.
- `main()`: demonstrates the algorithm by solving the Steiner tree problem for randomly generated points.

### Key Features

- PSO-based optimization of additional vertices placement for the Steiner Tree.
- Visualization of particles' movements and optimization progress.
- Option to adjust the number of additional vertices to improve results.

---

## 2. Genetic Algorithm for Variable Selection

This program implements a genetic algorithm (GA) to select `m` variables from a sample covariance matrix. It aims to identify a subset of variables where their pairwise absolute correlation is minimal.

### Functions

- `GA_correlation(..)`: uses a genetic algorithm to select `m` variables with the lowest absolute correlation.
- `main()`: demonstrates the GA by creating a sample correlation matrix and applying the GA to select variables.

### Key Features

- Genetic algorithm-based optimization for selecting variables with minimal pairwise correlation.
- Adjustable parameters such as population size, mutation probability, and tournament size.
- Visualization of the GA's progress and results.
