"""
Optimization
------------
R1'in gücünü minimize eder (SciPy minimize_scalar, bounded).
Parametre: R1_min, R1_max
"""
import numpy as np
from scipy.optimize import minimize_scalar
from numerics.linear_solver import parse_netlist, build_mna


def _power(net, R1):
    done, lines = False, []
    for ln in net.strip().splitlines():
        if not done and ln.upper().startswith("R1"):
            p = ln.split(); p[-1] = str(R1); ln = " ".join(p); done = True
        lines.append(ln)
    circ = parse_netlist("\n".join(lines))
    G, b, nodes = build_mna(circ)
    v = np.linalg.solve(G, b)
    v1, v2 = v[nodes.index(1)], v[nodes.index(2)]
    i = (v1 - v2) / R1
    return i**2 * R1


def run(netlist_str: str, fig, params=None):
    p = params or {}
    lo = p.get("R1_min", 1.0)
    hi = p.get("R1_max", 50_000.0)

    res = minimize_scalar(lambda R: _power(netlist_str, R),
                          bounds=(lo, hi), method="bounded",
                          options={"xatol": 1e-2})
    if not res.success:
        return "Optimization failed"
    return f"Optimal R1 ≈ {res.x:.2f} Ω → P ≈ {res.fun:.4f} W"
