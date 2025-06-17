"""
ODE Solution
------------
RC step response; R ve C değerleri panelden alınır (ODE_R, ODE_C).
"""
import numpy as np
from scipy.integrate import solve_ivp


def run(netlist_str: str, fig, params=None):
    p = params or {}
    R = p.get("ODE_R", 1_000.0)     # Ω
    C = p.get("ODE_C", 1e-6)        # F
    Vin = 10.0
    tau = R * C

    def f(t, v): return (Vin - v) / (R * C)

    sol = solve_ivp(f, (0, 5*tau), [0], max_step=tau/20)
    t, v = sol.t * 1000, sol.y[0]   # ms

    fig.clf(); ax = fig.add_subplot(111)
    ax.plot(t, v); ax.set_xlabel("Time (ms)"); ax.set_ylabel("v (V)")
    ax.set_title(f"RC Step Response (τ ≈ {tau*1000:.2f} ms)")
    fig.tight_layout()

    return f"RC step solved (τ ≈ {tau*1000:.2f} ms)"
