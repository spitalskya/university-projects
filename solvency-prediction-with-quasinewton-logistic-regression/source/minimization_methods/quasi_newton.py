from typing import Callable, Optional, Literal, Any
import numpy as np
from scipy.optimize import OptimizeResult, minimize, approx_fprime
from minimization_methods.minimization_in_direction import bisection, backtracking


def BFGS(obj_fun: Callable[[np.ndarray], float],
         grad: Optional[Callable[[np.ndarray], np.ndarray]],
         x_0: np.ndarray, step: Literal["optimal", "suboptimal"], args: tuple=(), 
         callback: Optional[callable]=None, **kwargs) -> OptimizeResult:
    """BFGS quasinewton minimization method

    Args:
        obj_fun (Callable[[np.ndarray], float]): objective function to be minimized
        grad (Optional[Callable[[np.ndarray], np.ndarray]]): gradient of the objective function
            if None, approximation is used
        x_0 (np.ndarray): starting point
        step (Literal['optimal', 'suboptimal']): step size to use in each iteration
            'optimal' - found with bisection
            'suboptimal' - found with backtracking
        args (tuple):  args to be passed to the objective function and its gradient
            defaults to ()
        callback (Optional[callable]): function to call in each iteration 
            defaults to None
    
    Raises:
        ValueError: if step is not 'optimal' or 'suboptimal'
    
    Returns:
        OptimizeResult: result of the minimization
            x (np.ndarray): found optimum point
            trajectory (list[np.ndarray]): list of points that the method iterated through
            success (bool): boolean flag whether the minimization was successful
            message (str): message about success of the minimization
            nit (int): number of iterations of BFGS method
            nfev (int): number of objective function evaluations (also in calculating step size)
            njev (int): number of gradient evaluations (also in calculating step size)
    """
    # determine function used to calculate the step size in each iteration
    step_optimizer: callable
    if step == "optimal":
        step_optimizer = bisection
    elif step == "suboptimal":
        step_optimizer = backtracking
    else:
        raise ValueError("step argument must be either \"optimal\" or \"suboptimal\"")
    
    # approximate gradient if it was not provided
    if grad is None:
        def grad(x: np.ndarray, *args) -> np.ndarray:
            return approx_fprime(x, obj_fun, *args)
    
    # get stopping conditions
    maxiter: int = kwargs.get("maxiter", 10_000)
    tol: float = kwargs.get("tol", 1e-3)
    
    # calculate the intitial value of the gradient and H matrix
    g: np.ndarray = grad(x_0, *args)
    H: np.ndarray[np.ndarray] = np.identity(x_0.shape[0])
    x: np.ndarray = np.array(x_0, dtype=np.float64)
    
    # start the iterations
    nfev: int = 0
    njev: int = 1
    trajectory: list[np.ndarray] = [x.copy()]
    for it in range(1, maxiter + 1):
        # calculate the direction in current iteration
        s: np.ndarray = np.array(-H @ g, dtype=np.float64)
        
        # find optimal or suboptimal step in that direction
        step_optimizer_result: OptimizeResult = step_optimizer(obj_fun=obj_fun, grad=grad, x_0=x, s=s, args=args)
        if not step_optimizer_result.success:
            break
        nfev += step_optimizer_result.nfev
        njev += step_optimizer_result.njev
        lam: float = step_optimizer_result.x
        
        # if the step is too small, break (may produce zeroes in the denominator later)
        if np.abs(lam) < 1e-8: 
            break
        
        # calculate next point
        x_plus: np.ndarray = x + lam * s
        g_plus: np.ndarray = grad(x_plus, *args)
        trajectory.append(x_plus.copy())
        
        # call callback if provided
        if callback:
            callback(x_plus)
        
        # if norm of the gradient is small, break
        if np.linalg.norm(g_plus) < tol:
            break
        
        # H+ calculation
        y: np.ndarray = g_plus - g
        p: np.ndarray = x_plus - x
        yp_outer: np.ndarray = np.outer(y, p)
        denominator: float = np.dot(p, y)
        H += ((1 + (y @ H @ y)/denominator) * ((np.outer(p, p)) / denominator)
               - (H @ yp_outer + yp_outer.T @ H) / denominator)
        
        # set the new values
        x = x_plus
        g = g_plus
    
    # determine whether the minimization was successful
    msg: str
    success: bool
    if np.linalg.norm(g_plus) < tol:
        msg, success = "Optimization successful", True
    else:
        msg, success = "Optimization not successful", False
    
    # return the result of the minimization
    return OptimizeResult(x=x_plus, trajectory=trajectory, 
                          success=success, message=msg,
                          nit=it, nfev=nfev, njev=njev+it)


def DFP(obj_fun: Callable[[np.ndarray], float],
        grad: Optional[Callable[[np.ndarray], np.ndarray]],
        x_0: np.ndarray, step: Literal["optimal", "suboptimal"],
        args: tuple=(), callback: Optional[callable]=None, **kwargs) -> OptimizeResult:   
    """DFP quasinewton minimization method

    Args:
        obj_fun (Callable[[np.ndarray], float]): objective function to be minimized
        grad (Optional[Callable[[np.ndarray], np.ndarray]]): gradient of the objective function
            if None, approximation is used
        x_0 (np.ndarray): starting point
        step (Literal['optimal', 'suboptimal']): step size to use in each iteration
            'optimal' - found with bisection
            'suboptimal' - found with backtracking
        args (tuple):  args to be passed to the objective function and its gradient
            defaults to ()
        callback (Optional[callable]): function to call in each iteration 
            defaults to None
            
    Raises:
        ValueError: if step is not 'optimal' or 'suboptimal'

    Returns:
        OptimizeResult: result of the minimization
            x (np.ndarray): found optimum point
            trajectory (list[np.ndarray]): list of points that the method iterated through
            success (bool): boolean flag whether the minimization was successful
            message (str): message about success of the minimization
            nit (int): number of iterations of DFP method
            nfev (int): number of objective function evaluations (also in calculating step size)
            njev (int): number of gradient evaluations (also in calculating step size)
    """
    # determine function used to calculate the step size in each iteration
    step_optimizer: callable
    if step == 'optimal':
        step_optimizer = bisection
    elif step == 'suboptimal':
        step_optimizer = backtracking
    else:
        raise ValueError("step argument must be either \"optimal\" or \"suboptimal\"")

    # approximate gradient if it was not provided
    if grad is None:
        def grad(x: np.ndarray, *args) -> np.ndarray:
            return approx_fprime(x, obj_fun, *args)
    
    # get stopping conditions
    maxiter: int = kwargs.get("maxiter", 10_000)
    tol: float = kwargs.get("tol", 1e-3)
    
    # calculate the intitial value of the gradient and H matrix
    g: np.ndarray = grad(x_0, *args)
    H: np.ndarray[np.ndarray] = np.identity(x_0.shape[0])
    x: np.ndarray = np.array(x_0, dtype=np.float64)

    # start the iterations
    nfev: int = 0
    njev: int = 1
    trajectory: list[np.ndarray] = [x.copy()]
    for it in range(1, maxiter + 1):
        # calculate the direction in current iteration
        s: np.ndarray = np.array(-H @ g, dtype=np.float64)

        # find optimal or suboptimal step in that direction
        step_optimizer_result: OptimizeResult = step_optimizer(obj_fun=obj_fun, grad=grad, x_0=x, s=s, args=args)
        if not step_optimizer_result.success:
            break
        nfev += step_optimizer_result.nfev
        njev += step_optimizer_result.njev
        step_len: float = step_optimizer_result.x

        # if the step is too small, break (may produce zeroes in the denominator later)
        if np.abs(step_len) < 1e-8:
            break

        
        # calculate next point
        x_plus = x + step_len * s
        g_plus = grad(x_plus, *args)
        njev += 1
        trajectory.append(x_plus.copy())

        # call callback if provided
        if callback:
            callback(x_plus)

        # if norm of the gradient is small, break
        if np.linalg.norm(g_plus) < tol:
            break

        # H+ calculation
        p_k = x_plus - x
        y_k = g_plus - g
        H += (np.outer(p_k, p_k) / np.inner(p_k, y_k)) - ((H @ np.outer(y_k, y_k) @ H) / (y_k @ H @ y_k))

        # set the new values
        x = x_plus
        g = g_plus
        
    # determine whether the minimization was successful
    if np.linalg.norm(g_plus) < tol:
        msg, success = "Optimization successful", True
    else:
        msg, success = "Optimization not successful", False

    # return the result of the minimization
    return OptimizeResult(x=x_plus, success=success, message=msg,
                          nit=it, nfev=nfev, njev=njev, trajectory=trajectory)
