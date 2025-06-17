"""
Diff / Integral module – computes numerical derivative dV1/dR1 and
integral ∫ V1 dR1 over a user-defined R1 range, then plots the derivative.
"""

import numpy as np
from numerics.linear_solver import parse_netlist, build_mna   # reuse helpers


# --------------------------------------------------------------------------- #
def _v1_given_R(netlist_str: str, r_value: float) -> float:
    """Return node-1 voltage when R1 = r_value (Ω)."""
    lines, replaced = [], False
    for ln in netlist_str.strip().splitlines():
        if not replaced and ln.upper().startswith("R1"):
            parts = ln.split()
            parts[-1] = str(r_value)
            ln = " ".join(parts)
            replaced = True
        lines.append(ln)
    circ = parse_netlist("\n".join(lines))
    G, b, nodes = build_mna(circ)
    v = np.linalg.solve(G, b)
    return float(v[nodes.index(1)])


# --------------------------------------------------------------------------- #
def run(netlist_str: str, fig):
    """
    GUI entry – draws dV1/dR1 curve and returns integral value.
    """
    R_min, R_max, N = 10.0, 10_000.0, 40        # Ω
    r_vals = np.linspace(R_min, R_max, N)
    v_vals = np.array([_v1_given_R(netlist_str, R) for R in r_vals])

    # Numerical derivative (central diff via np.gradient)
    dv_dR = np.gradient(v_vals, r_vals)

    # Numerical integral (trapezoidal rule)
    area = np.trapz(v_vals, r_vals)

    # ---- plot derivative ---------------------------------------------------
    fig.clf()
    ax = fig.add_subplot(111)
    ax.plot(r_vals, dv_dR)
    ax.set_xlabel("R1 (Ω)")
    ax.set_ylabel("dV1/dR1  (V/Ω)")
    ax.set_title("Numerical derivative  dV1/dR1")
    fig.tight_layout()

    return f"∫ V1 dR1 ≈ {area:.3f}  (V·Ω)  over {R_min}–{R_max} Ω"
