"""
Performance Benchmark
---------------------
Time direct solve (numpy.linalg.solve) vs LU solve
(scipy.linalg.lu_factor/lu_solve) on the same G matrix.

Returns
-------
str : timing tabloları (ms) ve hız oranı.
"""
from __future__ import annotations
import time, numpy as np, matplotlib.pyplot as plt
from scipy.linalg import lu_factor, lu_solve
from .linear_solver import parse_netlist, build_mna

def _timeit(fn, *a):
    t0 = time.perf_counter(); fn(*a); return (time.perf_counter()-t0)*1e3  # ms

def run(net, fig, params=None):
    G, I = build_mna(parse_netlist(net))

    t_direct = _timeit(np.linalg.solve, G, I)
    lu, piv  = lu_factor(G)
    t_lu     = _timeit(lu_solve, (lu, piv), I)
    speedup  = t_direct / t_lu if t_lu else float("inf")

    # Bar chart
    fig.clf(); ax = fig.add_subplot(111)
    ax.bar(["Direct", "LU"], [t_direct, t_lu], color=["tab:blue","tab:green"])
    ax.set_ylabel("Time (ms)"); ax.set_title("Solver Performance")
    for i, v in enumerate([t_direct, t_lu]): ax.text(i, v, f"{v:.1f}", ha="center", va="bottom")
    fig.tight_layout()

    return (f"[Performance]\nDirect solve : {t_direct:.2f} ms\n"
            f"LU solve     : {t_lu:.2f} ms\n"
            f"Speed-up     : ×{speedup:.2f}")
