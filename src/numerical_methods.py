import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar
from scipy.integrate import odeint, quad
import scipy.linalg
import time

# LU Decomposition
def run_lu_decomposition():
    A = np.array([[4, 3], [6, 3]])
    b = np.array([10, 12])
    lu, piv = scipy.linalg.lu_factor(A)
    x = scipy.linalg.lu_solve((lu, piv), b)
    return A, b, x

# Root Finding
def solve_roots():
    f = lambda x: x**3 - x - 2
    res = minimize_scalar(lambda x: abs(f(x)), bounds=(1, 2), method='bounded')
    return res.x

# Interpolation
def interpolate_values():
    x = np.array([0, 1, 2, 3])
    y = np.array([1, 3, 2, 5])
    xp = np.linspace(0, 3, 100)
    yp = np.interp(xp, x, y)
    return x, y, xp, yp

# Differentiation
def differentiate_data():
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    dy_dx = np.gradient(y, x)
    return x, dy_dx

# Integration
def integrate_data():
    f = lambda x: np.exp(-x**2)
    area, _ = quad(f, 0, 1)
    return area

# ODE Solving
def solve_odes():
    def model(y, t):
        return -2 * y
    t = np.linspace(0, 5, 100)
    y0 = 1
    y = odeint(model, y0, t)
    return t, y

# Optimization
def optimize_function():
    f = lambda x: (x - 2)**2 + 1
    res = minimize_scalar(f, bounds=(0, 4), method='bounded')
    return res.x, res.fun

# LU vs Direct Comparison
def compare_lu_vs_direct():
    A = np.array([[4, 3], [6, 3]])
    b1 = np.array([10, 12])
    b2 = np.array([20, 30])

    start_direct = time.perf_counter()
    x1_direct = np.linalg.solve(A, b1)
    x2_direct = np.linalg.solve(A, b2)
    time_direct = time.perf_counter() - start_direct

    start_lu = time.perf_counter()
    lu, piv = scipy.linalg.lu_factor(A)
    x1_lu = scipy.linalg.lu_solve((lu, piv), b1)
    x2_lu = scipy.linalg.lu_solve((lu, piv), b2)
    time_lu = time.perf_counter() - start_lu

    return {
        "x1_direct": x1_direct,
        "x2_direct": x2_direct,
        "x1_lu": x1_lu,
        "x2_lu": x2_lu,
        "time_direct": time_direct,
        "time_lu": time_lu
    }
