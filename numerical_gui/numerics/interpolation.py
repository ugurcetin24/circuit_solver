"""
Interpolation module – samples node-1 voltage versus R1 value, then builds
a cubic spline and plots both the raw points and the smooth curve.

Assumptions
-----------
* The first resistor line in the netlist starts with "R1".
* We vary R1 while all other elements stay constant.
"""

import numpy as np
from scipy.interpolate import CubicSpline
from numerics.linear_solver import parse_netlist, build_mna   # reuse helpers


# --------------------------------------------------------------------------- #
def _v1_given_R(netlist_str: str, r_value: float) -> float:
    """Return node-1 voltage when R1 = r_value (Ω)."""
    lines = []
    done = False
    for ln in netlist_str.strip().splitlines():
        if not done and ln.upper().startswith("R1"):
            parts = ln.split()
            parts[-1] = str(r_value)
            ln = " ".join(parts)
            done = True
        lines.append(ln)
    circ = parse_netlist("\n".join(lines))
    G, b, nodes = build_mna(circ)
    v = np.linalg.solve(G, b)
    return float(v[nodes.index(1)])          # node-1 is index 1 in nodes list


# --------------------------------------------------------------------------- #
def run(netlist_str: str, fig):
    """
    Called by GUI when 'Interpolation' button is pressed.
    Draws scatter points (sampled V1) and cubic-spline curve.
    """
    # ---- sample data -------------------------------------------------------
    R_min, R_max, N = 10.0, 10_000.0, 12          # Ω
    r_vals = np.linspace(R_min, R_max, N)
    v_vals = np.array([_v1_given_R(netlist_str, R) for R in r_vals])

    # ---- cubic spline fit --------------------------------------------------
    spline = CubicSpline(r_vals, v_vals)
    r_dense = np.linspace(R_min, R_max, 300)
    v_dense = spline(r_dense)

    # ---- plot --------------------------------------------------------------
    fig.clf()
    ax = fig.add_subplot(111)
    ax.plot(r_vals, v_vals, "o", label="samples")
    ax.plot(r_dense, v_dense, "-", label="cubic spline")
    ax.set_xlabel("R1 (Ω)")
    ax.set_ylabel("V1 (V)")
    ax.set_title("V1 vs R1 – cubic spline")
    ax.legend()
    fig.tight_layout()

    return "Cubic spline drawn for V1(R1)"
