"""
Performance Stats
-----------------
Direct vs LU çözümünün tek sefer süre ölçümü (ms) grafiği.
"""
import time, numpy as np
from scipy.linalg import lu_factor, lu_solve
from numerics.linear_solver import parse_netlist, build_mna


def run(netlist_str: str, fig, params=None):
    circ = parse_netlist(netlist_str)
    G, b, _ = build_mna(circ)

    t0 = time.perf_counter(); np.linalg.solve(G, b)
    d_ms = (time.perf_counter() - t0) * 1000
    t0 = time.perf_counter(); lu_solve(lu_factor(G), b)
    lu_ms = (time.perf_counter() - t0) * 1000

    fig.clf(); ax = fig.add_subplot(111)
    ax.bar(["Direct", "LU"], [d_ms, lu_ms])
    ax.set_ylabel("Time (ms)"); fig.tight_layout()

    return f"Direct: {d_ms:.3f} ms | LU: {lu_ms:.3f} ms"
