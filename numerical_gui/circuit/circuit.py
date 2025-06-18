"""
Circuit core utilities.
Parse a simple SPICE-like netlist and build the MNA matrix.

Author: refactor-clean branch
"""
import re, numpy as np
NODE_RE = re.compile(r"^([RVI])(\w+)\s+(\d+)\s+(\d+)\s+([-\d\.]+)", re.I)

def parse_netlist(net: str):
    elems = []
    for ln in net.strip().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("*"):
            continue
        m = NODE_RE.match(ln)
        if not m:
            raise ValueError(f"Bad line: {ln}")
        t, name, n1, n2, val = m.groups()
        elems.append((t.upper(), name, int(n1), int(n2), float(val)))
    return elems

def build_mna(elems):
    max_node = 0; vsrc = 0
    for t, _, n1, n2, _ in elems:
        max_node = max(max_node, n1, n2)
        if t == "V": vsrc += 1
    n, m = max_node, vsrc
    size = n + m
    G = np.zeros((size, size)); I = np.zeros(size)
    k = 0
    for t, _, n1, n2, val in elems:
        def stamp(a, b, g):
            if a: G[a-1,a-1] += g
            if b: G[b-1,b-1] += g
            if a and b:
                G[a-1,b-1] -= g
                G[b-1,a-1] -= g
        if t == "R":
            stamp(n1, n2, 1/val)
        elif t == "I":
            if n1: I[n1-1] -= val
            if n2: I[n2-1] += val
        elif t == "V":
            row = n + k
            if n1:
                G[row, n1-1] = G[n1-1, row] = 1
            if n2:
                G[row, n2-1] = G[n2-1, row] = -1
            I[row] = val
            k += 1
    return G, I
