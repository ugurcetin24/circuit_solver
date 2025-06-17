"""
LU Decomposition
----------------
G matrisini P·L·U olarak ayırır, |L| ve |U| ısı haritasını yan yana gösterir.
Parametre: yok
"""
import numpy as np
from scipy.linalg import lu
from numerics.linear_solver import parse_netlist, build_mna


def run(netlist_str: str, fig, params=None):
    params = params or {}
    circ = parse_netlist(netlist_str)
    G, b, nodes = build_mna(circ)

    P, L, U = lu(G)
    y = np.linalg.solve(L, P.T @ b)
    x = np.linalg.solve(U, y)

    fig.clf()
    ax1 = fig.add_subplot(1, 2, 1)
    im1 = ax1.imshow(np.abs(L), origin="upper", aspect="auto")
    ax1.set_title("|L|"); fig.colorbar(im1, ax=ax1, fraction=0.046)
    ax2 = fig.add_subplot(1, 2, 2)
    im2 = ax2.imshow(np.abs(U), origin="upper", aspect="auto")
    ax2.set_title("|U|"); fig.colorbar(im2, ax=ax2, fraction=0.046)
    fig.tight_layout()

    txt = ", ".join([f"{x[i]:.3f} V" for i in range(len(nodes))])
    return f"Node voltages (LU): {txt}"
