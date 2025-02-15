from typing import Callable, Optional
import numpy as np
from scipy.optimize import OptimizeResult, approx_fprime


def backtracking(obj_fun: Callable[[np.ndarray], float],
                 x_0: np.ndarray, s: np.ndarray,
                 grad: Optional[Callable[[np.ndarray], np.ndarray]]=None,
                 alpha: float=0.1, delta: float=0.5,
                 callback: Optional[callable]=None, args: tuple=(), **kwargs) -> OptimizeResult:
    """Method that minimizes objective function in the provided direction 
    using backtracking algorithm

    Args:
        obj_fun (Callable[[np.ndarray], float]): objective function to be minimized in the provided direction
        x_0 (np.ndarray): starting point of the minimization
        s (np.ndarray): direction to minimize in
        grad (Optional[Callable[[np.ndarray], np.ndarray]]): gradient of the objective function
            if None, approximation is used
            defaults to None
        alpha (float): alpha parameter for first Goldstein condition
            defaults to 0.1
        delta (float): factor of reduction of the step size 
            defaults to 0.5
        callback (Optional[callable]): function to be called in each iteration
            defaults to None
        args (tuple): args to be passed to the objective function and gradient
            defaults to ()

    Raises:
        ValueError: if starting point x_0 is not provided

    Returns:
        OptimizeResult: result of the minimization in the provided direction
            x (np.ndarray): found optimum point -> step size
            success (bool): boolean flag whether the minimization was successful
            nit (int): number of iterations
            nfev (int): number of objective function evaluations
            njev (int): number of gradient evaluations
    """
    if x_0 is None:
        raise ValueError("Initial guess 'x0' must be provided.")
       
    # approximate gradient if it was not provided
    if grad is None:
        def grad(x: np.ndarray) -> np.ndarray:
            return approx_fprime(x, obj_fun, *args)
    
    # get stopping condition
    maxiter: int = kwargs.get("maxiter", 1_000)
    
    # compute the initial values for Goldstein condition
    fun0: float = obj_fun(x_0, *args)
    direction_der_x_0: float = np.dot(grad(x_0), s)
    
    # start the iterations
    lam: float = 1
    it: int = 0
    success: bool
    # while first Goldstein condition is not satisfied
    while obj_fun(x_0 + lam * s, *args) >= fun0 + alpha * lam * direction_der_x_0:
        # stop if too many iterations were used
        if it == maxiter:
            success = False
            break

        # call callback if provided
        if callback is not None:
            callback(lam)
        
        # reduce lambda
        lam *= delta
        it += 1
    
    # if through rounding errors lambda became 0, it is unusable
    # therefore set the success of the minimization to False
    if lam == 0:
        success = False
    else:
        success = True

    # return the result of the minimization
    return OptimizeResult(x=lam, nit=it, nfev=it+1, njev=1, success=success)
    
    
def bisection(obj_fun: Callable[[np.ndarray], float],
              x_0: np.ndarray[float], s: np.ndarray[float], 
              grad: Optional[Callable[[np.ndarray], np.ndarray]]=None,
              callback: Optional[callable]=None, args: tuple=(), **kwargs) -> OptimizeResult:
    """Method that minimizes objective function in the provided direction 
    using bisection algorithm

    Args:
        obj_fun (Callable[[np.ndarray], float]): objective function to be minimized in the provided direction
        x_0 (np.ndarray): starting point of the minimization
        s (np.ndarray): direction to minimize in
        grad (Optional[Callable[[np.ndarray], np.ndarray]]): gradient of the objective function
            if None, approximation is used
            defaults to None
        callback (Optional[callable]): function to be called in each iteration
            defaults to None
        args (tuple): args to be passed to the objective function and gradient
            defaults to ()

    Raises:
        ValueError: if starting point x_0 is not provided

    Returns:
        OptimizeResult: result of the minimization in the provided direction
            x (np.ndarray): found optimum point -> step size
            success (bool): boolean flag whether the minimization was successful
            nit (int): number of iterations
            nfev (int): number of objective function evaluations
            njev (int): number of gradient evaluations
    """
    if x_0 is None:
        raise ValueError("Initial guess 'x0' must be provided.")
    
    # approximate gradient if it was not provided
    if grad is None:
        def grad(x: np.ndarray, *args) -> np.ndarray:
            return approx_fprime(x, obj_fun, *args)
    
    njev: int = 0

    # compute initial directional derivative
    dir_derivative_0: float = np.dot(grad(x_0, *args), s)

    # getting closed interval to be used in the following bisection
    # based on the value of directional derivative in x_0, find the interval 
    # which endpoints have different signs of directional derivative
    #   one endpoints is x_0, second one is moved exponentially further
    found_minimum: bool = False                
    x: np.ndarray[float] = x_0.copy()
    it_bounds: int = 0
    if dir_derivative_0 < 0:
        k: int = 1
        while True:
            x += k * s
            dir_derivative: float = np.dot(grad(x, *args), s)
            if dir_derivative > 0:
                a: np.ndarray[float] = x_0.copy()
                b: np.ndarray[float] = x.copy()
                break
            elif dir_derivative == 0:
                found_minimum = True
                break
            k *= 2
            njev += 1
            it_bounds += 1
    elif dir_derivative_0 > 0:
        k: int = 1
        while True:
            x -= k * s
            dir_derivative: float = np.dot(grad(x, *args), s)
            if dir_derivative < 0:
                a: np.ndarray[float] = x.copy()
                b: np.ndarray[float] = x_0.copy()
                break
            elif dir_derivative == 0:
                found_minimum = True
                break
            k *= 2
            njev += 1
            it_bounds += 1
    else:
        found_minimum = True

    # if the minimum point was found during the search for the minimization interval
    # return it
    if found_minimum:
        # compute the coefficient before direction s needed to move from x_0 to found optimum 
        lam: float = ((x - x_0) / s)[0]
        return OptimizeResult(x=lam, success=True, message="Optimatization successful", 
                          nit=it_bounds, njev=njev, nfev=0)
    
     
    # get stopping conditions
    tol: float = kwargs.get("tol", 1e-8)
    maxiter: int = kwargs.get("maxiter", 1_000)
    
    
    # start the iterations
    midpoint: np.ndarray[float] = (a+b) / 2   
    it: int
    for it in range(1, maxiter+1):
        # compute the directional derivative in the midpoint
        # adjust the midpoint accordingly
        dir_der_midpoint: float = np.dot(grad(midpoint, *args), s)
        if dir_der_midpoint < 0:
            a = midpoint.copy()
        elif dir_der_midpoint > 0:
            b = midpoint.copy()
        else:
            # if minimum was found, do not continue
            midpoint = (a+b) / 2
            break
          
        midpoint = (a+b) / 2

        # call callback if provided
        if callback is not None:
            callback(midpoint)
        
        # if interval is too small or directional derivative in the midpoint
        # is close to zero, end the minimization
        if (np.linalg.norm(b-a) < tol) or (np.abs(dir_der_midpoint) < tol):
            break

        njev += 1
    
    # determine whether the minimization was successful
    success: bool = (np.linalg.norm(b-a) < tol) or (np.abs(dir_der_midpoint) < tol)
    msg: str
    if success:
        msg = "Optimatization successful"
    else:
        msg = "Optimatization failed"

    # compute the coefficient before direction s needed to move from x_0 to found optimum 
    lam: float = ((midpoint - x_0) / s)[0]
    
    # return the result of the minimization
    return OptimizeResult(x=lam, success=success, message=msg, 
                          nit=it + it_bounds, tol=tol, njev=njev, nfev=0)
