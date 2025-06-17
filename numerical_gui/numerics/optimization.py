"""
Optimization module – finds the R1 value that minimizes power dissipation
(on R1 itself) using bounded scalar minimization.

Definition
----------
Power on R1:  P(R1) = I_R1^2 * R1.
Current through R1 is (V1 - V2) / R1, but since V1 is fixed at 10 V and
V2 depends on the divider, we compute it numerically via circuit solve.
"""

import numpy as np
from scipy.optimize import minimize_scalar
from numerics.linear_solver import parse_netlist, build_mna   # reuse helpers


# --------------------------------------------------------------------------- #
def _power_on_R1(netlist_str: str, r_value: float) -> float:
    """Return power (W) dissipated on R1 when its value = r_value (Ω)."""
    # Replace R1 value in a copy of the netlist
    lines, swapped = [], False
    for ln in netlist_str.strip().splitlines():
        if not swapped and ln.upper().startswith("R1"):
            parts = ln.split()
            parts[-1] = str(r_value)
            ln = " ".join(parts)
            swapped = True
        lines.append(ln)

    circ = parse_netlist("\n".join(lines))
    G, b, nodes = build_mna(circ)
    v = np.linalg.solve(G, b)

    # Current through R1 = (V1 - V2) / R1  (node-1 idx = 1, node-2 idx = 2)
    v1, v2 = v[nodes.index(1)], v[nodes.index(2)]
    i_r1 = (v1 - v2) / r_value
    p_r1 = (i_r1 ** 2) * r_value
    return float(p_r1)


# --------------------------------------------------------------------------- #
def run(netlist_str: str, fig):
    """
    GUI hook – minimizes _power_on_R1 over R1 ∈ [R_min, R_max],
    no plot required; returns textual summary.
    """
    R_min, R_max = 1.0, 50_000.0     # Ω – adjust if needed

    result = minimize_scalar(
        lambda R: _power_on_R1(netlist_str, R),
        bounds=(R_min, R_max),
        method="bounded",
        options={"xatol": 1e-2}       # ±0.01 Ω tolerance
    )

    if not result.success:
        return "Optimization failed: SciPy did not converge."

    opt_R  = result.x
    opt_P  = result.fun

    return (f"Optimal R1 ≈ {opt_R:.2f} Ω  →  "
            f"Power dissipation ≈ {opt_P:.4f} W")
