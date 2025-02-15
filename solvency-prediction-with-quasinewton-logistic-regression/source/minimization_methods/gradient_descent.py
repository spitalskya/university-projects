from typing import Callable, Optional
import numpy as np
from scipy.optimize import OptimizeResult, approx_fprime
from minimization_methods.minimization_in_direction import bisection


def optimalStep(obj_fun: Callable[[np.ndarray], float],
                grad: Optional[Callable[[np.ndarray], np.ndarray]],
                x_0: np.ndarray, args: tuple=(), callback: Optional[callable]=None, 
                **kwargs) -> OptimizeResult:
    """Implementation of Cauchy gradient method

    Args:
        obj_fun (Callable[[np.ndarray], float]): objective function to be minimized
        grad (Optional[Callable[[np.ndarray], np.ndarray]]): gradient of the objective function
            if None, approximation is used
        x_0 (np.ndarray): starting point
        args (tuple):  args to be passed to the objective function and its gradient
            defaults to ()
        callback (Optional[callable]): function to call in each iteration 
            defaults to None
            
    Raises:
        ValueError: if starting point x_0 is not provided
        
    Returns:
        OptimizeResult: result of the minimization
            x (np.ndarray): found optimum point
            trajectory (list[np.ndarray]): list of points that the method iterated through
            success (bool): boolean flag whether the minimization was successful
            message (str): message about success of the minimization
            nit (int): number of iterations
            nfev (int): number of objective function evaluations (also in calculating step size)
            njev (int): number of gradient evaluations (also in calculating step size)
    """
    if x_0 is None:
        raise ValueError("Must provide initial guess `x0`!")
    
    # approximate gradient if it was not provided
    if grad is None:
        def grad(x: np.ndarray, *args) -> np.ndarray:
            return approx_fprime(x, obj_fun, *args)
    
    # get stopping conditions   
    maxiter: int = kwargs.get("maxiter", 10_000)
    tol: float = kwargs.get("tol", 1e-3)
    
    # start the iterations
    x: np.ndarray = np.array(x_0, dtype=np.float64)
    trajectory: list[np.ndarray] = [x.copy()]
    it: int
    njev_bisection: int = 0
    for it in range(1, maxiter + 1):
        # calculate the gradient in current point
        grad_value: np.ndarray = grad(x, *args)
        
        # if norm of the gradient is small, break
        if np.linalg.norm(grad_value) < tol:
            break
        
        # find optimal step in direction of -gradient
        stepsize_info: OptimizeResult = bisection(obj_fun=obj_fun, grad=grad, x_0=x, args=args, s=-grad_value)
        if not stepsize_info.success:
            break
        stepsize: float = stepsize_info.x
        njev_bisection += stepsize_info.njev

        # move to the next point
        x -= stepsize * grad_value
        trajectory.append(x.copy())
        
        # call callback if provided
        if callback:
            callback(x)

    # determine whether the minimization was successful
    success: bool = np.linalg.norm(grad_value) < tol
    msg: str
    if success:
        msg = "Optimization successful"
    else:
        msg = "Optimization failed"

    # return the result of the minimization
    return OptimizeResult(x=x, success=success, 
                          message=msg, nit=it, nfev=0,
                          njev=it + njev_bisection, trajectory=trajectory)
    

def constantStep(obj_fun: Callable[[np.ndarray], float],
                 grad: Optional[Callable[[np.ndarray], np.ndarray]],
                 x_0: np.ndarray, args: tuple = (), callback: Optional[callable]=None, 
                 **kwargs) -> OptimizeResult:
    """Implementation of gradient method with constant step size

    Args:
        obj_fun (Callable[[np.ndarray], float]): objective function to be minimized
        grad (Optional[Callable[[np.ndarray], np.ndarray]]): gradient of the objective function
            if None, approximation is used
        x_0 (np.ndarray): starting point
        args (tuple):  args to be passed to the objective function and its gradient
            defaults to ()
        callback (Optional[callable]): function to call in each iteration 
            defaults to None

    Raises:
        ValueError: if starting point x_0 is not provided
    
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
    if x_0 is None:
        raise ValueError("Must provide initial guess `x_0`!")
    
    # approximate gradient if it was not provided
    if grad is None:
        def grad(x: np.ndarray, *args) -> np.ndarray:
            return approx_fprime(x, obj_fun, *args)

    # get stopping conditions
    maxiter: int = kwargs.get("maxiter", 10_000)
    tol: float = kwargs.get("tol", 1e-3)

    # get step size to use
    stepsize: float = kwargs.get("stepsize", 1e-1)

    # start the iterations
    x: np.ndarray = np.array(x_0, dtype=np.float64)
    trajectory: list[np.ndarray] = [x.copy()]
    it: int
    for it in range(1, maxiter+1):
        # calculate the gradient in current point
        grad_value: np.ndarray = grad(x, *args)

        # if norm of the gradient is small, break
        if np.linalg.norm(grad_value) < tol:
            break
        
        # move to the next point
        x -= stepsize * grad_value
        trajectory.append(x.copy())

        # call callback if provided
        if callback is not None:
            callback(x)

    # determine whether the minimization was successful
    success: bool = np.linalg.norm(grad_value) < tol
    msg: str
    if success:
        msg = "Optimization successful"
    else:
        msg = "Optimization failed"

    # return the result of the minimization
    return OptimizeResult(x=x, success=success, message=msg,
                          grad_value=grad_value, 
                          nit=it, njev=it, trajectory=trajectory)

