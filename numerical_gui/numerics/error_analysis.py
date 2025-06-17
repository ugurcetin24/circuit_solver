"""
Error Analysis module – computes synthetic relative error on node voltages.
"""

import numpy as np
from circuit.circuit_solver import Circuit   # mevcut sınıfı içe aktar


# ---------------------------------------------------------------------------
def parse_netlist(netlist_str: str) -> Circuit:
    """
    Convert raw netlist text into a Circuit object.

    Accepts lines like:
        R1 1 2 100
        V1 1 0 10
        I1 5 0 1
    """
    circuit = Circuit()
    for line in netlist_str.strip().splitlines():
        parts = line.split()
        if len(parts) != 4:
            continue  # basit doğrulama; hatalı satırı atla
        name, node1, node2, value = parts
        node1, node2 = int(node1), int(node2)
        value = float(value)

        if name.upper().startswith("R"):
            circuit.add_resistor(name, node1, node2, value)
        elif name.upper().startswith("V"):
            circuit.add_voltage_source(name, node1, node2, value)
        elif name.upper().startswith("I"):
            circuit.add_current_source(name, node1, node2, value)
    return circuit


# ---------------------------------------------------------------------------
def run(netlist_str: str, fig):
    """
    Called by the GUI when the user clicks “Error Analysis”.

    Parameters
    ----------
    netlist_str : str
        Circuit netlist taken from the input textbox.
    fig : matplotlib.figure.Figure
        Canvas passed by the GUI; can be used for plotting.

    Returns
    -------
    str
        A textual report to display under the buttons.
    """
    # ---- solve original circuit ----
    circuit = parse_netlist(netlist_str)
    node_v = circuit.solve_nodal()            # {'1': 10.0, '2': -90.0, ...}
    true_vals = np.array(list(node_v.values()))

    # ---- add ±0.5 % synthetic noise ----
    noisy_vals = true_vals * (1 + np.random.normal(0, 0.005, true_vals.shape))
    rel_err = np.abs(true_vals - noisy_vals) / np.maximum(np.abs(true_vals), 1e-12)

    # ---- bar plot ----
    fig.clf()                                 # previous contents → clear
    ax = fig.add_subplot(111)
    ax.bar(range(len(rel_err)), rel_err * 100)
    ax.set_title("Relative Node-Voltage Error (%)")
    ax.set_xlabel("Node index")
    ax.set_ylabel("Error %")
    fig.tight_layout()

    # ---- numeric summary back to GUI ----
    return f"Mean relative error: {rel_err.mean() * 100:.3f}%"
