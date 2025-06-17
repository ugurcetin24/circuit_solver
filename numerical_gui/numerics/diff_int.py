"""
Diff / Integral
---------------
dV1/dR1 eğrisini çizer, ∫V1 dR1 değerini raporlar.
Parametre: R1_min, R1_max
"""
import numpy as np
from numerics.linear_solver import parse_netlist, build_mna


def _v1(net, R1):
    done, out = False, []
    for ln in net.strip().splitlines():
        if not done and ln.upper().startswith("R1"):
            p = ln.split(); p[-1] = str(R1); ln = " ".join(p); done = True
        out.append(ln)
    circ = parse_netlist("\n".join(out))
    G, b, nodes = build_mna(circ)
    return float(np.linalg.solve(G, b)[nodes.index(1)])


def run(netlist_str: str, fig, params=None):
    p = params or {}
    R_lo = p.get("R1_min", 10.0)
    R_hi = p.get("R1_max", 10_000.0)

    r = np.linspace(R_lo, R_hi, 40)
    v = np.array([_v1(netlist_str, x) for x in r])
    dv = np.gradient(v, r)
    area = np.trapz(v, r)

    fig.clf(); ax = fig.add_subplot(111)
    ax.plot(r, dv); ax.set_xlabel("R1 (Ω)"); ax.set_ylabel("dV1/dR1")
    ax.set_title("Numerical derivative dV1/dR1"); fig.tight_layout()

    return f"Integral ∫V1 dR1 ≈ {area:.3f} V·Ω"
