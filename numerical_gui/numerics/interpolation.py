"""
Interpolation
-------------
Sample the circuit’s response (node voltage) versus R1, then fit a
CubicSpline so we can estimate voltage for *any* R1 in the range.

Parameters (dict, optional)
---------------------------
target_node : int   -> Node index (1-based) to monitor       (default 1)
R1_min      : float -> Lower bound for R1 in ohms           (default 10 Ω)
R1_max      : float -> Upper bound for R1 in ohms           (default 1e4 Ω)
samples     : int   -> Number of sampling points            (default 10)

Returns
-------
str : Text report containing basic interpolation error metrics.

Author : Ugur C. (refactor-clean branch)
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

# sibling import – shared helpers
from .linear_solver import parse_netlist, build_mna


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------
def _patch_R1(net: str, new_val: float) -> str:
    """Replace the last token of the R1 line with *new_val* (in ohms)."""
    out, done = [], False
    for ln in net.strip().splitlines():
        if not done and ln.upper().startswith("R1"):
            toks = ln.split()
            toks[-1] = f"{new_val:.6g}"
            ln = " ".join(toks)
            done = True
        out.append(ln)
    if not done:
        raise ValueError("Netlist must contain element named 'R1'.")
    return "\n".join(out)


def _node_voltage(net: str, node: int) -> float:
    """Return voltage at *node* (1-based) after solving the circuit."""
    G, I = build_mna(parse_netlist(net))
    V = np.linalg.solve(G, I)
    return float(V[node - 1])


# ---------------------------------------------------------------------
# Public entry
# ---------------------------------------------------------------------
def run(netlist_str: str, fig: plt.Figure, params: dict | None = None) -> str:
    # -- Parse parameters ------------------------------------------------
    p           = params or {}
    node        = int(p.get("target_node", 1))
    R_lo        = float(p.get("R1_min", 10.0))
    R_hi        = float(p.get("R1_max", 10_000.0))
    n_samples   = int(p.get("samples", 10))
    if n_samples < 4:
        n_samples = 4   # CubicSpline needs at least 4 points

    # -- Sample circuit response ----------------------------------------
    Rs   = np.linspace(R_lo, R_hi, n_samples)
    Vs   = np.array([_node_voltage(_patch_R1(netlist_str, r), node) for r in Rs])

    # -- Fit Cubic Spline ------------------------------------------------
    spline = CubicSpline(Rs, Vs)
    Rs_dense = np.logspace(np.log10(R_lo), np.log10(R_hi), 200)
    Vs_dense = spline(Rs_dense)

    # -- Simple error estimate (leave-one-out) --------------------------
    errs = []
    for i in range(n_samples):
        mask   = np.arange(n_samples) != i
        spl_i  = CubicSpline(Rs[mask], Vs[mask])
        errs.append(abs(spl_i(Rs[i]) - Vs[i]))
    rms_err = float(np.sqrt(np.mean(np.square(errs))))

    # -- Plot ------------------------------------------------------------
    fig.clf()
    ax = fig.add_subplot(111)
    ax.semilogx(Rs_dense, Vs_dense, label="Cubic spline")
    ax.scatter(Rs, Vs, color="tab:red", zorder=5, label="Samples")
    ax.set_xlabel("R1 (Ω)")
    ax.set_ylabel(f"V_node{node} (V)")
    ax.set_title("Voltage vs R1 – Cubic Spline Interpolation")
    ax.grid(which="both", ls="--", alpha=0.3)
    ax.legend()
    fig.tight_layout()

    # -- Text report -----------------------------------------------------
    lines = [
        "[Interpolation]",
        f"Target node            : {node}",
        f"R1 range               : {R_lo:.1f} Ω – {R_hi:.1f} Ω",
        f"Samples used           : {n_samples}",
        f"RMS leave-one-out error: {rms_err:.3e} V",
    ]
    return "\n".join(lines)
