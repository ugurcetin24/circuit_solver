"""
Comparison of Solvers
---------------------
Solve G · x = I using:
  1) Direct   (numpy.linalg.solve)
  2) LU       (scipy.linalg.lu_solve)
  3) CG       (scipy.sparse.linalg.cg)

Reports iteration count & error norms, plots bar chart of runtimes.

Parameters
----------
tol : float -> CG tolerance (default 1e-10)

Returns
-------
str : Table of time (ms) & residuals.

Author : Ugur C. (refactor-clean branch)
"""
from __future__ import annotations

import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import lu_factor, lu_solve
from scipy.sparse.linalg import cg

from .linear_solver import parse_netlist, build_mna  # sibling helpers


# ----------------------------------------------------------------------
# Timing helpers
# ----------------------------------------------------------------------
_now_ms = lambda: time.perf_counter() * 1e3


def _solve_direct(G, I):
    return np.linalg.solve(G, I)


def _solve_lu(G, I):
    lu, piv = lu_factor(G)
    return lu_solve((lu, piv), I)


# ----------------------------------------------------------------------
# Public entry
# ----------------------------------------------------------------------
def run(netlist_str: str, fig: plt.Figure, params: dict | None = None) -> str:
    p = params or {}
    tol = float(p.get("tol", 1e-10))

    G, I = build_mna(parse_netlist(netlist_str))

    # --- Direct -------------------------------------------------------
    t0 = _now_ms()
    x_direct = _solve_direct(G, I)
    t_direct = _now_ms() - t0

    # --- LU -----------------------------------------------------------
    t0 = _now_ms()
    x_lu = _solve_lu(G, I)
    t_lu = _now_ms() - t0

    # --- Conjugate Gradient ------------------------------------------
    t0 = _now_ms()
    x_cg, _ = cg(G, I, tol=tol, maxiter=10_000)
    t_cg = _now_ms() - t0

    residual = lambda x: np.linalg.norm(G @ x - I)

    # ----------------------------- Plot ------------------------------
    fig.clf()
    ax = fig.add_subplot(111)
    bars = ["Direct", "LU", "CG"]
    times = [t_direct, t_lu, t_cg]
    ax.bar(bars, times, color=["tab:blue", "tab:green", "tab:orange"])
    ax.set_ylabel("Time (ms)")
    ax.set_title("Solver Comparison")

    # Annotate bars
    for i, v in enumerate(times):
        ax.text(i, v, f"{v:.1f}", ha="center", va="bottom")

    fig.tight_layout()

    # --------------------------- Report ------------------------------
    lines = [
        "[Comparison]",
        f"{'Method':<10}{'Time (ms)':>12}{'Residual':>14}",
        "-" * 36,
        f"{'Direct':<10}{t_direct:12.2f}{residual(x_direct):14.3e}",
        f"{'LU':<10}{t_lu:12.2f}{residual(x_lu):14.3e}",
        f"{'CG':<10}{t_cg:12.2f}{residual(x_cg):14.3e}",
    ]
    return "\n".join(lines)
