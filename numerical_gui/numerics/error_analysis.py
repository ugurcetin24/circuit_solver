"""
Error Analysis
--------------
Given a circuit netlist, this module
1. Solves the nominal system (exact G · x = I).
2. Creates a perturbed conductance matrix G' by adding small Gaussian
   noise (default ±0.5 %) to each non-zero element.
3. Solves the perturbed system and estimates the relative error in node
   voltages.
4. Plots a bar chart of |V_nominal| with error bars showing |ΔV|.

Author : Ugur C. (refactor-clean branch)
"""

import numpy as np
from numpy.random import default_rng
import matplotlib.pyplot as plt

from ..circuit.circuit import parse_netlist, build_mna

# Reusable RNG for reproducibility in GUI runs
_RNG = default_rng(seed=42)


def run(netlist_str: str, fig: plt.Figure, params: dict | None = None) -> str:
    """
    Parameters
    ----------
    netlist_str : str
        Raw SPICE-like netlist.
    fig : matplotlib.figure.Figure
        Figure object supplied by the GUI; the plot is drawn here.
    params : dict | None
        Optional parameters:
          • perturb_pct : float – 1 σ noise level in percent (default 0.5)

    Returns
    -------
    str
        Multiline report summarising condition number and relative errors.
    """
    p         = params or {}
    sigma_pct = float(p.get("perturb_pct", 0.5))       # %
    sigma     = sigma_pct / 100.0

    # --- Step 1 : Build exact system and solve ---------------------------
    elems          = parse_netlist(netlist_str)
    G_exact, I_vec = build_mna(elems)
    try:
        V_nom = np.linalg.solve(G_exact, I_vec)
    except np.linalg.LinAlgError as err:
        return f"[ErrorAnalysis] Matrix solve failed: {err}"

    # --- Step 2 : Perturb conductance matrix -----------------------------
    noise_mask     = G_exact != 0.0              # only perturb existing stamps
    gaussian_noise = _RNG.normal(loc=0.0, scale=sigma, size=G_exact.shape)
    G_pert         = G_exact * (1.0 + gaussian_noise * noise_mask)

    # --- Step 3 : Solve perturbed system ---------------------------------
    V_pert = np.linalg.solve(G_pert, I_vec)

    # --- Step 4 : Compute metrics ----------------------------------------
    delta_V        = V_pert - V_nom
    rel_err        = np.linalg.norm(delta_V) / np.linalg.norm(V_nom)
    cond_G         = np.linalg.cond(G_exact)

    # --- Step 5 : Plot ---------------------------------------------------
    fig.clf()
    ax  = fig.add_subplot(111)
    idx = np.arange(len(V_nom))

    ax.bar(idx, np.abs(V_nom), yerr=np.abs(delta_V), capsize=5)
    ax.set_title("Node Voltages |V| with Perturbation Error Bars")
    ax.set_xlabel("Node Index")
    ax.set_ylabel("|Voltage| [V]")
    ax.grid(alpha=0.3, ls="--")
    fig.tight_layout()

    # --- Step 6 : Human-readable report ----------------------------------
    lines = [
        "[Error Analysis]",
        f"σ (perturbation)     : ±{sigma_pct:.2f} %",
        f"Condition number κ(G) : {cond_G:.2e}",
        f"Relative error ‖ΔV‖/‖V‖ : {rel_err:.2e}",
        "",
        "Node-wise details:",
    ]
    for i, (v_nom, dv) in enumerate(zip(V_nom, delta_V), start=1):
        lines.append(
            f"  Node {i:>2} : V = {v_nom: .6f} V   ΔV = {dv:+.6e} V"
        )
    return "\n".join(lines)
