"""
Comparison module – Direct vs LU vs Iterative (CG→GMRES fallback).
Fix: plot only the first len(nodes) entries (node voltages), discard
extra rows holding source currents.
"""
import numpy as np
import scipy.sparse.linalg as spla
from scipy.linalg import lu_factor, lu_solve
from numerics.linear_solver import parse_netlist, build_mna

MAX_IT = 1000
TOL = 1e-10


def _cg(A, b):
    try:
        return spla.cg(A, b, tol=TOL, maxiter=MAX_IT)
    except TypeError:
        return spla.cg(A, b)


def _gmres(A, b):
    try:
        return spla.gmres(A, b, tol=TOL, restart=200, maxiter=MAX_IT)
    except TypeError:
        return spla.gmres(A, b)


def iterative_solve(A, b):
    v, info = _cg(A, b)
    if info == 0:
        return v, "CG"
    v, info = _gmres(A, b)
    if info != 0:
        raise RuntimeError(f"GMRES failed (info={info})")
    return v, "GMRES"


def run(netlist_str: str, fig):
    circ = parse_netlist(netlist_str)
    G, b, nodes = build_mna(circ)

    # Solve
    v_dir = np.linalg.solve(G, b)
    v_lu  = lu_solve(lu_factor(G), b)
    v_it, label = iterative_solve(G, b)

    # --- keep only node‐voltage part -------------------------------
    n = len(nodes)                  # node count (ground excluded)
    v_dir = v_dir[:n]
    v_lu  = v_lu[:n]
    v_it  = v_it[:n]

    # Plot
    fig.clf()
    ax = fig.add_subplot(111)
    idx = np.arange(n)
    ax.plot(idx, v_dir, "o-", label="Direct")
    ax.plot(idx, v_lu,  "x--", label="LU")
    ax.plot(idx, v_it,  "s:", label=label)
    ax.set_xlabel("Node index")
    ax.set_ylabel("Voltage [V]")
    ax.set_title(f"Node Voltages – Direct vs LU vs {label}")
    ax.legend()
    fig.tight_layout()

    max_dev = np.max(np.abs(v_dir - v_it))
    return f"Max |Direct – {label}| = {max_dev:.2e} V"
