"""
LU Decomposition
================
Factor the circuit’s conductance matrix G such that

      P · G = L · U

where P is a row-permutation matrix, L is unit-lower-triangular,
and U is upper-triangular.  Visualise |L| and |U| as heat maps.

Parameters (dict, optional)
---------------------------
pivoting : str  -> 'partial' (default) or 'none'
             Partial pivoting uses `scipy.linalg.lu`, otherwise numpy.triu/ tril.

Returns
-------
str :   Text report containing matrix shapes, permutation parity and det(G).

Author : Ugur C. (refactor-clean branch)
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import lu, det, LinAlgError

# Re-export helpers from sibling module
from .linear_solver import parse_netlist, build_mna


def run(netlist_str: str, fig: plt.Figure, params: dict | None = None) -> str:
    # --------------------------- Parameters ---------------------------
    p           = params or {}
    pivoting    = str(p.get("pivoting", "partial")).lower()
    use_pivot   = (pivoting != "none")

    # --------------------------- Build G ------------------------------
    G, I = build_mna(parse_netlist(netlist_str))
    n    = G.shape[0]

    # ------------------------- Decomposition --------------------------
    try:
        if use_pivot:
            P, L, U = lu(G)              # SciPy: partial pivoting
        else:
            # crude LU without pivoting (for teaching)
            P = np.eye(n)
            L = np.tril(G, k=-1) + np.eye(n)
            U = np.triu(G)
    except LinAlgError as err:
        return f"[LU] decomposition failed: {err}"

    # ---------------------- Plot heat maps ----------------------------
    fig.clf()
    ax1 = fig.add_subplot(1, 2, 1)
    im1 = ax1.imshow(np.abs(L), origin="upper", cmap="viridis", aspect="auto")
    ax1.set_title("|L|")

    ax2 = fig.add_subplot(1, 2, 2)
    im2 = ax2.imshow(np.abs(U), origin="upper", cmap="viridis", aspect="auto")
    ax2.set_title("|U|")

    for ax in (ax1, ax2):
        ax.set_xticks([]); ax.set_yticks([])

    fig.colorbar(im2, ax=[ax1, ax2], fraction=0.04, location="right")
    fig.suptitle("LU Decomposition Heat-Maps")
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    # -------------------------- Report -------------------------------
    parity      = int(np.round(det(P)))
    det_G       = float(det(G))
    nnz_L       = int(np.count_nonzero(L))
    nnz_U       = int(np.count_nonzero(U))

    report = [
        "[LU Decomposition]",
        f"G size            : {n} × {n}",
        f"Pivoting mode     : {'partial' if use_pivot else 'none'}",
        f"Permutation parity: {parity:+d}",
        f"det(G)            : {det_G:.3e}",
        f"Non-zeros in L    : {nnz_L}",
        f"Non-zeros in U    : {nnz_U}",
    ]
    return "\n".join(report)
