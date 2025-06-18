"""
Differentiation & Integration
=============================
Compute the numerical derivative (dV/dR1) and the integral (∫V dR1)
for a chosen circuit node as R1 sweeps between two bounds.

Parameters (dict, optional)
---------------------------
target_node : int   -> Node index (1-based) to analyse  (default 1)
R1_min      : float -> Lower bound for R1 in ohms      (default 10 Ω)
R1_max      : float -> Upper bound for R1 in ohms      (default 1e4 Ω)
samples     : int   -> Number of sampling points       (default 50)

Returns
-------
str : Text report including average derivative and total integral.

Author : Ugur C. (refactor-clean branch)
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumulative_trapezoid

from .linear_solver import parse_netlist, build_mna   # sibling import

# ---------------------------------------------------------------------
# Helper – patch R1 in netlist
# ---------------------------------------------------------------------
def _replace_R1(net: str, new_val: float) -> str:
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


def _solve_node_voltage(net: str, node: int) -> float:
    G, I = build_mna(parse_netlist(net))
    V = np.linalg.solve(G, I)
    return float(V[node - 1])        # node index 1-based


# ---------------------------------------------------------------------
# Public entry – GUI calls run()
# ---------------------------------------------------------------------
def run(netlist_str: str, fig: plt.Figure, params: dict | None = None) -> str:
    # ----------------------- parameters ------------------------------
    p         = params or {}
    node      = int(p.get("target_node", 1))
    R_low     = float(p.get("R1_min", 10.0))
    R_high    = float(p.get("R1_max", 10_000.0))
    N         = max(5, int(p.get("samples", 50)))   # at least 5 points

    Rs = np.linspace(R_low, R_high, N)
    Vs = np.array([_solve_node_voltage(_replace_R1(netlist_str, r), node) for r in Rs])

    # --------------------- differentiation ---------------------------
    dV_dR = np.gradient(Vs, Rs)          # central diff internally

    # ----------------------- integration -----------------------------
    # cumulative integral so it aligns with Rs[1:]
    int_V = cumulative_trapezoid(Vs, Rs, initial=0.0)

    avg_slope = float(np.mean(dV_dR))
    total_int = float(int_V[-1])

    # ------------------------- plot ----------------------------------
    fig.clf()
    ax1 = fig.add_subplot(111)
    ax1.plot(Rs, Vs, label="V(R1)")
    ax1.set_xlabel("R1 (Ω)")
    ax1.set_ylabel(f"V_node{node} (V)", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")
    ax1.grid(alpha=0.3, ls="--")

    # Second y-axis for integral
    ax2 = ax1.twinx()
    ax2.plot(Rs, int_V, color="tab:orange", label="∫V dR1")
    ax2.set_ylabel("Integral [V·Ω]", color="tab:orange")
    ax2.tick_params(axis="y", labelcolor="tab:orange")

    # combine legends
    lines, labels = [], []
    for ax in (ax1, ax2):
        line_objs, lbls = ax.get_legend_handles_labels()
        lines.extend(line_objs); labels.extend(lbls)
    ax1.legend(lines, labels, loc="upper right")

    ax1.set_title("Numerical Differentiation & Integration")
    fig.tight_layout()

    # ------------------------- report -------------------------------
    lines = [
        "[Differentiation / Integration]",
        f"Target node        : {node}",
        f"R1 range           : {R_low:.1f} Ω – {R_high:.1f} Ω",
        f"Sampling points    : {N}",
        f"Average dV/dR      : {avg_slope:.3e} V/Ω",
        f"Total ∫V dR1       : {total_int:.3e} V·Ω",
    ]
    return "\n".join(lines)
