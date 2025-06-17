"""
Performance / Stability module – measures solution time for two methods:

    • Direct solve        -> numpy.linalg.solve
    • LU factorisation    -> scipy.linalg.lu_factor + lu_solve

and displays the timings in a bar chart (milliseconds).
"""

import time
import numpy as np
from scipy.linalg import lu_factor, lu_solve
from numerics.linear_solver import parse_netlist, build_mna   # reuse helpers


# --------------------------------------------------------------------------- #
def run(netlist_str: str, fig):
    """
    GUI entry – times each method once (cold run) and plots bar chart.
    """
    # Build MNA matrix & RHS once
    circuit = parse_netlist(netlist_str)
    G, b, _ = build_mna(circuit)

    # --- Direct solver ------------------------------------------------------
    t0 = time.perf_counter()
    _ = np.linalg.solve(G, b)
    direct_ms = (time.perf_counter() - t0) * 1000.0

    # --- LU factorisation ---------------------------------------------------
    t0 = time.perf_counter()
    lu_piv = lu_factor(G)
    _ = lu_solve(lu_piv, b)
    lu_ms = (time.perf_counter() - t0) * 1000.0

    # --- Plot ----------------------------------------------------------------
    fig.clf()
    ax = fig.add_subplot(111)
    methods = ["Direct", "LU"]
    times   = [direct_ms, lu_ms]
    ax.bar(methods, times, color=["tab:blue", "tab:orange"])
    ax.set_ylabel("Time  [ms]")
    ax.set_title("Solver Performance (single run)")
    for i, t in enumerate(times):
        ax.text(i, t + 0.02 * max(times), f"{t:.3f} ms", ha="center", va="bottom")
    fig.tight_layout()

    return f"Direct: {direct_ms:.3f} ms   |   LU: {lu_ms:.3f} ms"
