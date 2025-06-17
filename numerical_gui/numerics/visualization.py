"""
Visualization module – animates node-1 voltage when the source amplitude
varies as  V1(t) = 10 V · sin(2π t)   (f = 1 Hz).
"""

import numpy as np
from matplotlib.animation import FuncAnimation
from circuit.circuit_solver import Circuit
from numerics.linear_solver import parse_netlist, build_mna   # reuse helpers


# --------------------------------------------------------------------------- #
def _solve_voltage(node: int, amplitude: float, base_netlist: str) -> float:
    """
    Return voltage at <node> when the V1 source amplitude is <amplitude> volts.
    """
    new_lines = []
    for ln in base_netlist.strip().splitlines():
        if ln.upper().startswith("V1"):
            parts = ln.split()
            parts[-1] = str(amplitude)          # replace value
            ln = " ".join(parts)
        new_lines.append(ln)
    net = "\n".join(new_lines)

    circ = parse_netlist(net)
    G, i_vec, nodes = build_mna(circ)
    v = np.linalg.solve(G, i_vec)

    try:
        idx = nodes.index(node)
        return float(v[idx])
    except ValueError:
        return np.nan


# --------------------------------------------------------------------------- #
def run(netlist_str: str, fig):
    """
    Called by the GUI when the user clicks 'Visualization'.
    Produces a live line-plot animation on the supplied Figure.
    """
    # -- initial plot boilerplate --------------------------------------------
    fig.clf()
    ax = fig.add_subplot(111)
    ax.set_title("Node-1 Voltage vs. Time (V1 amplitude = 10 sin 2πt)")
    ax.set_xlabel("Time  [s]")
    ax.set_ylabel("Voltage  [V]")
    line, = ax.plot([], [], lw=2)
    ax.set_ylim(-20, 20)
    ax.set_xlim(0, 5)

    xs, ys = [0], [0]            # first point (0 s, 0 V)

    # -- animation update ----------------------------------------------------
    def update(frame):
        t = frame / 20           # 20 fps ⇒ Δt = 0.05 s
        amp = 10 * np.sin(2 * np.pi * t)          # 1 Hz sine amplitude
        v_node1 = _solve_voltage(1, amp, netlist_str)

        xs.append(t)
        ys.append(v_node1)
        line.set_data(xs, ys)

        ax.set_xlim(0, max(5, t + 0.5))            # extend x-axis if needed
        line.figure.canvas.draw_idle()             # << force canvas refresh
        return line,

    # -- create FuncAnimation & keep reference --------------------------------
    ani = FuncAnimation(fig, update, frames=200, interval=50, blit=False)
    fig.tight_layout()
    fig._animation = ani        # prevent garbage-collection of animation

    # initial draw
    fig.canvas.draw_idle()

    return "Animating node-1 voltage (1 Hz sine on V1)"
