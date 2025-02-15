import matplotlib.pyplot as plt
import numpy as np


class Visualizer:
    """Class that handles visualization of convergence plot"""

    @staticmethod
    def visualize(ax: plt.Axes, j_k: list[np.ndarray], j_opt: float) -> None:
        """Visualize convergence plot (distance of each iteration to optimum)

        Args:
            ax (plt.Axes): Axes instance to add the plot into
            j_k (list[np.ndarray]): list of points visited in each iteration of a method
            j_opt (float): optimum point found by the method
        """
        # construct a list of distances of each iteration to optimum
        distances: list[float] = []
        for point in j_k:
            norm: float = np.linalg.norm(point - j_opt)
            if norm != 0: distances.append(norm)
        iterations: list[int] = list(range(1, len(distances) + 1))
        
        # plot the distances on the log-scale
        ax.plot(iterations, distances, marker='.')
        ax.set_yscale('log')
        ax.set_xlabel('Iteration')
        ax.set_ylabel('$||J(x^k) - J^* ||_2$')
        ax.set_title('Convergence graph - distances to found optimum in each iteration')
        ax.grid(True)
