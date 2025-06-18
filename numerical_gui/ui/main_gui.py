"""
Super-Modern Circuit Solver GUI (v1.1)
=====================================
* Starts **maximised** on launch and prevents shrinking below that size.
* Left pane: Netlist editor + 12 action buttons
* Right pane: Response console, matplotlib figure, and status bar

Author : Ugur C.  – refactor-clean branch
"""

from __future__ import annotations

import importlib
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# ---------------------------------------------------------------------------
# Dynamic discovery of numerics modules
# ---------------------------------------------------------------------------
from ..numerics import __all__ as _NUMERIC_NAMES  # populated in numerics/__init__.py

_NUMERIC_MODULES = {
    name: importlib.import_module(f"..numerics.{name}", package=__package__)
    for name in _NUMERIC_NAMES
}

_LABELS = {
    "linear_solver": "Linear Solver",
    "error_analysis": "Error Analysis",
    "root_finding": "Root Finding",
    "diff_int": "Diff / Int",
    "lu_decomp": "LU Decomp",
    "ode_solver": "ODE Solver",
    "performance": "Performance",
    "comparison": "Comparison",
    "optimization": "Optimisation",
    "interpolation": "Interpolation",
}


class CircuitSolverGUI(ttk.Frame):
    """Main application frame."""

    BTN_COLS = 4  # buttons per row

    def __init__(self, master: tk.Tk):
        super().__init__(master, padding=10)
        self.pack(fill="both", expand=True)

        # ----------------------- THEME HANDLING ---------------------------
        style = ttk.Style(master)
        if "azure-dark" in style.theme_names():
            style.theme_use("azure-dark")
        elif "azure" in style.theme_names():
            style.theme_use("azure")
        elif "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Accent.TButton", font=(None, 10, "bold"), padding=6)

        # ------------------ WINDOW GEOMETRY & LOCK -----------------------
        master.title("Numerical Methods – Circuit Solver (Modern UI)")
        master.geometry("1200x700")            # fallback size before maximise
        master.update_idletasks()               # ensure geometry applied
        try:
            master.state("zoomed")             # Windows ➜ maximise
        except tk.TclError:
            master.attributes("-zoomed", True)  # Linux / Tk 8.6
        # After zoom, lock current size as minimum so user cannot shrink
        master.update_idletasks()
        master.minsize(master.winfo_width(), master.winfo_height())

        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)

        # ----------------------------- LAYOUT ----------------------------
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True)

        # LEFT PANE – Netlist + Buttons
        left = ttk.Frame(paned, padding=(0, 0, 8, 0))
        paned.add(left, weight=1)
        left.rowconfigure(1, weight=1)

        ttk.Label(left, text="Netlist", font=(None, 10, "bold")).grid(row=0, column=0, sticky="w")
        self.netlist = scrolledtext.ScrolledText(left, height=15, wrap="none")
        self.netlist.grid(row=1, column=0, sticky="nsew")

        btn_frame = ttk.Frame(left)
        btn_frame.grid(row=2, column=0, pady=(10, 0), sticky="ew")
        for c in range(self.BTN_COLS):
            btn_frame.columnconfigure(c, weight=1)

        # Auto-generate module buttons
        for idx, (name, mod) in enumerate(_NUMERIC_MODULES.items()):
            r, c = divmod(idx, self.BTN_COLS)
            label = _LABELS.get(name, name.replace("_", " ").title())
            ttk.Button(
                btn_frame,
                text=label,
                style="Accent.TButton",
                command=lambda m=mod, n=name: self._run_module(m, n),
            ).grid(row=r, column=c, padx=2, pady=2, sticky="ew")

        # RIGHT PANE – Console + Figure + StatusBar
        right = ttk.Frame(paned, padding=(8, 0, 0, 0))
        paned.add(right, weight=1)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        ttk.Label(right, text="Response", font=(None, 10, "bold")).grid(row=0, column=0, sticky="w")
        self.console = scrolledtext.ScrolledText(right, state="disabled", wrap="word")
        self.console.grid(row=1, column=0, sticky="nsew")

        self.fig = Figure(figsize=(5, 3))
        self.ax = self.fig.add_subplot(111); self.ax.axis("off")
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=2, column=0, pady=(10, 0), sticky="nsew")
        right.rowconfigure(2, weight=2)

        self.status = ttk.Label(right, text="Ready", anchor="w")
        self.status.grid(row=3, column=0, sticky="ew", pady=(6, 0))

    # ------------------------------------------------------------------
    # Module execution
    # ------------------------------------------------------------------
    def _run_module(self, module, mod_name: str):
        net = self.netlist.get("1.0", tk.END).strip()
        if not net:
            messagebox.showwarning("Empty netlist", "Please enter a circuit netlist first.")
            return

        start = time.perf_counter()
        self._clear_outputs()
        self.status.config(text=f"Running {mod_name} …")
        self.update_idletasks()

        try:
            result = module.run(net, self.fig)
        except Exception as exc:  # noqa: BLE001
            result = f"[Exception in {mod_name}]\n{type(exc).__name__}: {exc}"

        elapsed = time.perf_counter() - start
        self._write_console(result)
        self.canvas.draw_idle()
        self.status.config(text=f"{mod_name} finished in {elapsed:.2f} s")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _clear_outputs(self):
        self.ax.clear(); self.ax.axis("off")
        self.console.configure(state="normal"); self.console.delete("1.0", tk.END)
        self.console.configure(state="disabled")

    def _write_console(self, txt: str):
        self.console.configure(state="normal")
        self.console.insert(tk.END, txt)
        self.console.configure(state="disabled")
        self.console.see(tk.END)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    CircuitSolverGUI(root)
    root.mainloop()
