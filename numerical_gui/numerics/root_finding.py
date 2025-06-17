"""
Root Finding
------------
R1 aralığında V_target gerilimini sağlayan değeri biseksiyonla bulur
(panel parametreleri: R1_min, R1_max, V_target).
"""
import numpy as np
from numerics.linear_solver import parse_netlist, build_mna

MAX_ITER, TOL = 30, 1e-3


def _voltage(net, R1, node=2):
    lines, done = [], False
    for ln in net.strip().splitlines():
        if not done and ln.upper().startswith("R1"):
            p = ln.split(); p[-1] = str(R1); ln = " ".join(p); done = True
        lines.append(ln)
    circ = parse_netlist("\n".join(lines))
    G, b, nodes = build_mna(circ)
    v = np.linalg.solve(G, b)
    return float(v[nodes.index(node)])


def run(netlist_str: str, fig, params=None):
    params = params or {}
    R_lo = params.get("R1_min", 10.0)
    R_hi = params.get("R1_max", 10_000.0)
    V_t  = params.get("V_target", 5.0)

    f_lo = _voltage(netlist_str, R_lo) - V_t
    f_hi = _voltage(netlist_str, R_hi) - V_t
    if f_lo * f_hi > 0:
        return "Bisection failed: change R range or V_target."

    for _ in range(MAX_ITER):
        R_mid = 0.5 * (R_lo + R_hi)
        V_mid = _voltage(netlist_str, R_mid)
        f_mid = V_mid - V_t
        if abs(f_mid) < TOL:
            break
        if f_lo * f_mid < 0:
            R_hi, f_hi = R_mid, f_mid
        else:
            R_lo, f_lo = R_mid, f_mid

    return f"R1 ≈ {R_mid:.2f} Ω → V2 ≈ {V_mid:.3f} V (target {V_t} V)"
