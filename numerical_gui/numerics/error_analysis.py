"""
Error Analysis
--------------
Adds ±0.5 % sentetik gürültüyle node gerilimlerinin göreli hatasını
grafik olarak gösterir.

Parametre: yok
"""
import numpy as np
from circuit.circuit_solver import Circuit


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


def run(netlist_str: str, fig, params=None):
    params = params or {}
    circ = parse_netlist(netlist_str)
    node_v = circ.solve_nodal()           # {node: voltage}

    true = np.array(list(node_v.values()))
    noisy = true * (1 + np.random.normal(0, 0.005, true.shape))
    rel = np.abs(true - noisy) / np.maximum(np.abs(true), 1e-12)

    fig.clf()
    ax = fig.add_subplot(111)
    ax.bar(range(len(rel)), rel * 100)
    ax.set_title("Relative Node-Voltage Error (%)")
    ax.set_xlabel("Node index")
    ax.set_ylabel("Error %")
    fig.tight_layout()

    return f"Mean relative error: {rel.mean()*100:.3f} %"
