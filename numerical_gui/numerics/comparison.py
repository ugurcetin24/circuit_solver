"""
Comparison
----------
Direct, LU ve CG→(fallback) GMRES çözümlerini karşılaştırır,
SPD olmayan/legacy SciPy durumlarına uyumludur.
"""
import numpy as np, scipy.sparse.linalg as spla
from scipy.linalg import lu_factor, lu_solve
from numerics.linear_solver import parse_netlist, build_mna

TOL, MAX_IT = 1e-10, 1000


def _cg(A, b):
    try:  return spla.cg(A, b, tol=TOL, maxiter=MAX_IT)
    except TypeError:  return spla.cg(A, b)


def _gmres(A, b):
    try:  return spla.gmres(A, b, tol=TOL, restart=200, maxiter=MAX_IT)
    except TypeError:  return spla.gmres(A, b)


def _iterative(A, b):
    v, info = _cg(A, b)
    if info == 0: return v, "CG"
    v, info = _gmres(A, b)
    if info != 0: raise RuntimeError(f"GMRES failed (info={info})")
    return v, "GMRES"


def run(netlist_str: str, fig, params=None):
    circ = parse_netlist(netlist_str)
    G, b, nodes = build_mna(circ)

    v_dir = np.linalg.solve(G, b)
    v_lu  = lu_solve(lu_factor(G), b)
    v_it, label = _iterative(G, b)

    n = len(nodes)
    v_dir, v_lu, v_it = v_dir[:n], v_lu[:n], v_it[:n]

    fig.clf(); ax = fig.add_subplot(111)
    k = np.arange(n)
    ax.plot(k, v_dir, "o-", label="Direct")
    ax.plot(k, v_lu,  "x--", label="LU")
    ax.plot(k, v_it,  "s:", label=label)
    ax.set_xlabel("Node"); ax.set_ylabel("V (V)")
    ax.set_title(f"Node Voltages – Direct vs LU vs {label}")
    ax.legend(); fig.tight_layout()

    dev = np.max(np.abs(v_dir - v_it))
    return f"Max |Direct – {label}| = {dev:.2e} V"
