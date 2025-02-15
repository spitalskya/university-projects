from typing import Callable, Literal, Optional
from warnings import warn
from timeit import default_timer
import numpy as np
import pandas as pd
from matplotlib.pyplot import Axes
from scipy.optimize import OptimizeResult
import matplotlib.pyplot as plt
from visualizer import Visualizer
from minimization_methods.gradient_descent import optimalStep, constantStep
from minimization_methods.quasi_newton import BFGS, DFP


class LogisticRegression:
    """Handles fitting logistic regression on given data via numerous optimization methods"""
    _solution: Optional[OptimizeResult]         # result of minimization of the objective function
    _prediction_function: Optional[
        Callable[[np.ndarray[np.ndarray]], np.ndarray[float]]
        ]   # function used to calculate probability of dependent value to be equal to 1

    minimization_time: Optional[float]      # time needed to minimize objective function
    fitted: bool                            # whether the data were already fitted
    coefficients: np.ndarray[float]         # coefficient to used for calculating the probability 
                                            # of dependent value to be equal to 1 with provided data

    def __init__(self) -> None:
        """Creates unfitted instance"""
        self._solution = None
        self.fitted = False
        self.minimization_time = None


    def fit(self,
            u: np.ndarray[np.ndarray],
            v: np.ndarray[float],
            method: Literal["BFGS", "DFP", "Cauchy", "Grad-Const"],
            step: Optional[Literal["optimal", "suboptimal"]] = None,
            time_minimization: bool = False) -> None:
        """Fits the regression, i.e., finds optimal coefficients
        for a sigmoid function which describes given data the best. Stores the function.

        Args:
            u (np.ndarray[np.ndarray]): training matrix with independent vectors
            v (np.ndarray[float]): training vector with values in {0, 1} corresponding to the rows of matrix `u`
            method (Literal['BFGS', 'DFP', 'Cauchy', 'Grad-Const'): minimization method to use 
                when determining coefficient for prediction function
            step (Optional[Literal['optimal', 'suboptimal']]): step size to use in minimization
                needs to be set for BFGS and DFP methods
                defaults to None
            time_minimization (bool): whether to store the time needed for minimization in self.time_minimization
                defaults to False.

        Raises:
            ValueError: 
                if `method` is not set or is not supported type
                if `step` is not set and `method` is either BFGS or DFP
        """
        if method is None:
            raise ValueError("Method must be set")

        # warn if the coefficients were already determined and prompt if should continue
        if self.fitted:
            warn("Overriding already fitted instance!")
            if (input("continue (y/n)? ").strip().lower() != "y"):
                return

        # objective function to be minimized used for determining the coefficients in the prediction function
        def objective_function(x: np.ndarray) -> float:
            return np.sum((1 - v) * np.dot(u, x) + np.log(1 + np.exp(-np.dot(u, x))))

        # gradient of the objective function
        def gradient(x: np.ndarray) -> np.ndarray[float]:
            return np.dot(u.T, (1 - v - (1 / (1 + np.exp(np.dot(u, x))))))

        # add vector of ones to the u matrix (for scalar coefficient)
        ones = np.ones((u.shape[0], 1))
        u = np.hstack((ones, u))

        if time_minimization:
            start = default_timer()

        # minimize the objective function
        x0 = np.zeros(u.shape[1])
        if method == "BFGS":
            if step is None: raise ValueError("For BFGS method, `step` must not be `None`")
            self._solution = BFGS(obj_fun=objective_function, grad=gradient, x_0=x0, step=step)
        elif method == "DFP":
            if step is None: raise ValueError(f"For DFP method, `step` must not be `None`")
            self._solution = DFP(obj_fun=objective_function, grad=gradient, x_0=x0, step=step)
        elif method == "Cauchy":
            self._solution = optimalStep(obj_fun=objective_function, grad=gradient, x_0=x0)
        elif method == "Grad-Const":
            self._solution = constantStep(obj_fun=objective_function, grad=gradient, x_0=x0, stepsize=2e-5)
        else:
            raise ValueError("Wrong method name provided, \
                             only \"BFGS\", \"DFP\", \"Cuachy\" and \"Grad-Const\" are supported")

        # store all necessary values

        # minimization time
        if time_minimization:
            self.minimization_time = default_timer() - start
        
        # optimal coefficients
        self.coefficients = self._solution.x

        # function to predict probability from vector of independent variables
        def sigmoid(u_for_pred: np.ndarray[np.ndarray]) -> np.ndarray[float]:
            return 1 / (1 + np.exp(-np.inner(self.coefficients, u_for_pred)))
        self._prediction_function = sigmoid

        # coefficient were determined
        self.fitted = True


    def get_result(self) -> OptimizeResult:
        """Returns the OptimizeResult from method optimization run

        Returns:
            OptimizeResult: result of the minimization
                x (np.ndarray): found optimum point
                trajectory (list[np.ndarray]): list of points that the method iterated through
                success (bool): boolean flag whether the minimization was successful
                message (str): message about success of the minimization
                nit (int): number of iterations
                nfev (int): number of objective function evaluations 
                njev (int): number of gradient evaluations 
        """
        return self._solution

    def predict_probability(self, u: np.ndarray[np.ndarray[int]]) -> np.ndarray[float]:
        """Returns probabilities of dependent variable being 1 from given u matrix of independent vectors

        Args:
            u (np.ndarray[np.ndarray[int]]): matrix of independent vectors

        Raises:
            ValueError: if model wasn't yet fitted (coefficients are not determined)

        Returns:
            np.ndarray[float]: array of predicted probabilities for each row of u matrix
        """
        if not self.fitted:
            raise ValueError("Can't use predict on a non-fitted model!")
        ones = np.ones((u.shape[0], 1))
        u = np.hstack((ones, u))

        result = self._prediction_function(u)

        return result

    def predict(self, u: np.ndarray[np.ndarray[int]]) -> np.ndarray[float]:
        """Returns predicted values of dependent variable from given u matrix of independent vectors
            probability of dependent variable being 1 >= 0.5 corresponds to 1
            else 0

        Args:
            u (np.ndarray[np.ndarray[int]]): matrix of independent vectors

        Raises:
            ValueError: if model wasn't yet fitted (coefficients are not determined)

        Returns:
            np.ndarray[float]: array of predicted predicted values of dependent variable for each row of u matrix
        """
        if not self.fitted:
            raise ValueError("Can't use predict on a non-fitted model!")
        return np.rint(self.predict_probability(u))
    
    
    def visualize(self, ax: Axes) -> None:
        """Visualized the convergence of the minimization run

        Args:
            ax (Axes): Axes instance to plot into
        """
        Visualizer.visualize(ax, self._solution.trajectory, self._solution.x)


def main() -> None:
    # example run of logistic regression on solvency data
    
    # load the training data
    train_data = pd.read_csv("data/credit_risk_train.csv")
    u_train, v_train = train_data.drop("Creditability", axis="columns").to_numpy(), train_data["Creditability"].to_numpy()


    # find the coefficients
    log_reg = LogisticRegression()
    log_reg.fit(u=u_train, v=v_train, method="DFP", step="optimal", time_minimization=True)
    print("Coefficients for the sigmoid:", log_reg.coefficients)
    print("Success:", log_reg.get_result().success)
    print("Time:", log_reg.minimization_time)
    
    # load the testing data
    test_data = pd.read_csv("data/credit_risk_test.csv")
    u_test = test_data.drop("Creditability", axis="columns").to_numpy()
    v_real, v_pred = test_data["Creditability"].to_numpy(), log_reg.predict(u_test)

    # calculate the percentage of correct predictions
    count_predicted_correctly: int = 0
    for i in range(len(v_real)):
        if v_real[i] == v_pred[i]:
            count_predicted_correctly += 1
    print("Correctly predicted:", count_predicted_correctly / len(v_real))

    # visualize the convergence of minimization
    _, ax = plt.subplots(1, 1)
    log_reg.visualize(ax)
    plt.show()


if __name__ == "__main__":
    main()
