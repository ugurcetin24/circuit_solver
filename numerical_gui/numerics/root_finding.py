"""
Root-Finding module – adjusts R1 so that node-2 voltage reaches a target value
using the bisection method.

Workflow
--------
1. Replace R1's value in the netlist with a test value.
2. Solve the circuit (reuse helpers from linear_solver).
3. Compute f(R) = V_target – V2(R).
4. Apply bisection until |f(R)| < TOL.
"""
import numpy as np
from numerics.linear_solver import parse_netlist, build_mna   # helper funcs

TARGET_NODE = 2          # node whose voltage we control
TARGET_V   = 5.0         # desired voltage at that node  (V)
TOL        = 1e-3        # acceptable voltage error     (V)
MAX_ITER   = 30          # max bisection iterations
R_MIN, R_MAX = 1.0, 1e5  # initial bracket for R1 (Ω)


# --------------------------------------------------------------------------- #
def _node_voltage(netlist: str, r_value: float) -> float:
    """Return V(TARGET_NODE) when R1 = <r_value> Ω."""
    new_lines = []
    substituted = False
    for ln in netlist.strip().splitlines():
        if not substituted and ln.upper().startswith("R1"):
            parts = ln.split()
            parts[-1] = str(r_value)
            ln = " ".join(parts)
            substituted = True
        new_lines.append(ln)

    updated_net = "\n".join(new_lines)
    circ = parse_netlist(updated_net)
    G, b, nodes = build_mna(circ)
    v = np.linalg.solve(G, b)
    return float(v[nodes.index(TARGET_NODE)])


# --------------------------------------------------------------------------- #
def run(netlist_str: str, fig):
    """
    GUI entry point – performs bisection on R1 until V₂ ≈ TARGET_V.
    Returns a textual report; no plot is generated.
    """
    # Evaluate function at bracket ends
    f_min = _node_voltage(netlist_str, R_MIN) - TARGET_V
    f_max = _node_voltage(netlist_str, R_MAX) - TARGET_V

    if f_min * f_max > 0:
        return ("Bisection failed: target voltage is not bracketed.\n"
                "Try widening R_MIN/R_MAX or picking another TARGET_V.")

    r_lo, r_hi = R_MIN, R_MAX
    f_lo, f_hi = f_min, f_max

    for _ in range(MAX_ITER):
        r_mid = 0.5 * (r_lo + r_hi)
        v_mid = _node_voltage(netlist_str, r_mid)
        f_mid = v_mid - TARGET_V

        if abs(f_mid) < TOL:
            break

        # Update bracket
        if f_lo * f_mid < 0:        # root in [r_lo, r_mid]
            r_hi, f_hi = r_mid, f_mid
        else:                       # root in [r_mid, r_hi]
            r_lo, f_lo = r_mid, f_mid

    return (f"Bisection result: R1 ≈ {r_mid:.2f} Ω  "
            f"gives V2 ≈ {v_mid:.3f} V  (target {TARGET_V} V)")
