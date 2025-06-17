"""
Visualization
-------------
V1(t) = 10·sin(2πt) (1 Hz) olarak değişirken node-1 gerilimini canlı çizer.
Parametre: yok
"""
import numpy as np
from matplotlib.animation import FuncAnimation
from numerics.linear_solver import parse_netlist, build_mna


def _v1(net, amp):
    lines = []
    for ln in net.strip().splitlines():
        if ln.upper().startswith("V1"):
            p = ln.split(); p[-1] = str(amp); ln = " ".join(p)
        lines.append(ln)
    circ = parse_netlist("\n".join(lines))
    G, b, nodes = build_mna(circ)
    return float(np.linalg.solve(G, b)[nodes.index(1)])


def run(netlist_str: str, fig, params=None):
    xs, ys = [0], [0]
    ax = fig.clf().add_subplot(111)
    line, = ax.plot([], [], lw=2)
    ax.set_xlim(0, 5); ax.set_ylim(-20, 20)
    ax.set_xlabel("t (s)"); ax.set_ylabel("V1 (V)")
    ax.set_title("Live node-1 voltage (10 sin 2πt)")

    def upd(frame):
        t = frame / 20
        amp = 10*np.sin(2*np.pi*t)
        xs.append(t); ys.append(_v1(netlist_str, amp))
        line.set_data(xs, ys)
        return line,

    ani = FuncAnimation(fig, upd, frames=200, interval=50, blit=False)
    fig._ani = ani; fig.tight_layout()
    return "Animating node-1 voltage"
