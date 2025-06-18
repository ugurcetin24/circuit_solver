"""
Root Finding
------------
Adjust resistor R1 so that the voltage at a given node reaches a
target value. Uses the bisection method.

Parameters (dict, optional)
---------------------------
target_node   : int   -> Node index (1-based) whose voltage is regulated
target_voltage: float -> Desired voltage in volts            (default 5 V)
R1_min        : float -> Lower bound for R1 (ohms)           (default 10 Ω)
R1_max        : float -> Upper bound for R1 (ohms)           (default 1e5 Ω)
tol           : float -> Voltage tolerance                   (default 1 mV)

Returns
-------
str : Text report (root iteration table & final R1)

Author : Ugur C. (refactor-clean branch)
"""

from __future__ import annotations

from typing import Callable

import numpy as np
import matplotlib.pyplot as plt
from .linear_solver import parse_netlist, build_mna   # sibling import


def _patch_R1(netlist: str, new_value: float) -> str:
    """Return a new netlist where the last token of the R1 line is new_value."""
    lines, patched = [], False
    for ln in netlist.strip().splitlines():
        if not patched and ln.strip().upper().startswith("R1"):
            tokens = ln.split()
            tokens[-1] = f"{new_value:.6g}"
            ln = " ".join(tokens)
            patched = True
        lines.append(ln)
    if not patched:
        raise ValueError("Netlist must contain an element named 'R1'.")
    return "\n".join(lines)


def _voltage_fn(netlist: str, node: int) -> Callable[[float], float]:
    """Return f(R1) = V_node (voltage at target node) for varying R1."""
    def _f(R1_val: float) -> float:
        G, I = build_mna(parse_netlist(_patch_R1(netlist, R1_val)))
        V = np.linalg.solve(G, I)
        return float(V[node - 1])      # node index is 1-based
    return _f


def run(netlist_str: str, fig: plt.Figure, params: dict | None = None) -> str:
    # --------------------------- parameters -----------------------------
    p               = params or {}
    target_node     = int(p.get("target_node", 1))
    V_target        = float(p.get("target_voltage", 5.0))
    R_lo, R_hi      = float(p.get("R1_min", 10.0)), float(p.get("R1_max", 1e5))
    tol             = float(p.get("tol", 1e-3))        # 1 mV default

    fV              = _voltage_fn(netlist_str, target_node)

    # ------------------------- initial check ---------------------------
    V_lo, V_hi = fV(R_lo), fV(R_hi)
    if (V_lo - V_target) * (V_hi - V_target) > 0:
        return ("[RootFinding] Target voltage not bracketed.\n"
                f"V({R_lo:.1f} Ω)={V_lo:.3f} V, "
                f"V({R_hi:.1f} Ω)={V_hi:.3f} V")

    # ---------------------- bisection iterations -----------------------
    iterations, table = 0, []
    while True:
        R_mid = 0.5 * (R_lo + R_hi)
        V_mid = fV(R_mid)
        table.append((iterations, R_mid, V_mid))
        if abs(V_mid - V_target) < tol:
            break
        if (V_lo - V_target) * (V_mid - V_target) < 0:
            R_hi, V_hi = R_mid, V_mid
        else:
            R_lo, V_lo = R_mid, V_mid
        iterations += 1
        if iterations > 60:
            return "[RootFinding] Failed to converge within 60 iterations."

    # -------------------------- report text ----------------------------
    report = [
        "[Root Finding – Bisection]",
        f"Target Node            : {target_node}",
        f"Target Voltage (Vt)    : {V_target:.3f} V",
        f"Tolerance              : ±{tol:.3g} V",
        "",
        f"{'Iter':>4} | {'R1 (Ω)':>10} | {'V_node (V)':>11}",
        "-" * 32,
    ]
    report += [f"{i:>4d} | {r:>10.3f} | {v:>11.6f}" for i, r, v in table]
    report.append("-" * 32)
    report.append(f"Converged R1 ≈ {R_mid:.3f} Ω  →  V ≈ {V_mid:.3f} V")

    # --------------------------- plot ----------------------------------
    fig.clf()
    ax = fig.add_subplot(111)
    Rs = np.logspace(np.log10(R_lo * 0.1), np.log10(R_hi * 10), 100)
    Vs = [fV(r) for r in Rs]
    ax.semilogx(Rs, Vs, label=f"V_node {target_node}")
    ax.axhline(V_target, ls="--", color="k", label="Target")
    ax.axvline(R_mid, ls=":", color="tab:red", label="R1*")
    ax.set_xlabel("R1 (Ω)")
    ax.set_ylabel(f"V_node{target_node} (V)")
    ax.set_title("Root-Finding: Voltage vs R1")
    ax.legend()
    ax.grid(True, which="both", ls="--", alpha=0.4)
    fig.tight_layout()

    return "\n".join(report)
