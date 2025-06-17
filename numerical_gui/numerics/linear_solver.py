"""
Linear Solver module – constructs the MNA matrix G and RHS vector i,
solves G·v = i, and visualises |G| as a heat-map.
"""
import numpy as np
from circuit.circuit_solver import Circuit

# ------------------------------------------------------------------ #
def parse_netlist(netlist_str: str) -> Circuit:
    circuit = Circuit()
    for line in netlist_str.strip().splitlines():
        parts = line.split()
        if len(parts) != 4:
            continue
        name, n1, n2, val = parts
        n1, n2 = int(n1), int(n2)
        val = float(val)
        if name.upper().startswith("R"):
            circuit.add_resistor(name, n1, n2, val)
        elif name.upper().startswith("V"):
            circuit.add_voltage_source(name, n1, n2, val)
        elif name.upper().startswith("I"):
            circuit.add_current_source(name, n1, n2, val)
    return circuit


def build_mna(circuit: Circuit):
    """
    Re-creates the MNA matrix (A) and RHS vector (b) using the same
    algorithm in Circuit.solve_nodal(), but returns them for inspection.
    """
    nodes = set()
    v_sources = []
    for comp in circuit.components:
        nodes.update([comp["node1"], comp["node2"]])
        if comp["type"] == "voltage_source":
            v_sources.append(comp)

    nodes.discard(0)                     # ground
    n_list = sorted(nodes)
    idx = {node: i for i, node in enumerate(n_list)}
    n = len(n_list)
    m = len(v_sources)

    A = np.zeros((n + m, n + m))
    b = np.zeros(n + m)

    v_idx = 0
    for comp in circuit.components:
        n1, n2, val = comp["node1"], comp["node2"], comp["value"]

        if comp["type"] == "resistor":
            g = 1 / val
            if n1 != 0:
                i = idx[n1]; A[i, i] += g
            if n2 != 0:
                j = idx[n2]; A[j, j] += g
            if n1 != 0 and n2 != 0:
                i, j = idx[n1], idx[n2]
                A[i, j] -= g
                A[j, i] -= g

        elif comp["type"] == "current_source":
            if n1 != 0:
                i = idx[n1]; b[i] -= val
            if n2 != 0:
                j = idx[n2]; b[j] += val

    for vs in v_sources:
        n1, n2, vv = vs["node1"], vs["node2"], vs["value"]
        row = n + v_idx
        if n1 != 0:
            i = idx[n1]; A[row, i] = A[i, row] = 1
        if n2 != 0:
            j = idx[n2]; A[row, j] = A[j, row] = -1
        b[row] = vv
        v_idx += 1

    return A, b, n_list


# ------------------------------------------------------------------ #
def run(netlist_str: str, fig):
    """
    Triggered by the 'Linear Solver' button.
    """
    circuit = parse_netlist(netlist_str)
    G, i_vec, nodes = build_mna(circuit)
    voltages = np.linalg.solve(G, i_vec)

    # ----------- heat-map of |G| -----------
    fig.clf()
    ax = fig.add_subplot(111)
    cax = ax.imshow(np.abs(G), origin="upper", aspect="auto")
    ax.set_title("‖G‖ Conductance-Matrix Heat-map")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    fig.colorbar(cax, ax=ax, shrink=0.8)
    fig.tight_layout()

    # ----------- textual output ------------
    txt = ", ".join([f"V{n}={voltages[i]:.3f} V" for i, n in enumerate(nodes)])
    return f"Node voltages: {txt}"
