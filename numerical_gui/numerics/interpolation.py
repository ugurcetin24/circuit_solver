"""
Interpolation
-------------
R1_min–R1_max aralığında V1(R1) örnekler, kubik spline çizer.
Panele bağlı parametre: R1_min, R1_max
"""
import numpy as np
from scipy.interpolate import CubicSpline
from numerics.linear_solver import parse_netlist, build_mna


def _v1(net, R1):
    done, lines = False, []
    for ln in net.strip().splitlines():
        if not done and ln.upper().startswith("R1"):
            p = ln.split(); p[-1] = str(R1); ln = " ".join(p); done = True
        lines.append(ln)
    circ = parse_netlist("\n".join(lines))
    G, b, nodes = build_mna(circ)
    return float(np.linalg.solve(G, b)[nodes.index(1)])


def run(netlist_str: str, fig, params=None):
    p = params or {}
    R_lo = p.get("R1_min", 10.0)
    R_hi = p.get("R1_max", 10_000.0)

    r = np.linspace(R_lo, R_hi, 12)
    v = np.array([_v1(netlist_str, x) for x in r])
    cs = CubicSpline(r, v)

    fig.clf()
    ax = fig.add_subplot(111)
    ax.plot(r, v, "o", label="samples")
    r_d = np.linspace(R_lo, R_hi, 300)
    ax.plot(r_d, cs(r_d), "-", label="spline")
    ax.set_xlabel("R1 (Ω)")
    ax.set_ylabel("V1 (V)")
    ax.legend(); fig.tight_layout()

    return "Cubic spline drawn"
