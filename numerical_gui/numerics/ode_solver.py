"""
ODE Solver (RC Step Response)
-----------------------------
Treat the circuit as an RC load (R1 // C) fed by V1 step.
Solve dV/dt = (Vs – V)/RC with SciPy’s solve_ivp.

Parameters
----------
R1  : float  ohms      (default 1 kΩ)
C   : float  farads    (default 1 µF)
Vs  : float  volts     (default 10 V step)
t_end : float seconds  (default 0.05 s)

Returns
-------
str : Rise-time, τ = R C ve en büyük % aşım.
"""
from __future__ import annotations
import numpy as np, matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

def _ode(t, v, vs, tau):            # dV/dt
    return (vs - v)/tau

def run(net, fig, params=None):
    p      = params or {}
    R      = float(p.get("R1", 1_000.0))
    C      = float(p.get("C", 1e-6))
    Vs     = float(p.get("Vs", 10.0))
    t_end  = float(p.get("t_end", 0.05))
    tau    = R * C

    sol = solve_ivp(_ode, [0, t_end], [0], args=(Vs, tau),
                    t_eval=np.linspace(0, t_end, 400))
    t, v = sol.t, sol.y[0]
    overshoot = (v.max() - Vs) / Vs * 100.0

    # Plot
    fig.clf()
    ax = fig.add_subplot(111)
    ax.plot(t, v, label="V(t)")
    ax.axhline(Vs, ls="--", color="k", label="Vs")
    ax.set_xlabel("Time (s)"); ax.set_ylabel("Voltage (V)")
    ax.set_title("RC Step Response")
    ax.grid(ls="--", alpha=.3); ax.legend()
    fig.tight_layout()

    return (f"[ODE Solver]\nτ = {tau:.3e} s\n"
            f"Rise-time (10-90 %) ≈ {0.22*tau:.3e} s\n"
            f"Overshoot ≈ {overshoot:.2f} %")
