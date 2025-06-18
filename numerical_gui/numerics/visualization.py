"""
Visualization – Live Sine Wave Demo
-----------------------------------
Animate 10 sin(2π 50 t) for 0.1 s as a proof-of-concept.

No parameters.

Returns
-------
str : “Live plot finished.”
"""
from __future__ import annotations
import numpy as np, matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def run(net, fig, params=None):
    t = np.linspace(0, 0.1, 1000); v = 10*np.sin(2*np.pi*50*t)

    fig.clf(); ax = fig.add_subplot(111)
    ln, = ax.plot([], [], lw=2); ax.set_xlim(0,0.1); ax.set_ylim(-11,11)
    ax.set_xlabel("Time (s)"); ax.set_ylabel("Voltage (V)")
    ax.set_title("Live Sine Visualization")

    def init(): ln.set_data([], []); return ln,
    def update(i):
        ln.set_data(t[:i], v[:i]); return ln,

    ani = FuncAnimation(fig, update, frames=len(t), init_func=init,
                        interval=20, blit=True)
    fig.tight_layout()
    return "[Visualization] Live plot finished."
