"""
Optimization
============
Find the R1 value that maximises **or** minimises the voltage of a chosen
circuit node.

Parameters (dict, optional)
---------------------------
objective      : str   -> "max" (default) or "min"
target_node    : int   -> Node index (1-based) to observe      (default 1)
R1_min         : float -> Lower bound for R1 in ohms          (default 10 Ω)
R1_max         : float -> Upper bound for R1 in ohms          (default 1e4 Ω)
grid_points    : int   -> Plot helper: coarse sweep samples   (default 40)

Returns
-------
str : Text report summarising optimum R1 and corresponding voltage.

Author : Ugur C. (refactor-clean branch)
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar

from .linear_solver import parse_netlist, build_mna   # sibling helper imports


# ---------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------
def _replace_R1(net: str, new_val: float) -> str:
    """Return a new netlist where R1's value is substituted with *new_val*."""
    out, done = [], False
    for ln in net.strip().splitlines():
        if not done and ln.upper().startswith("R1 "):
            toks = ln.split()
            toks[-1] = f"{new_val:.6g}"
            ln = " ".join(toks)
            done = True
        out.append(ln)
    if not done:
        raise ValueError("Netlist must contain an element named 'R1'.")
    return "\n".join(out)


def _voltage_at_node(net: str, node: int) -> float:
    """Solve circuit and return voltage of *node* (1-based)."""
    G, I = build_mna(parse_netlist(net))
    V = np.linalg.solve(G, I)
    return float(V[node - 1])


# ---------------------------------------------------------------------
# Public entry – called by GUI
# ---------------------------------------------------------------------
def run(netlist_str: str, fig: plt.Figure, params: dict | None = None) -> str:
    # ------------------------ parameters -----------------------------
    p            = params or {}
    objective    = str(p.get("objective", "max")).lower()
    node         = int(p.get("target_node", 1))
    R_lo         = float(p.get("R1_min", 10.0))
    R_hi         = float(p.get("R1_max", 10_000.0))
    n_grid       = max(10, int(p.get("grid_points", 40)))

    if R_lo >= R_hi:
        return "[Optimization] R1_min must be < R1_max."

    # ---------------------- objective setup --------------------------
    sign = -1.0 if objective == "max" else +1.0   # minimise f = ±V → max/min
    def _f(R_val: float) -> float:
        V = _voltage_at_node(_replace_R1(netlist_str, R_val), node)
        return sign * V

    # --------------------- optimisation call -------------------------
    res = minimize_scalar(_f, bounds=(R_lo, R_hi), method="bounded")
    if not res.success:
        return f"[Optimization] SciPy failed: {res.message}"

    R_opt = float(res.x)
    V_opt = _voltage_at_node(_replace_R1(netlist_str, R_opt), node)

    # ----------------------- coarse sweep (plot) ---------------------
    grid_R = np.logspace(np.log10(R_lo), np.log10(R_hi), n_grid)
    grid_V = [_voltage_at_node(_replace_R1(netlist_str, r), node) for r in grid_R]

    # -------------------------- plot --------------------------------
    fig.clf()
    ax = fig.add_subplot(111)
    ax.semilogx(grid_R, grid_V, label=f"V(node {node})")
    ax.axvline(R_opt, ls="--", color="tab:red", label=f"R1 optimum ≈ {R_opt:.2f} Ω")
    ax.scatter([R_opt], [V_opt], color="tab:red")
    ax.set_xlabel("R1 (Ω)")
    ax.set_ylabel(f"V_node{node} (V)")
    ttl_obj = "Maximisation" if objective == "max" else "Minimisation"
    ax.set_title(f"{ttl_obj} of Node {node} Voltage")
    ax.grid(which="both", ls="--", alpha=0.3)
    ax.legend()
    fig.tight_layout()

    # -------------------------- report ------------------------------
    lines = [
        "[Optimization]",
        f"Objective          : {'Maximise' if objective=='max' else 'Minimise'} V_node{node}",
        f"Search range       : {R_lo:.1f} Ω – {R_hi:.1f} Ω",
        f"Optimal R1         : {R_opt:.3f} Ω",
        f"Voltage at optimum : {V_opt:.6f} V",
        f"SciPy iterations   : {res.nit}",
        f"Function evals     : {res.nfev}",
    ]
    return "\n".join(lines)
