"""
ODE Solver module – simulates the step response of a first-order RC circuit:

    Vin --- R ---+--- C --- GND
                 |
                v(t)

ODE: dv/dt = (Vin - v) / (R C)

Parameters below (R, C, Vin) can be tweaked or later read from GUI.
"""

import numpy as np
from scipy.integrate import solve_ivp


# --------------------------------------------------------------------------- #
def run(netlist_str: str, fig):
    """
    GUI entry – integrates dv/dt for 0 ≤ t ≤ 5·τ and plots v(t).
    """
    # --- fixed demo parameters ----------------------------------------------
    R, C = 1e3, 1e-6            # 1 kΩ, 1 µF  →  τ = 1 ms
    Vin  = 10.0                 # step input amplitude (V)
    tau  = R * C                # time constant

    # --- ODE definition ------------------------------------------------------
    def rc_ode(t, v):
        return (Vin - v) / (R * C)

    t_final = 5 * tau           # simulate 0 → 5τ  (≈ 99.3% charging)
    sol = solve_ivp(rc_ode, (0, t_final), [0.0],
                    max_step=tau / 20,         # fine resolution
                    dense_output=True)

    t = sol.t
    v = sol.y[0]

    # --- plotting ------------------------------------------------------------
    fig.clf()
    ax = fig.add_subplot(111)
    ax.plot(t * 1000, v)        # x-axis in ms
    ax.set_xlabel("Time  [ms]")
    ax.set_ylabel("Capacitor voltage  v(t)  [V]")
    ax.set_title("RC Step Response  (τ ≈ {:.2f} ms)".format(tau * 1000))
    fig.tight_layout()

    return "RC step solved: τ ≈ {:.2f} ms".format(tau * 1000)
