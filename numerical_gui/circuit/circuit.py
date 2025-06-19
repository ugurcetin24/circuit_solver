"""
Circuit helpers – fixed MNA implementation
=========================================
Supports:
  • R  (resistor)  : Rname n1 n2 value   – Ω
  • V  (DC source) : Vname n+ n- value   – V

Extended MNA is used for voltage sources: the admittance matrix is
(n_nodes + m)×(n_nodes + m) where *m* is the number of voltage sources.

Add further element types by creating new _stamp_* helpers and expanding
build_mna accordingly.
"""

from __future__ import annotations

from typing import List, Tuple
import numpy as np

# -----------------------------------------------------------------------------
# Typing helpers
# -----------------------------------------------------------------------------
Elem = Tuple[str, int, int, float]   # (type, node1, node2, value)

# -----------------------------------------------------------------------------
# 1) Netlist parser
# -----------------------------------------------------------------------------

def parse_netlist(net: str) -> List[Elem]:
    """Parse a very small SPICE‑like netlist into a list of tuples."""
    elems: List[Elem] = []
    for line in net.strip().splitlines():
        # remove comments (everything after '*') and extra whitespace
        line = line.split("*", 1)[0].strip()
        if not line:
            continue  # skip blank / comment lines

        name, n1, n2, value = line.split()[:4]
        elems.append((name[0].upper(), int(n1), int(n2), float(value)))
    return elems

# -----------------------------------------------------------------------------
# 2) Stamp helpers
# -----------------------------------------------------------------------------

def _stamp_R(G: np.ndarray, n1: int, n2: int, value: float) -> None:
    """Stamp a resistor into the conductance matrix G."""
    g = 1.0 / value
    if n1:
        G[n1 - 1, n1 - 1] += g
    if n2:
        G[n2 - 1, n2 - 1] += g
    if n1 and n2:
        G[n1 - 1, n2 - 1] -= g
        G[n2 - 1, n1 - 1] -= g


def _stamp_V(G: np.ndarray, I: np.ndarray,
             n_nodes: int, k: int,
             n1: int, n2: int, value: float) -> None:
    """Stamp a (DC) ideal voltage source using the extended MNA scheme."""
    row = n_nodes + k  # position of the extra equation / unknown

    # KCL columns (tie current unknown to the nodes)
    if n1:
        G[n1 - 1, row] = 1
        G[row, n1 - 1] = 1
    if n2:
        G[n2 - 1, row] = -1
        G[row, n2 - 1] = -1

    # KVL right‑hand side
    I[row] = value

# -----------------------------------------------------------------------------
# 3) Build MNA matrices
# -----------------------------------------------------------------------------

def build_mna(elems: List[Elem]):
    """Return (G, I) so that G @ x = I solves for node voltages and source currents."""
    if not elems:
        raise ValueError("Empty element list – nothing to solve")

    # Basic counts
    n_nodes = max(max(n1, n2) for _, n1, n2, _ in elems)  # highest node ID
    v_srcs: List[Elem] = [e for e in elems if e[0] == "V"]
    m = len(v_srcs)                                       # number of voltage sources

    N = n_nodes + m                                       # total matrix size
    G = np.zeros((N, N), dtype=float)
    I = np.zeros(N, dtype=float)

    # --- stamp resistors first ---
    for typ, n1, n2, val in elems:
        if typ == "R":
            _stamp_R(G, n1, n2, val)

    # --- stamp voltage sources ---
    for k, (_, n1, n2, val) in enumerate(v_srcs):
        _stamp_V(G, I, n_nodes, k, n1, n2, val)

    return G, I

# -----------------------------------------------------------------------------
# Re‑exports for convenient import … from ..circuit import parse_netlist, build_mna
# -----------------------------------------------------------------------------
__all__ = ["parse_netlist", "build_mna"]
