import numpy as np 
from minimization_methods.gradient_descent import optimalStep, constantStep
from minimization_methods.quasi_newton import DFP, BFGS
from scipy.optimize import minimize

"""Test implemented minimization methods on functions from MVO labs"""

def f1(x, a=1):
    A = np.diag((1, a))
    h = np.array((a, a**2))
    return 0.5 * x@A@x - x@h

def df1(x, a=1):
    A = np.diag((1, a))
    h = np.array((a, a**2))
    return A@x - h

def f2(x):
    A = np.array([[11, 9],[9,10]])
    h = np.array((200, 190))
    return 0.5 * x@A@x - x@h

def df2(x):
    A = np.array([[11, 9],[9,10]])
    h = np.array((200, 190))
    return A@x - h

def generate_f3(n, ret_params=False):
    """
    Generate a quartic function f3(x) of the form
    0.25 * x^T * A * x + 0.5 * x^T * G * x + h^T * x.

    Parameters
    ----------
    n : int
        The dimension of the quadratic function.
    ret_params : bool, optional
        Whether to return additional parameters used to define the function.
        If True, returns the quartic function and its gradient..
        If False, returns also matrices A, G and vector h.

    Returns
    -------
    If `ret_params` is False, returns the quartic function Q(x) as
    a callable function and its gradient as callable function.

    If `ret_params` is True, returns a tuple containing:
        - The quartic function Q(x) as a callable function.
        - Gradient of Q(x) as callable function
        - A : numpy.ndarray
            A random n x n positive definite matrix.
        - G : numpy.ndarray
            A random n x n positive definite matrix.
        - h : numpy.ndarray
            A vector of length n.
    """
    A = np.random.randn(n, n)
    A = A@A.T + np.eye(n)

    G = np.random.randn(n, n)
    G = G@G.T + np.eye(n)

    h = np.random.randn(n)

    def f3(x):
        return 0.25 * (x@A@x)**2 + 0.5 * (x@G@x) + h@x

    def df3(x):
        return 0.5 * (x@A@x) *(A@x) + G@x + h

    if ret_params:
        return f3, df3, A, G, h

    return f3, df3


def main():
    f3, df3 = generate_f3(4)
    x3 = np.zeros(4)
    x = np.zeros(2)
    
    print("f1 minimum")
    print(minimize(fun=f1, x0=x, jac=df1, args=(5,)).x)
    print(optimalStep(obj_fun=f1, grad=df1, x_0=x, args=(5,)))
    print(constantStep(obj_fun=f1, grad=df1, x_0=x, args=(5, ), stepsize=1e-2).x)
    print(DFP(obj_fun=f1, grad=df1, x_0=x, args=(5, ), step="optimal").x)
    print(DFP(obj_fun=f1, grad=df1, x_0=x, args=(5,), step="suboptimal").x)
    print(BFGS(obj_fun=f1, grad=df1, x_0=x, args=(5,), step="optimal").x)
    print(BFGS(obj_fun=f1, grad=df1, x_0=x, args=(5,), step="suboptimal").x)
    print()
    
    print("f2 minimum")
    print(minimize(fun=f2, x0=x, jac=df2).x)
    print(optimalStep(obj_fun=f2, grad=df2, x_0=x, maxiter=100).x)
    print(constantStep(obj_fun=f2, grad=df2, x_0=x, stepsize=1e-2).x)
    print(DFP(obj_fun=f2, grad=df2, x_0=x, step="optimal").x)
    print(DFP(obj_fun=f2, grad=df2, x_0=x, step="suboptimal").x)
    print(BFGS(obj_fun=f2, grad=df2, x_0=x, step="optimal").x)
    print(BFGS(obj_fun=f2, grad=df2, x_0=x, step="suboptimal").x)
    print()
    
    print("f3 minimum")
    print(minimize(fun=f3, x0=x3, jac=df3).x)
    print(optimalStep(obj_fun=f3, grad=df3, x_0=x3, maxiter=100).x)
    print(constantStep(obj_fun=f3, grad=df3, x_0=x3, args=(), stepsize=1e-2).x)
    print(DFP(obj_fun=f3, grad=df3, x_0=x3, args=(), step="optimal").x)
    print(DFP(obj_fun=f3, grad=df3, x_0=x3, args=(), step="suboptimal").x)
    print(BFGS(obj_fun=f3, grad=df3, x_0=x3, args=(), step="optimal").x)
    print(BFGS(obj_fun=f3, grad=df3, x_0=x3, args=(), step="suboptimal").x)
    
    
if __name__ == "__main__":
    main()
