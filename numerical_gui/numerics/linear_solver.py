"""
Linear Solver
-------------
Çözümün yanı sıra |G| matrisini ısı haritası olarak çizdirir.
Bu dosya ortak *parse_netlist* ve *build_mna* fonksiyonlarını EXPORT eder;
diğer modüller buradan import eder.

Parametre: yok
"""
import numpy as np
from circuit.circuit_solver import Circuit


# -------- helper: parse netlist into Circuit ------------------------------- #
def parse_netlist(net: str) -> Circuit:
    circ = Circuit()
    for ln in net.strip().splitlines():
        t = ln.split()
        if len(t) != 4:
            continue
        name, n1, n2, val = t
        n1, n2 = int(n1), int(n2)
        val = float(val)
        if name.upper().startswith("R"):
            circ.add_resistor(name, n1, n2, val)
        elif name.upper().startswith("V"):
            circ.add_voltage_source(name, n1, n2, val)
        elif name.upper().startswith("I"):
            circ.add_current_source(name, n1, n2, val)
    return circ


# -------- helper: build Modified Nodal Matrix ------------------------------ #
def build_mna(circ: Circuit):
    nodes = {c["node1"] for c in circ.components} | {c["node2"] for c in circ.components}
    nodes.discard(0)
    n_list = sorted(nodes)
    idx = {n: i for i, n in enumerate(n_list)}
    n = len(n_list)

    vsrc = [c for c in circ.components if c["type"] == "voltage_source"]
    m = len(vsrc)

    A = np.zeros((n + m, n + m))
    b = np.zeros(n + m)

    # Passive elements & sources
    vs_row = 0
    for comp in circ.components:
        n1, n2, val = comp["node1"], comp["node2"], comp["value"]

        if comp["type"] == "resistor":
            g = 1 / val
            if n1 != 0:
                i = idx[n1]; A[i, i] += g
            if n2 != 0:
                j = idx[n2]; A[j, j] += g
            if n1 and n2:
                i, j = idx[n1], idx[n2]
                A[i, j] -= g
                A[j, i] -= g

        elif comp["type"] == "current_source":
            if n1:
                i = idx[n1]; b[i] -= val
            if n2:
                j = idx[n2]; b[j] += val

    # Voltage sources
    for vs in vsrc:
        n1, n2, v = vs["node1"], vs["node2"], vs["value"]
        row = n + vs_row
        if n1:
            i = idx[n1]; A[row, i] = A[i, row] = 1
        if n2:
            j = idx[n2]; A[row, j] = A[j, row] = -1
        b[row] = v
        vs_row += 1

    return A, b, n_list


# --------------------------------------------------------------------------- #
def run(netlist_str: str, fig, params=None):
    params = params or {}
    circ = parse_netlist(netlist_str)
    G, i_vec, _ = build_mna(circ)
    v = np.linalg.solve(G, i_vec)

    fig.clf()
    ax = fig.add_subplot(111)
    ax.imshow(np.abs(G), origin="upper", aspect="auto")
    ax.set_title("‖G‖ Conductance-Matrix Heat-map")
    fig.tight_layout()

    txt = ", ".join([f"{val:.3f} V" for val in v[:len(circ.nodes)-1]])
    return f"Node voltages: {txt}"
