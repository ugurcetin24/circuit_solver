"""
Visualization module – sine wave demo (stable)
=============================================
This module demonstrates that Matplotlib and the GUI integrate
correctly.  It draws a simple sine wave.  Later you can extend the same
file with Bode plots, error curves, optimisation trajectories, etc.

Public API
----------
run(netlist_str: str, fig: matplotlib.figure.Figure | None, params: dict | None = None) -> str
    • *netlist_str*  – The raw netlist text passed by the GUI (currently
      unused, reserved for future plots that depend on circuit data).
    • *fig*          – A Figure object created by the GUI.  If ``None``,
      the function creates its own figure (useful for unit tests).
    • *params*       – Optional dictionary for future extensions.
    Returns a short status string that the GUI prints to its console.
"""
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------
# Public entry
# ---------------------------------------------------------------------

def run(netlist_str: str, fig=None, params: dict | None = None) -> str:
    """Draw a sine wave and return a text status for the GUI console."""
    # -- Data ---------------------------------------------------------
    x = np.linspace(0.0, 2.0 * np.pi, 400)
    y = np.sin(x)

    # -- Figure / Axes ------------------------------------------------
    if fig is None:                      # stand‑alone or CLI test
        fig, ax = plt.subplots()
        created_here = True
    else:                                # GUI passes its own Figure
        fig.clf()                        # clear previous content
        ax = fig.add_subplot(111)
        created_here = False

    ax.plot(x, y, linewidth=2.0)
    ax.set_title("Sine wave demo")
    ax.set_xlabel("radians")
    ax.set_ylabel("sin(x)")
    ax.grid(True, linewidth=0.3, linestyle="--", alpha=0.7)
    fig.tight_layout()

    # Do *not* block the Tk mainloop the GUI is running.  The GUI itself
    # owns the FigureCanvasTkAgg and will show it automatically.  In unit
    # tests we can still call ``plt.show()``.
    if created_here:
        plt.show()

    return "[Visualization] sine wave plotted successfully."
