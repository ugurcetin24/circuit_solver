"""
LU Decomposition module – factors the MNA matrix G into P·L·U,
solves for node voltages, and visualises |L| and |U| side-by-side.
"""

import numpy as np
from scipy.linalg import lu
from circuit.circuit_solver import Circuit
from numerics.linear_solver import parse_netlist, build_mna  # yeniden kullanıyoruz

# ----------------------------------------------------------------------------- #
def run(netlist_str: str, fig):
    """Triggered by the 'LU Decomposition' button in the GUI."""
    circuit = parse_netlist(netlist_str)
    G, i_vec, nodes = build_mna(circuit)

    # ----------- LU factorisation -----------
    P, L, U = lu(G)                  # SciPy returns permutation as P

    # Solve:  P·L·U·x = b   →   L·U·x = Pᵀ·b
    y = np.linalg.solve(L, P.T @ i_vec)
    x = np.linalg.solve(U, y)

    # ----------- plot |L| and |U| -----------
    fig.clf()
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)

    im1 = ax1.imshow(np.abs(L), origin="upper", aspect="auto")
    ax1.set_title("|L| Lower-Triangular")
    fig.colorbar(im1, ax=ax1, fraction=0.046)

    im2 = ax2.imshow(np.abs(U), origin="upper", aspect="auto")
    ax2.set_title("|U| Upper-Triangular")
    fig.colorbar(im2, ax=ax2, fraction=0.046)

    for ax in (ax1, ax2):
        ax.set_xlabel("Col")
        ax.set_ylabel("Row")

    fig.tight_layout()

    # ----------- textual output -------------
    txt = ", ".join([f"V{n}={x[i]:.3f} V" for i, n in enumerate(nodes)])
    return f"Node voltages (LU): {txt}"
