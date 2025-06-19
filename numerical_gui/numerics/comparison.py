"""
comparison.py – Direct & LU benchmark (ms)
==========================================
Basit ve sağlam: G · x = I sistemini yalnızca
  1. Direct dense   → numpy.linalg.solve
  2. LU faktörizasyon→ scipy.linalg.lu_factor / lu_solve   (SciPy varsa)
ile çözer, süreleri ve ∞-norm artıklarını raporlar.

CG çıkarıldı → hiçbir sürüm uyumsuzluğu / yakınsamama hatası kalmaz.
"""

from time import perf_counter
import numpy as np
import matplotlib.pyplot as plt

# — SciPy opsiyonel —
try:
    from scipy.linalg import lu_factor, lu_solve
except Exception:
    lu_factor = lu_solve = None

from ..circuit import parse_netlist, build_mna

# ────────── ana fonksiyon ───────────────────────────────────────
def run(netlist_str: str,
        fig: plt.Figure | None = None,
        params: dict | None = None) -> str:
    G, I = build_mna(parse_netlist(netlist_str))

    labels, t_ms, resid = [], [], []

    # Direct -----------------------------------------------------
    t0 = perf_counter()
    x = np.linalg.solve(G, I)
    t_ms.append((perf_counter() - t0) * 1000)          # ms
    resid.append(np.linalg.norm(G @ x - I, np.inf))
    labels.append("Direct")

    # LU ---------------------------------------------------------
    if lu_factor and lu_solve:
        t0 = perf_counter()
        x = lu_solve(lu_factor(G), I)
        t_ms.append((perf_counter() - t0) * 1000)
        resid.append(np.linalg.norm(G @ x - I, np.inf))
        labels.append("LU")

    # — Konsol raporu —
    for l, t, r in zip(labels, t_ms, resid):
        print(f"{l:<6}: {t:8.3f} ms | residual = {r:.2e}")

    # — Grafik —
    if fig is None:
        fig, ax = plt.subplots()
    else:
        fig.clf(); ax = fig.add_subplot(111)

    bars = ax.bar(labels, t_ms, color="#1f77b4")
    ax.set_ylabel("Time (ms)")
    ax.set_title("Solver Runtime Comparison")
    ax.set_ylim(0, max(t_ms) * 1.2 if t_ms else 1)

    for rect, t in zip(bars, t_ms):
        ax.annotate(f"{t:.2f}",
                    xy=(rect.get_x() + rect.get_width() / 2, rect.get_height()),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8)

    fig.tight_layout()
    return "[Comparison] OK"
