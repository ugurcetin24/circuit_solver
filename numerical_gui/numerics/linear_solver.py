"""
Linear Solver (Nodal Analysis)
------------------------------
Solves the circuit using MNA and returns node voltages.
"""

import numpy as np
from ..circuit.circuit import parse_netlist, build_mna

def run(netlist_str: str, fig, params=None) -> str:
    """
    Parameters
    ----------
    netlist_str : str
        Raw SPICE-like netlist text.
    fig : matplotlib.figure.Figure
        Figure passed by GUI to allow drawing (not used here).
    params : dict | None
        Reserved for future algorithm parameters.

    Returns
    -------
    str
        Human-readable result table.
    """
    elements = parse_netlist(netlist_str)
    G, I = build_mna(elements)
    try:
        x = np.linalg.solve(G, I)
    except np.linalg.LinAlgError as err:
        return f"[Error] {err}"

    # Pretty output
    out_lines = ["[Nodal Analysis Result]"]
    for idx, v in enumerate(x, start=1):
        out_lines.append(f"Node {idx} Voltage: {v:8.4f} V")
    return "\n".join(out_lines)
